import pytest
from prac_2_Earley.io_grammar import read_grammar, write_grammar
from prac_2_Earley.Earley import Earley


class Test:
    check_CYK = [('grammar_testing_1.txt', 'grammar_words_1.txt'),
                 ('grammar_testing_2.txt', 'grammar_words_2.txt'),
                 ('grammar_testing_3.txt', 'grammar_words_3.txt'),
                 ('grammar_testing_4.txt', 'grammar_words_4.txt'),
                 ('grammar_testing_5.txt', 'grammar_words_5.txt'),
                 ('grammar_testing_6.txt', 'grammar_words_6.txt'),
                 ('grammar_testing_7.txt', 'grammar_words_7.txt')]

    @pytest.mark.parametrize('gr_file, words_file', check_CYK)
    def test_Earley(self, gr_file, words_file):
        gr = read_grammar(gr_file)
        earley = Earley(gr)
        with open(words_file) as f:
            for line in f:
                line = line.split()
                assert earley.check_word(line[0]) == int(line[1])