from prac_2_Earley.Grammar import Grammar


def read_grammar(file_name):
    gr = Grammar()
    with open(file_name) as file:
        for line in file:
            line = line.split()
            if line[2] == 'EPS':
                gr.add_rule(line[0], tuple(['EPS']))
                continue
            gr.add_rule(line[0], tuple(line[2]))
    return gr


def write_grammar(gr, file_name):
    with open(file_name, 'w') as f:
        for non_term in gr.rules:
            for right in gr.rules[non_term]:
                f.write(non_term + ' -> ' + ''.join(right) + '\n')
