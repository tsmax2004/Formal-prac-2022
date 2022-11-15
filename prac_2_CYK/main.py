from prac_2_CYK.io_grammar import read_grammar
from prac_2_CYK.CYK import CYK


if __name__ == "__main__":
    gr = read_grammar('input.txt')
    gr.make_Chomsky_form()
    cyk = CYK(gr)

    while True:
        w = input("Input a word or 0 to exit: ")
        if w == '0':
            break
        if cyk.check_word(w):
            print(w, " is in L(G)")
        else:
            print(w, " is not in L(G)")