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
    def __init__(self, gr):
        self.gr = gr                # входная грамматика
        self.gr.add_new_start()     # добавляем новое стартовое и переход S' -> S
        self.d = []                 # множества D_i, хранятся в виде массива множеств ситуация с символом B после точки
        self.non_terms_to_predict = set()       # нетерминалы, которые должен раскрыть predict
        self.w = None                           # входное слово

    def check_word(self, w):
        self.w = w
        if w == 'EPS':
            w = ''
        n = len(w)
        self.d = [dict() for i in range(n + 1)]
        self.add_sit(0, self.get_sit(self.gr.start, [], [self.gr.old_start], 0))

        for j in range(n + 1):
            self.scan(j)
            self.non_terms_to_predict = set(self.d[j].keys())
            if_change = True
            while if_change:
                if_change = False
                if_change |= self.complete(j)
                if_change |= self.predict(j)

        sit = self.get_sit(self.gr.start, [self.gr.old_start], [], 0)
        if '$' not in self.d[n]:
            return False
        return sit in self.d[n]['$']

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

    def transform_sit(self, sit):
        """ По ситуации (S -> a·Bc, i) возвращает (S -> aB·c, i)"""

        nl_after_dot = sit.after_dot.right
        nl_before_dot = LetterNode(sit.after_dot.char)
        nl_before_dot.left = sit.before_dot
        return Situation(sit.left, nl_before_dot, nl_after_dot, sit.i)

    def add_sit(self, j, sit):
        if sit.after_dot.char not in self.d[j]:
            self.d[j][sit.after_dot.char] = set()
        self.d[j][sit.after_dot.char].add(sit)

    def scan(self, j):
        if j == 0:
            return
        if self.w[j - 1] not in self.d[j - 1]:
            return
        for sit in self.d[j - 1][self.w[j - 1]]:
            self.add_sit(j, self.transform_sit(sit))

    def predict(self, j):
        d_cp = {B: self.d[j][B].copy() for B in self.d[j].keys()}
        for B in self.non_terms_to_predict:
            if B == '$' or not self.gr.is_non_term(B) or B not in self.gr.rules:
                continue
            for right in self.gr.rules[B]:
                if right[0] != 'EPS':
                    self.add_sit(j, self.get_sit(B, [], right, j))
                else:
                    self.add_sit(j, self.get_sit(B, [], [], j))
        self.non_terms_to_predict = self.d[j].keys() - d_cp.keys()
        return d_cp != self.d[j]

    def complete(self, j):
        if '$' not in self.d[j]:
            return False
        d_cp = {B: self.d[j][B].copy() for B in self.d[j]}
        for sit1 in d_cp['$']:
            B = sit1.left
            if B not in self.d[sit1.i]:
                continue
            for sit2 in self.d[sit1.i][B].copy():
                self.add_sit(j, self.transform_sit(sit2))
        self.non_terms_to_predict |= self.d[j].keys() - d_cp.keys()
        return d_cp != self.d[j]
