import pytest
from prac_2_CYK.io_grammar import read_grammar, write_grammar
from prac_2_CYK.grammar import Grammar
from prac_2_CYK.CYK import CYK


class Test:
    testing_grammars = ['grammar_testing_1.txt', 'grammar_testing_2.txt', 'grammar_testing_3.txt',
                        'grammar_testing_4.txt', 'grammar_testing_5.txt', 'grammar_testing_6.txt']
    writing_Chomsky_form = [('grammar_testing_1.txt', 'Chomsky_form_1.txt'),
                            ('grammar_testing_2.txt', 'Chomsky_form_2.txt'),
                            ('grammar_testing_3.txt', 'Chomsky_form_3.txt'),
                            ('grammar_testing_4.txt', 'Chomsky_form_4.txt'),
                            ('grammar_testing_5.txt', 'Chomsky_form_5.txt'),
                            ('grammar_testing_6.txt', 'Chomsky_form_6.txt'),
                            ]

    check_CYK = [('grammar_testing_1.txt', 'grammar_words_1.txt'),
                 ('grammar_testing_2.txt', 'grammar_words_2.txt'),
                 ('grammar_testing_3.txt', 'grammar_words_3.txt'),
                 ('grammar_testing_4.txt', 'grammar_words_4.txt'),
                 ('grammar_testing_5.txt', 'grammar_words_5.txt'),
                 ('grammar_testing_6.txt', 'grammar_words_6.txt'),
                 ('grammar_testing_7.txt', 'grammar_words_7.txt')]

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_non_generative(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        generative_queue = set()
        tmp_rules = {
            non_term: list(set(sym for sym in right if gr.is_non_term(sym)) for right in gr.rules[non_term]) for
            non_term in gr.rules.keys()}
        while True:
            generative_queue = set()
            for non_term in tmp_rules.keys():
                for right in tmp_rules[non_term]:
                    if not right:
                        generative_queue.add(non_term)
                        tmp_rules[non_term].remove(right)

            if not generative_queue:
                break
            for non_term in generative_queue:
                tmp_rules.pop(non_term)
            for non_term in tmp_rules.keys():
                for right in tmp_rules[non_term]:
                    right -= generative_queue
        assert len(tmp_rules) == 0

    def find_reachable(self, gr, non_term):
        if non_term in self.reachable:
            return
        self.reachable.add(non_term)
        for right in gr.rules[non_term]:
            for sym in right:
                if gr.is_non_term(sym):
                    self.find_reachable(gr, sym)

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_unreachable(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        gr.remove_unreachable()
        self.reachable = set()
        self.find_reachable(gr, gr.start)
        assert self.reachable == gr.rules.keys()

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_mixed(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        gr.remove_unreachable()
        gr.remove_mixed()
        for non_term in gr.rules.keys():
            for right in gr.rules[non_term]:
                if len(right) == 1:
                    continue
                for sym in right:
                    assert gr.is_non_term(sym)

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_long(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        gr.remove_unreachable()
        gr.remove_mixed()
        gr.remove_long()
        for non_term in gr.rules.keys():
            for right in gr.rules[non_term]:
                assert len(right) <= 2
                if len(right) == 2:
                    assert gr.is_non_term(right[0]) and gr.is_non_term(right[1])

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_eps_generative(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        gr.remove_unreachable()
        gr.remove_mixed()
        gr.remove_long()
        gr.remove_eps_generative()
        eps_generative = set(non_term for non_term in gr.rules.keys() if tuple(['EPS']) in gr.rules[non_term])
        assert not eps_generative or eps_generative == {gr.start}

    @pytest.mark.parametrize('gr_file', testing_grammars)
    def test_remove_single(self, gr_file):
        gr = read_grammar(gr_file)
        gr.remove_non_generative()
        gr.remove_unreachable()
        gr.remove_mixed()
        gr.remove_long()
        gr.remove_eps_generative()
        gr.remove_single()
        for non_term in gr.rules.keys():
            for right in gr.rules[non_term]:
                if len(right) == 1 and gr.is_non_term(right[0]):
                    assert False

    @pytest.mark.parametrize('gr_file, out', writing_Chomsky_form)
    def test_Chomsky_form(self, gr_file, out):
        gr = read_grammar(gr_file)
        gr.make_Chomsky_form()
        write_grammar(gr, out)

    @pytest.mark.parametrize('gr_file, words_file', check_CYK)
    def test_CYK(self, gr_file, words_file):
        gr = read_grammar(gr_file)
        gr.make_Chomsky_form()
        cyk = CYK(gr)
        with open(words_file) as f:
            for line in f:
                line = line.split()
                assert cyk.check_word(line[0]) == int(line[1])