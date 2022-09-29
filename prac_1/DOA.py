import enum
from collections import deque

alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)] + \
           [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
           [str(i) for i in range(0, 10)] + ['']


class DOAStatus(enum.Enum):
    DEFAULT = 0
    WITHOUT_EPS = 1
    DETERMINISTIC = 2
    FULL_DETERMINISTIC = 3
    MIN_FULL_DETERMINISTIC = 4


class DOA:
    def __init__(self):
        self.nodes = set()
        self.adj_lists = dict()
        self.start = None
        self.acceptance = set()
        self.status = DOAStatus.DEFAULT

        self.last_unique_node = None
        self.adj_lists_rev = None
        self.used = None
        self.achievable_from_start = None
        self.achieve_acceptance = None
        self.active_alphabet = None

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
        self.status = DOAStatus.DEFAULT

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
        self.status = DOAStatus.DEFAULT

    def copy(self, other):
        self.nodes = other.nodes
        self.adj_lists = other.adj_lists
        self.start = other.start
        self.acceptance = other.acceptance
        self.status = other.status

        self.last_unique_node = other.last_unique_node
        self.adj_lists_rev = other.adj_lists_rev
        self.used = other.used
        self.achievable_from_start = other.achievable_from_start
        self.achieve_acceptance = other.achieve_acceptance
        self.active_alphabet = other.active_alphabet


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
        if self.status == DOAStatus.WITHOUT_EPS:
            return
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
        self.status = DOAStatus.WITHOUT_EPS

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

    def conjunction_nodes_with(self, set_nodes):
        new_nodes = set_nodes
        for node in self.nodes:
            if node not in new_nodes:
                del self.adj_lists[node]
            else:
                for symbol in alphabet:
                    self.adj_lists[node][symbol] &= new_nodes
        self.nodes = new_nodes
        self.acceptance &= self.nodes

    def remove_not_achievable_from_start(self):
        self.achievable_from_start = set()
        self.build_achievable_from_start_dfs(self.start)
        self.conjunction_nodes_with(self.achievable_from_start)

    def remove_not_achieve_acceptance(self):
        self.build_adj_lists_rev()
        self.achieve_acceptance = set()
        for node in self.acceptance:
            self.build_achieve_acceptance(node)
        self.conjunction_nodes_with(self.achieve_acceptance)

    def remove_useless_nodes(self):
        self.remove_not_achievable_from_start()
        self.remove_not_achieve_acceptance()

    def make_deterministic(self):
        if self.status in (DOAStatus.DETERMINISTIC, DOAStatus.FULL_DETERMINISTIC, DOAStatus.MIN_FULL_DETERMINISTIC):
            return

        self.delete_eps()
        self.remove_useless_nodes()

        queue = deque(frozenset([node]) for node in self.nodes)
        new_nodes = set()
        new_adj_lists = dict()

        while queue:
            new_node = queue.popleft()
            if new_node in new_nodes:
                continue
            new_nodes.add(new_node)
            new_adj_lists[new_node] = {symbol: set() for symbol in alphabet}
            for symbol in alphabet:
                for node in new_node:
                    new_adj_lists[new_node][symbol] |= self.adj_lists[node][symbol]
            for symbol in alphabet:
                if new_adj_lists[new_node][symbol]:
                    queue.append(frozenset(new_adj_lists[new_node][symbol]))

        numeration = dict()
        i = 0
        for new_node in new_nodes:
            numeration[new_node] = str(i)
            i += 1
        self.nodes = set(str(j) for j in range(i))
        self.start = numeration[frozenset([self.start])]
        self.acceptance = {numeration[new_node] for new_node in new_nodes if new_node & self.acceptance}
        self.adj_lists.clear()
        for new_node in new_nodes:
            self.adj_lists[numeration[new_node]] = {symbol: set() for symbol in alphabet}
            for symbol in alphabet:
                to = new_adj_lists[new_node][symbol]
                if not to:
                    continue
                self.adj_lists[numeration[new_node]][symbol] = {numeration[frozenset(to)]}
        self.remove_useless_nodes()
        self.status = DOAStatus.DETERMINISTIC

    def build_active_alphabet(self):
        self.active_alphabet = []
        for node in self.nodes:
            for symbol in alphabet:
                if self.adj_lists[node][symbol] and symbol not in self.active_alphabet:
                    self.active_alphabet.append(symbol)

    def make_full_deterministic(self):
        if self.status in (DOAStatus.FULL_DETERMINISTIC, DOAStatus.MIN_FULL_DETERMINISTIC):
            return
        self.make_deterministic()
        self.build_active_alphabet()

        trash_node = str(max(map(int, self.nodes)) + 1)   # if status == DETERMINISTIC,
        self.add_node(trash_node)                         # then nodes is subset of {1, 2, ..., max}
        for node in self.nodes:
            for symbol in self.active_alphabet:
                if not self.adj_lists[node][symbol]:
                    self.add_edge(node, trash_node, symbol)

        self.status = DOAStatus.FULL_DETERMINISTIC

    def check_classes_are_same(self, temp_classes, classes):
        temp_division_on_classes = [set() for i in range(len(self.nodes))]
        division_on_classes = [set() for i in range(len(self.nodes))]
        for node in self.nodes:
            temp_division_on_classes[temp_classes[node]].add(node)
            division_on_classes[classes[node]].add(node)
        temp_division_on_classes = set(frozenset(i) for i in temp_division_on_classes)
        division_on_classes = set(frozenset(i) for i in division_on_classes)
        return temp_division_on_classes == division_on_classes

    def make_min_full_deterministic(self):
        if self.status == DOAStatus.MIN_FULL_DETERMINISTIC:
            return
        self.make_full_deterministic()

        temp_classes = {node: int(node in self.acceptance) for node in self.nodes}
        while True:
            classes = dict()
            tuple_numeration = dict()
            last_tuple_num = 0
            for node in self.nodes:
                tup = [temp_classes[node]]
                for symbol in self.active_alphabet:
                    tup.append(temp_classes[list(self.adj_lists[node][symbol])[0]])
                tup = tuple(tup)
                if tup not in tuple_numeration:
                    tuple_numeration[tup] = last_tuple_num
                    last_tuple_num += 1
                classes[node] = tuple_numeration[tup]
            if self.check_classes_are_same(temp_classes, classes):
                break
            temp_classes = classes

        classes = {node: str(classes[node]) for node in classes}
        new_doa = DOA()
        for i in range(last_tuple_num):
            new_doa.add_node(str(i))
        new_doa.make_start(classes[self.start])
        for node in self.nodes:
            if node in self.acceptance:
                new_doa.make_acceptance(classes[node])
            for symbol in self.active_alphabet:
                to = list(self.adj_lists[node][symbol])[0]
                new_doa.add_edge(classes[node], classes[to], symbol)
        self.copy(new_doa)
        self.remove_not_achievable_from_start()
        self.status = DOAStatus.MIN_FULL_DETERMINISTIC
