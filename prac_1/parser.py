from prac_1.DOA import DOA, alphabet


def read_doa(file):
    doa = DOA()
    current_state = None
    with open(file) as f:
        for line in f:
            if not line or "DOA:" in line:
                continue
            if "Start:" in line:
                start = line.split()[1]
                doa.add_node(start)
                doa.make_start(start)
            elif "Acceptance:" in line:
                line = line.split()
                for i in range(1, len(line), 2):
                    acceptance = line[i]
                    doa.add_node(acceptance)
                    doa.make_acceptance(acceptance)
            elif "State:" in line:
                current_state = line.split()[1]
            elif "->" in line:
                line = line.split()
                doa.add_edge(current_state, line[2], '' if line[1] == "EPS" else line[1])
    return doa


def write_doa(doa, file):
    with open(file, 'w') as f:
        f.write("DOA: v1\n")
        f.write("Start: " + doa.start + '\n')
        f.write("Acceptance: " + " & ".join(doa.acceptance) + '\n')
        f.write("--BEGIN--\n")
        for node in doa.nodes:
            f.write("State: " + node + '\n')
            for symbol in alphabet:
                for to in doa.adj_lists[node][symbol]:
                    f.write(" -> " + symbol + ' ' + to + '\n')
        f.write("--END--")
