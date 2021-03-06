import click
import pandas as pd


class Parser:

    def __init__(self):
        self.edges = set()

        # maps unique nodes to ints
        self.int_map = dict()
        self.curr = 0

        # init count maps - used for determining weights of edges

        # maps edges to occurrence count
        self.edge_count_map = dict()

        # maps nodes to occurrence count
        self.node_count_map = dict()

    def _map_node(self, node):
        # maps unique (val, attr) pairs to ints
        if node not in self.int_map:
            self.int_map[node] = self.curr
            self.curr += 1

    def _count_edge(self, edge):
        # counts appearances of edge - used for weighting
        if edge not in self.edges:
            self.edge_count_map[edge] = 1
        else:
            self.edge_count_map[edge] += 1

    def _count_node(self, node):
        # counts appearance of node on left side of edge
        int_node = self.int_map[node]
        if int_node not in self.node_count_map:
            self.node_count_map[int_node] = 1
        else:
            self.node_count_map[int_node] += 1

    def add_edge(self, node_1, node_2):
        # takes two (val, attr) tuples and adds an edge between them
        self._map_node(node_1)
        self._map_node(node_2)

        self._count_node(node_1)

        edge = (self.int_map[node_1], self.int_map[node_2])
        self._count_edge(edge)

        self.edges.add(edge)

    def print_edges(self, out, weighted):
        for edge in sorted(self.edges):
            str_edge = str(edge[0]) + ' ' + str(edge[1])

            if weighted == 'count':
                str_edge += ' ' + str(self.edge_count_map[edge])
            elif weighted == 'proportion':
                prop = float(self.edge_count_map[edge]) / self.node_count_map[edge[0]]
                str_edge += ' ' + str(prop)

            if out is None:
                print str_edge
            else:
                out.write(str_edge + '\n')


class BCNFSplitter:

    def __init__(self, data_file, fd_file):
        self.data = pd.read_csv(data_file)

        # dict mapping list of LHS to string RHS
        self.fds = list()

        fdf = open(fd_file, 'r')

        # each fd maps list of cols to one col
        for line in fdf:
            split_fd = line.split('-')
            left = tuple(split_fd[0].split(','))
            right = split_fd[1].rstrip('\n')
            self.fds.append([left, right])

    def split_data(self):
        # returns normalized list of list of column indices
        # ex: [[1, 3], [1,2,4]]

        # start with all cols
        tables = [range(self.data.shape[1])]
        i = 0
        while i < len(tables):
            table = self.data.iloc[:, tables[i]]
            viol_fd = self._violated_fd(table)
            if viol_fd != -1:
                a = self.data.columns.get_loc(self.fds[viol_fd][1])
                x = [self.data.columns.get_loc(col)
                     for col in self.fds[viol_fd][0]]

                # XA
                x.append(a)
                tables.append(x)

                # R - A
                table = tables.pop(i)
                table.remove(a)
                tables.append(table)

                i -= 1
            i += 1

        return tables

    def _violated_fd(self, table):
        # returns index of violated fd or -1 if none
        for fd in self.fds:
            left = fd[0]
            right = fd[1]
            if all([s in table.columns for s in left]) \
                    and right in table.columns \
                    and not table.shape[1] == len(left) + 1:
                return self.fds.index(fd)

        return -1


@click.command()
@click.option('--fdfile', '-f', default=None,
              help='Functional Dependency File Name')
@click.option('--outfile', '-o', default=None, help='Output File Name')
@click.option('--weighting', '-w', type=click.Choice(['count', 'proportion']),
              help = "Type of Weighting")
@click.argument('filename')
def csv_to_graph(filename, fdfile, outfile, weighting):

    parser = Parser()

    f = open(filename, 'r')

    colnames = f.readline().split(',')

    if fdfile is not None:
        splitter = BCNFSplitter(filename, fdfile)
        tables = splitter.split_data()
    else:
        tables = [range(len(colnames))]

    for line in f:
        split = line.split(',')
        for table in tables:
            for i in range(len(table) - 1):
                col_1 = table[i]
                col_2 = table[i+1]
                node_1 = (split[col_1], col_1)
                node_2 = (split[col_2], col_2)
                parser.add_edge(node_1, node_2)

            # add edges for last col to first col
            col_1 = table[0]
            col_2 = table[len(table) - 1]
            node_1 = (split[col_1], col_1)
            node_2 = (split[col_2], col_2)
            parser.add_edge(node_1, node_2)

    if outfile is not None:
        out = open(outfile, 'w')
    else:
        out = None

    parser.print_edges(out, weighting)


if __name__ == '__main__':
    csv_to_graph()
