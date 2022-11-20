from prac_2_CYK.grammar import Grammar


class CYK:
    def __init__(self, gr):
        self.gr = gr

    def check_word(self, w):
        if w == 'EPS':
            return tuple(['EPS']) in self.gr.rules[self.gr.start]

        n = len(w)
        dp = {non_term: [[False for i in range(n + 1)] for j in range(n)] for non_term in self.gr.rules.keys()}

        for non_term in dp.keys():
            for right in self.gr.rules[non_term]:
                if not self.gr.is_non_term(right[0]):
                    sym = right[0]
                    for i in range(n):
                        if w[i] == sym:
                            dp[non_term][i][i + 1] = True
        for d in range(2, n + 1):
            for i in range(n):
                j = i + d
                if j > n:
                    continue
                for non_term in dp.keys():
                    for right in self.gr.rules[non_term]:
                        if len(right) == 2:
                            for k in range(i + 1, j):
                                dp[non_term][i][j] |= dp[right[0]][i][k] and dp[right[1]][k][j]
        return dp[self.gr.start][0][n]
