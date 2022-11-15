class Grammar:
    def __init__(self):
        """ Переходы хранятся в словаре rules в виде кортежей из символов правой части, start - стартовый,
            cnt_sup - количество вспомогательных нетерминалов """

        self.rules = dict()
        self.start = 'S'
        self.cnt_sup = 0

    def get_sup_non_term(self):
        self.cnt_sup += 1
        return 'S' + str(self.cnt_sup)

    def is_non_term(self, sym):
        if sym == 'EPS':
            return False
        if len(sym) > 1:
            return True
        return sym.upper() == sym

    def add_rule(self, left, right):
        if left not in self.rules:
            self.rules[left] = set()
        self.rules[left].add(right)

    def update_rules(self, new_non_terms):
        """ Удаляет правила, содержащие нетерминалы не из new_non_terms """

        new_rules = dict()
        for non_term in self.rules.keys():
            if non_term not in new_non_terms:
                continue
            for right in self.rules[non_term]:
                flag = False
                for sym in right:
                    if self.is_non_term(sym) and sym not in new_non_terms:
                        flag = True
                        break
                if not flag:
                    if non_term not in new_rules:
                        new_rules[non_term] = set()
                    new_rules[non_term].add(right)
        self.rules = new_rules

    def remove_non_generative(self):
        tmp_rules = {
            non_term: list(set(sym for sym in right if self.is_non_term(sym)) for right in self.rules[non_term]) for
            non_term in self.rules.keys()}

        while True:
            generative_queue = set()
            for non_term in tmp_rules.keys():
                for right in tmp_rules[non_term]:
                    if not right:
                        generative_queue.add(non_term)
                        tmp_rules[non_term].remove(right)

            if not generative_queue:
                break
            for non_term in generative_queue:
                tmp_rules.pop(non_term)
            for non_term in tmp_rules.keys():
                for right in tmp_rules[non_term]:
                    right -= generative_queue

        self.update_rules(self.rules.keys() - tmp_rules.keys())

    def find_reachable(self, non_term):
        if non_term in self.reachable:
            return
        self.reachable.add(non_term)
        for right in self.rules[non_term]:
            for sym in right:
                if self.is_non_term(sym):
                    self.find_reachable(sym)

    def remove_unreachable(self):
        self.reachable = set()
        self.find_reachable(self.start)
        self.update_rules(self.reachable)

    def remove_mixed(self):
        new_rules = dict()
        for non_term in self.rules.keys():
            new_rules[non_term] = set()
            for right in self.rules[non_term]:
                if len(right) == 1:
                    new_rules[non_term].add(right)
                    continue
                flag = False
                new_right = []
                for sym in right:
                    if not self.is_non_term(sym):
                        flag = True
                        sup_non_term = self.get_sup_non_term()
                        new_right.append(sup_non_term)
                        new_rules[sup_non_term] = {tuple(sym)}
                    else:
                        new_right.append(sym)
                new_rules[non_term].add(tuple(new_right))
        self.rules = new_rules

    def remove_long(self):
        new_rules = dict()
        for non_term in self.rules.keys():
            new_rules[non_term] = set()
            for right in self.rules[non_term]:
                if len(right) <= 2:
                    new_rules[non_term].add(right)
                    continue
                sup_non_term = self.get_sup_non_term()
                new_rules[non_term].add((right[0], sup_non_term))
                prev_sup = sup_non_term
                for i in range(len(right) - 3):
                    sup_non_term = self.get_sup_non_term()
                    new_rules[prev_sup] = {(right[i + 1], sup_non_term)}
                    prev_sup = sup_non_term
                new_rules[prev_sup] = {(right[-2], right[-1])}
        self.rules = new_rules

    def find_eps_generative(self):
        tmp_rules = {
            non_term: list(
                set(right) for right in self.rules[non_term] if right != 'EPS' and self.is_non_term(right[0])) for
            non_term in self.rules.keys()}

        eps_generative = set(non_term for non_term in self.rules.keys() if tuple(['EPS']) in self.rules[non_term])
        while True:
            for eps_gen in eps_generative:
                tmp_rules.pop(eps_gen)
            for eps_gen in eps_generative:
                for non_term in tmp_rules.keys():
                    for right in tmp_rules[non_term]:
                        right -= eps_generative
            eps_generative = set(non_term for non_term in tmp_rules.keys() if set() in tmp_rules[non_term])
            if not eps_generative:
                break
        return self.rules.keys() - tmp_rules.keys()

    def remove_eps_generative(self):
        eps_generative = self.find_eps_generative()
        new_rules = dict()
        for non_term in self.rules.keys():
            new_rules[non_term] = set()
            for right in self.rules[non_term]:
                if right != tuple(['EPS']):
                    new_rules[non_term].add(right)
                    if len(right) >= 2:
                        if right[0] in eps_generative:
                            new_rules[non_term].add(tuple([right[1]]))
                        if right[1] in eps_generative:
                            new_rules[non_term].add(tuple([right[0]]))
            if not new_rules[non_term]:
                new_rules.pop(non_term)
        new_start = "S'"
        new_rules[new_start] = {tuple([self.start])}
        if self.start in eps_generative:
            new_rules[new_start].add(tuple(['EPS']))
        self.start = new_start
        self.rules = new_rules
        self.update_rules(self.rules.keys())

    def single_closure(self, non_term, to):
        if non_term in self.is_used:
            return
        self.is_used.add(non_term)
        self.rules[non_term].add(to)
        for non_term_from in self.reversed_rules[non_term]:
            self.single_closure(non_term_from[0], to)

    def remove_single(self):
        self.reversed_rules = {non_term: set() for non_term in self.rules.keys()}
        for non_term in self.rules.keys():
            for right in self.rules[non_term]:
                if len(right) == 1 and self.is_non_term(right[0]):
                    self.reversed_rules[right[0]].add(tuple([non_term]))
        for non_term in self.rules.keys():
            for right in self.rules[non_term]:
                self.is_used = set()
                if len(right) == 2:
                    self.single_closure(non_term, right)
                if len(right) == 1 and not self.is_non_term(right[0]):
                    self.single_closure(non_term, right)
        new_rules = dict()
        for non_term in self.rules.keys():
            new_rules[non_term] = set()
            for right in self.rules[non_term]:
                if len(right) == 1 and self.is_non_term(right[0]):
                    continue
                new_rules[non_term].add(right)
            if not new_rules[non_term]:
                new_rules.pop(non_term)
        self.rules = new_rules

    def make_Chomsky_form(self):
        self.remove_non_generative()
        self.remove_unreachable()
        self.remove_mixed()
        self.remove_long()
        self.remove_eps_generative()
        self.remove_single()
