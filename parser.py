import click
import sys


class Parser:

    def __init__(self):
        self.edges = set()
        self.int_map = dict()
        self.curr = 0

    def _map_node(self, node):
        if node not in self.int_map:
            self.int_map[node] = self.curr
            self.curr += 1

    def add_edge(self, val_1, index_1, val_2, index_2):
        node_1 = (val_1, index_1)
        node_2 = (val_2, index_2)

        self._map_node(node_1)
        self._map_node(node_2)

        self.edges.add((self.int_map[node_1], self.int_map[node_2]))

    def print_edges(self):
        for edge in sorted(self.edges):
            print str(edge[0]) + ' ' + str(edge[1])


@click.command()
@click.option('--header', default=True, help='bool: Header for Data File')
@click.option('--fdfile', default=None, help='Functional Dependency File Name')
@click.option('--outfile', default=None, help='Output File Name')
@click.argument('filename')
def csv_to_graph(filename, header, fdfile, outfile):
    if fdfile is not None:
        print "Not supported yet"

    if outfile is not None:
        sys.stdout = open(outfile, 'w')

    parser = Parser()

    f = open(filename, 'r')

    if header is True:
        f.readline()

    for line in f:
        split = line.split(',')
        for i in range(len(split)-1):
            parser.add_edge(split[i], i, split[i+1], i+1)
        last_col = len(split) - 1
        parser.add_edge(split[last_col], last_col, split[0], 0)

    parser.print_edges()


if __name__ == '__main__':
    csv_to_graph()
