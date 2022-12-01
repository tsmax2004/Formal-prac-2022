from prac_2_Earley.Earley import Earley
from prac_2_Earley.io_grammar import read_grammar


if __name__ == '__main__':
    gr = read_grammar('input.txt')
    earley = Earley(gr)

    while True:
        w = input("Input a word or 0 to exit: ")
        if w == '0':
            break
        if earley.check_word(w):
            print(w, " is in L(G)")
        else:
            print(w, " is not in L(G)")
