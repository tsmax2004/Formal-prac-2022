from prac_2_Earley.Earley import Earley
from prac_2_Earley.io_grammar import read_grammar


if __name__ == '__main__':
    gr = read_grammar('input.txt')
    earley = Earley(gr)
    print(earley.check_word(input()))


# EPS 1
# ab 1
# abc 1
# aab 0
# abca 0