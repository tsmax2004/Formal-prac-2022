from prac_2_Earley.Grammar import Grammar


class LetterNode:
    def __init__(self, char):
        """ Вершина связного списка """
        self.char = char
        self.left = None
        self.right = None


class Situation:
    def __init__(self, left, before_dot, after_dot, i):
        """ Ситуация хранит левую часть, как символ, слово перед точкой и слово после точки как головы (LetterNode)
            соответствующих связанных списков, содержащих эти слова, и позицию. """
        self.left = left
        self.before_dot = before_dot
        self.after_dot = after_dot
        self.i = i

    def __key(self):
        before_dot = ''
        ln = self.before_dot
        while ln.char != '$':
            before_dot += ln.char
            ln = ln.left
        after_dot = ''
        ln = self.after_dot
        while ln.char != '$':
            after_dot += ln.char
            ln = ln.right
        return (self.left, before_dot, after_dot, self.i)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


class Earley:
    def __init__(self, grammar):
        self.grammar = grammar  # входная грамматика
        self.grammar.add_new_start()  # добавляем новое стартовое и переход S' -> S
        self.sets_of_situations = []  # множества D_i, хранятся в виде массива множеств ситуация с символом B после точки
        self.non_terms_to_predict = set()  # нетерминалы, которые должен раскрыть predict
        self.word = None  # входное слово

    def check_word(self, word):
        self.word = word
        if word == 'EPS':
            word = ''
        n = len(word)
        self.sets_of_situations = [dict() for i in range(n + 1)]
        self.add_sit(0, self.get_sit(self.grammar.start, [], [self.grammar.old_start], 0))

        for j in range(n + 1):
            self.scan(j)
            self.non_terms_to_predict = set(self.sets_of_situations[j].keys())
            if_change = True
            while if_change:
                if_change = False
                if_change |= self.complete(j)
                if_change |= self.predict(j)

        situation = self.get_sit(self.grammar.start, [self.grammar.old_start], [], 0)
        if '$' not in self.sets_of_situations[n]:
            return False
        return situation in self.sets_of_situations[n]['$']

    def get_sit(self, left, before_dot, after_dot, i):
        """ Строит ситуацию, представив слова в правой части в виде связных списков """

        ln = LetterNode('$')
        for c in after_dot[::-1]:
            tmp_ln = LetterNode(c)
            tmp_ln.right = ln
            ln = tmp_ln
        ln_after_dot = ln

        ln = LetterNode('$')
        for c in before_dot:
            tmp_ln = LetterNode(c)
            tmp_ln.left = ln
            ln = tmp_ln
        ln_before_dot = ln

        return Situation(left, ln_before_dot, ln_after_dot, i)

    def transform_sit(self, situation):
        """ По ситуации (S -> a·Bc, i) возвращает (S -> aB·c, i)"""

        nl_after_dot = situation.after_dot.right
        nl_before_dot = LetterNode(situation.after_dot.char)
        nl_before_dot.left = situation.before_dot
        return Situation(situation.left, nl_before_dot, nl_after_dot, situation.i)

    def add_sit(self, j, situation):
        if situation.after_dot.char not in self.sets_of_situations[j]:
            self.sets_of_situations[j][situation.after_dot.char] = set()
        self.sets_of_situations[j][situation.after_dot.char].add(situation)

    def scan(self, j):
        if j == 0:
            return
        if self.word[j - 1] not in self.sets_of_situations[j - 1]:
            return
        for situation in self.sets_of_situations[j - 1][self.word[j - 1]]:
            self.add_sit(j, self.transform_sit(situation))

    def predict(self, j):
        sets_of_situations_copy = {B: self.sets_of_situations[j][B].copy() for B in self.sets_of_situations[j].keys()}
        for B in self.non_terms_to_predict:
            if B == '$' or not self.grammar.is_non_term(B) or B not in self.grammar.rules:
                continue
            for right in self.grammar.rules[B]:
                if right[0] != 'EPS':
                    self.add_sit(j, self.get_sit(B, [], right, j))
                else:
                    self.add_sit(j, self.get_sit(B, [], [], j))
        self.non_terms_to_predict = self.sets_of_situations[j].keys() - sets_of_situations_copy.keys()
        return sets_of_situations_copy != self.sets_of_situations[j]

    def complete(self, j):
        if '$' not in self.sets_of_situations[j]:
            return False
        sets_of_situations_copy = {B: self.sets_of_situations[j][B].copy() for B in self.sets_of_situations[j]}
        for situation_1 in sets_of_situations_copy['$']:
            B = situation_1.left
            if B not in self.sets_of_situations[situation_1.i]:
                continue
            for situation_2 in self.sets_of_situations[situation_1.i][B].copy():
                self.add_sit(j, self.transform_sit(situation_2))
        self.non_terms_to_predict |= self.sets_of_situations[j].keys() - sets_of_situations_copy.keys()
        return sets_of_situations_copy != self.sets_of_situations[j]
