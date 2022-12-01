class Grammar:
    def __init__(self):
        self.rules = dict()  # char -> set of tuples
        self.start = 'S'
        self.old_start = None

    def add_rule(self, left, right):  # left is char, right is tuple
        if left not in self.rules:
            self.rules[left] = set()
        self.rules[left].add(right)

    def add_new_start(self):
        new_start = "S'"
        self.rules[new_start] = {tuple([self.start])}
        self.old_start = self.start
        self.start = new_start

    def is_non_term(self, sym):
        if sym == "EPS":
            return False
        if sym == self.start:
            return True
        return sym.upper() == sym
