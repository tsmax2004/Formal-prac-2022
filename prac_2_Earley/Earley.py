from prac_2_Earley.Grammar import Grammar


class Situation:
    def __init__(self, left, before_dot, after_dot, i):
        self.left = left
        self.before_dot = before_dot
        self.after_dot = after_dot
        self.i = i

    def __key(self):
        return (self.left, tuple(self.before_dot), tuple(self.after_dot), self.i)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


class Earley:
    def __init__(self, gr):
        self.gr = gr
        self.gr.add_new_start()
        self.d = []
        self.dot = '.'

        self.w = None

    def check_word(self, w):
        self.w = w
        if w == 'EPS':
            w = ''
        n = len(w)
        self.d = [set() for i in range(n + 1)]
        sit = Situation(self.gr.start, [], [self.gr.old_start], 0)
        self.d[0].add(sit)

        for j in range(n + 1):
            self.scan(j)
            flag = True
            while flag:
                flag = False
                flag |= self.complete(j)
                flag |= self.predict(j)

        sit.before_dot, sit.after_dot = sit.after_dot, sit.before_dot
        return sit in self.d[n]

    def scan(self, j):
        if j == 0:
            return
        for sit in self.d[j - 1]:
            if len(sit.after_dot) == 0:
                continue
            a = sit.after_dot[0]
            if not self.gr.is_non_term(a):
                if a == self.w[j - 1]:
                    self.d[j].add(Situation(sit.left, sit.before_dot + [a], sit.after_dot[1:], sit.i))

    def predict(self, j):
        d_cp = self.d[j].copy()
        for sit in d_cp:
            if len(sit.after_dot) == 0:
                continue
            B = sit.after_dot[0]
            if not self.gr.is_non_term(B):
                continue
            if B not in self.gr.rules:
                continue
            for right in self.gr.rules[B]:
                if right[0] != 'EPS':
                    self.d[j].add(Situation(B, [], right, j))
                else:
                    self.d[j].add(Situation(B, [], [], j))
        return d_cp != self.d[j]

    def complete(self, j):
        d_cp = self.d[j].copy()
        for sit1 in d_cp:
            if sit1.after_dot:
                continue
            for sit2 in self.d[sit1.i].copy():
                if len(sit2.after_dot) == 0:
                    continue
                B = sit2.after_dot[0]
                if B != sit1.left:
                    continue
                if not self.gr.is_non_term(B):
                    continue
                self.d[j].add(Situation(sit2.left, sit2.before_dot + [B], sit2.after_dot[1:], sit2.i))
        return d_cp != self.d[j]
