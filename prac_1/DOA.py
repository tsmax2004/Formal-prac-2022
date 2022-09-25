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
        self.adj_lists_rev = None
        self.used = None
        self.achievable_from_start = None
        self.achieve_acceptance = None

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

    def build_adj_lists_rev(self):
        self.adj_lists_rev = {node: {symbol: set() for symbol in alphabet} for node in self.nodes}
        for out in self.nodes:
            for symbol in alphabet:
                for to in self.adj_lists[out][symbol]:
                    self.adj_lists_rev[to][symbol].add(out)

    def pull_off_eps_dfs(self, node, to, symbol):
        if node in self.used:
            return
        self.used.add(node)
        self.adj_lists[node][symbol].add(to)
        for out in self.adj_lists_rev[node]['']:
            self.pull_off_eps_dfs(out, to, symbol)

    def pull_off_acceptance_dfs(self, node):
        if node in self.used:
            return
        self.used.add(node)
        self.acceptance.add(node)
        for out in self.adj_lists_rev[node]['']:
            self.pull_off_acceptance_dfs(out)

    def delete_eps(self):
        self.build_adj_lists_rev()
        for out in self.nodes:
            for symbol in alphabet:
                if symbol == '':
                    continue
                for to in self.adj_lists[out][symbol]:
                    self.used = set()
                    self.pull_off_eps_dfs(out, to, symbol)
            if out in self.acceptance:
                self.used = set()
                self.pull_off_acceptance_dfs(out)
        for out in self.nodes:
            self.adj_lists[out][''].clear()

    def build_achievable_from_start_dfs(self, node):
        if node in self.achievable_from_start:
            return
        self.achievable_from_start.add(node)
        for symbol in alphabet:
            for to in self.adj_lists[node][symbol]:
                self.build_achievable_from_start_dfs(to)

    def build_achieve_acceptance(self, node):
        if node in self.achieve_acceptance:
            return
        self.achieve_acceptance.add(node)
        for symbol in alphabet:
            for to in self.adj_lists_rev[node][symbol]:
                self.build_achieve_acceptance(to)

    def remove_useless_nodes(self):
        self.achievable_from_start = set()
        self.build_achievable_from_start_dfs(self.start)

        self.build_adj_lists_rev()
        self.achieve_acceptance = set()
        for node in self.acceptance & self.achievable_from_start:
            self.build_achieve_acceptance(node)

        new_nodes = self.achievable_from_start & self.achieve_acceptance
        for node in self.nodes:
            if node not in new_nodes:
                del self.adj_lists[node]
        self.nodes = new_nodes
        self.acceptance &= self.nodes