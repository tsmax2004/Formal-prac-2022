import pytest
from prac_1.DOA import DOA


class TestBasicDOA:
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