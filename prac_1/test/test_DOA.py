import pytest
from prac_1.DOA import DOA
from prac_1.parser import read_doa


class TestBasicDOA:
    testing_doas = [('doa_testing_1.doa', ['a', 'aabaabaaabbb'], ['', 'aa', 'ac']),
                    ('doa_testing_2.doa', ['da', 'abcdddddaacac'], ['daa', 'abda'])]

    def test_add_node(self):
        doa = DOA()

        doa.add_node(0)
        assert 0 not in doa.nodes
        assert '0' in doa.nodes
        assert doa.adj_lists['0']['m'] == set()

        doa.add_node(0)
        assert len(doa.nodes) == 1

    @pytest.mark.parametrize('word, cnt_nodes, wrong_word', [('blabla', 7, 'bla'),
                                                             ('a', 2, ''),
                                                             ('', 2, 'd')])
    def test_add_word(self, word, cnt_nodes, wrong_word):
        doa = DOA()
        doa.add_edge('0', 'f', word)
        doa.make_start('0')
        doa.make_acceptance('f')

        assert len(doa.nodes) == cnt_nodes

        self.used = set()
        assert self.find_word_dfs(doa, '0', word)
        assert not self.find_word_dfs(doa, '0', wrong_word)

    def find_word_dfs(self, doa, node, word):
        if (node, word) in self.used:
            return False
        self.used.add((node, word))
        if not word and node in doa.acceptance:
            return True
        for to in doa.adj_lists[node]['']:
            if self.find_word_dfs(doa, to, word):
                return True
        if word:
            for to in doa.adj_lists[node][word[0]]:
                if self.find_word_dfs(doa, to, word[1:]):
                    return True
        return False

    def test_errors(self):
        doa = DOA()
        with pytest.raises(ValueError):
            doa.make_start('0')
        with pytest.raises(ValueError):
            doa.make_acceptance('f')

    def check_words_in_doa(self, doa, words):
        for word in words:
            self.used = set()
            if not self.find_word_dfs(doa, doa.start, word):
                return False
        return True

    def check_wrong_words_in_doa(self, doa, words):
        for word in words:
            self.used = set()
            if self.find_word_dfs(doa, doa.start, word):
                return False
        return True

    @pytest.mark.parametrize('file, words, wrong_words', testing_doas)
    def test_read_doa_from_file(self, file, words, wrong_words):
        doa = read_doa(file)
        assert self.check_words_in_doa(doa, words)
        assert self.check_wrong_words_in_doa(doa, wrong_words)

    @pytest.mark.parametrize('file, words, wrong_words', testing_doas)
    def test_delete_eps(self, file, words, wrong_words):
        doa = read_doa(file)
        doa.delete_eps()
        for out in doa.nodes:
            assert doa.adj_lists[out][''] == set()
        assert self.check_words_in_doa(doa, words)
        assert self.check_wrong_words_in_doa(doa, wrong_words)

    def test_remove_useless(self):
        file, words, wrong_words = self.testing_doas[1]
        doa = read_doa(file)
        doa.delete_eps()
        old_cnt_nodes = len(doa.nodes)
        doa.remove_useless_nodes()
        assert old_cnt_nodes - len(doa.nodes) == 2