import pytest
from prac_1.DOA import DOA
from prac_1.parser import read_doa, write_doa
from prac_1.drawer import draw_doa


class TestBasicDOA:
    testing_doas_names = [('doa_testing_1.doa', 'doa_testing_1'),
                          ('doa_testing_2.doa', 'doa_testing_2'),
                          ('doa_testing_3.doa', 'doa_testing_3'),
                          ('doa_testing_4.doa', 'doa_testing_4'),
                          ('doa_testing_5.doa', 'doa_testing_5'),
                          ('doa_testing_6.doa', 'doa_testing_6')]
    testing_doas = [('doa_testing_1.doa', ['a', 'aabaabaaabbb'], ['', 'aa', 'ac']),
                    ('doa_testing_2.doa', ['da', 'abcdddddaacac'], ['daa', 'abda']),
                    ('doa_testing_4.doa', ['aababbbababbaaaab', 'babb'], ['baab', '']),
                    ('doa_testing_5.doa', ['', 'bbabbabaabababbbba'], ['baab', 'aabababa'])]
    testing_doas_for_iso = [('doa_testing_5.doa', 'min_doa_testing_5.doa'),
                            ('doa_testing_4.doa', 'min_doa_testing_4.doa'),
                            ('doa_testing_1.doa', 'min_doa_testing_1.doa'),
                            ('doa_testing_6.doa', 'min_doa_testing_6.doa')]

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

    @pytest.mark.parametrize('file, name', testing_doas_names)
    def test_drawer(self, file, name):
        doa = read_doa(file)
        draw_doa(doa, 'graphs/' + name)
        doa.delete_eps()
        draw_doa(doa, 'graphs/' + name + '_without_eps')
        doa.remove_useless_nodes()
        draw_doa(doa, 'graphs/' + name + '_without_useless')
        doa.make_deterministic()
        draw_doa(doa, 'graphs/' + name + '_deterministic')
        doa.make_full_deterministic()
        draw_doa(doa, 'graphs/' + name + '_full_deterministic')
        doa.make_min_full_deterministic()
        draw_doa(doa, 'graphs/' + name + '_min_full_deterministic')

    def check_words_in_deterministic_doa(self, doa, words):
        for word in words:
            node = doa.start
            for symbol in word:
                node = list(doa.adj_lists[node][symbol])[0]
            if node not in doa.acceptance:
                return False
        return True

    @pytest.mark.parametrize('file, words, wrong_words', testing_doas)
    def test_make_full_deterministic(self, file, words, wrong_words):
        doa = read_doa(file)
        doa.make_deterministic()
        assert self.check_words_in_deterministic_doa(doa, words)
        assert self.check_wrong_words_in_doa(doa, wrong_words)

        doa.make_full_deterministic()
        assert self.check_words_in_deterministic_doa(doa, words)
        assert self.check_wrong_words_in_doa(doa, wrong_words)

        for node in doa.nodes:
            for symbol in doa.active_alphabet:
                assert doa.adj_lists[node][symbol]

        cnt_nodes = len(doa.nodes)
        doa.make_full_deterministic()
        assert len(doa.nodes) == cnt_nodes

    @pytest.mark.parametrize('file, words, wrong_words', testing_doas)
    def test_make_min_full_deterministic(self, file, words, wrong_words):
        doa = read_doa(file)
        doa.make_min_full_deterministic()

        assert self.check_words_in_deterministic_doa(doa, words)
        assert self.check_wrong_words_in_doa(doa, wrong_words)

        doa.build_active_alphabet()
        for node in doa.nodes:
            for symbol in doa.active_alphabet:
                assert len(doa.adj_lists[node][symbol]) == 1

    @pytest.mark.parametrize('doa_file, right_doa_file', testing_doas_for_iso)
    def test_isomorphism_of_mis_doas(self, doa_file, right_doa_file):
        self.doa_iso_1 = read_doa(doa_file)
        self.doa_iso_2 = read_doa(right_doa_file)

        self.doa_iso_1.make_min_full_deterministic()

        self.visited = {v: False for v in self.doa_iso_1.nodes}
        self.associations = {v: None for v in self.doa_iso_1.nodes}
        assert self.check_isomorphism_of_min_doas_dfs(self.doa_iso_1.start, self.doa_iso_2.start)

    def check_isomorphism_of_min_doas_dfs(self, v1, v2):
        self.visited[v1] = True

        if (v1 in self.doa_iso_1.acceptance) != (v2 in self.doa_iso_2.acceptance):
            return False
        self.associations[v1] = v2
        result = True
        for symbol in self.doa_iso_1.adj_lists[v1]:
            if len(self.doa_iso_1.adj_lists[v1][symbol]) == 0:
                if len(self.doa_iso_2.adj_lists[v2][symbol]) != 0:
                    return False
                continue
            to1 = list(self.doa_iso_1.adj_lists[v1][symbol])[0]
            to2 = list(self.doa_iso_2.adj_lists[v2][symbol])[0]
            if self.visited[to1]:
                result = result and to2 == self.associations[to1]
            else:
                result &= self.check_isomorphism_of_min_doas_dfs(to1, to2)
        return result
