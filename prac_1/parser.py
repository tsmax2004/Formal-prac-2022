from prac_1.DOA import DOA


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
