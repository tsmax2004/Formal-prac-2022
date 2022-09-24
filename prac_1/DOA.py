alphabet = {chr(i) for i in range(ord('a'), ord('z') + 1)} | \
           {chr(i) for i in range(ord('A'), ord('Z') + 1)} | \
           {str(i) for i in range(0, 10)} | {''}


class DOA:
    def __init__(self):
        self.nodes = set()
        self.adj_lists = dict()
        self.start = None
        self.acceptance = set()

        self.last_unique_node = None

    def get_unique_node(self):
        if not self.last_unique_node:
            self.last_unique_node = 0
        self.last_unique_node += 1
        return '$' + str(self.last_unique_node)

    def add_node(self, node):
        node = str(node)
        if node in self.nodes:
            return
        self.nodes.add(node)
        self.adj_lists[node] = {symbol: set() for symbol in alphabet}

    def make_start(self, node):
        node = str(node)
        if node not in self.nodes:
            raise ValueError
        self.start = node

    def make_acceptance(self, node):
        node = str(node)
        if node not in self.nodes:
            raise ValueError
        self.acceptance.add(node)

    def add_edge(self, out, to, word):
        if out not in self.nodes:
            self.add_node(out)
        if to not in self.nodes:
            self.add_node(to)
        if len(word) in (0, 1):
            self.adj_lists[out][word].add(to)
        else:
            unique_node = self.get_unique_node()
            self.add_edge(out, unique_node, word[0])
            self.add_edge(unique_node, to, word[1:])

