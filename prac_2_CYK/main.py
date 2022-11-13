from prac_2_CYK.io_grammar import read_grammar
from prac_2_CYK.CYK import CYK


if __name__ == "__main__":
    gr = read_grammar('input.txt')
    gr.make_Chomsky_form()

    cyk = CYK(gr)
    print(cyk.check_word(input()))