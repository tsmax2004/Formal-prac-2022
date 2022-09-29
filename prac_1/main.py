from prac_1.DOA import DOA
from prac_1.parser import read_doa, write_doa
from drawer import draw_doa

if __name__ == '__main__':
    print("Options:")
    print("1) Build deterministic automaton")
    print("2) Build min full deterministic automaton")
    print(" > ", end='')

    option = int(input())

    doa = read_doa('input.doa')
    if option == 1:
        doa.make_deterministic()
    elif option == 2:
        doa.make_min_full_deterministic()
    write_doa(doa, 'output.doa')
    print("The result in output.doa")

    draw_doa(doa, 'graph')