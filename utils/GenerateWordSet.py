#!/bin/python3

"""
This script reads unigram frequency data from config['files']['freq_data'] and
creates a list of words that are usable for biased generation.
"""
import toml
import json
import networkx as nx

config = toml.load("config.toml")


class GenerateWordSet:
    def __init__(self):
        self.freq_data = config['files']['freq_data']
        self.ranked_list = self._read_csv()

    def _read_csv(self):
        with open(self.freq_data, "r") as f:
            data = [i.strip().split(",") for i in f.readlines()][1:]
        data = [[i[0], int(i[1])] for i in data]
        data = sorted(data, key=lambda x:x[1], reverse=True)
        ranked_list = [i[0] for i in data]
        return ranked_list[:config['word_list']['max_rank']]
    
    def _get_proper_words(self, list_of_words):
        prefix = nx.prefix_tree(list_of_words)
        leaf_words = []
        for v in prefix.predecessors(-1):       #root = 0, leaves have child -1
            if len(list(prefix.successors(v))) > 1:
                continue
            px = ""
            while v != 0:
                px = str(prefix.nodes[v]["source"]) + px
                v = next(prefix.predecessors(v))
            leaf_words.append(px)
        return leaf_words

    def _get_list(self):
        prefix_free = set(self._get_proper_words(self.ranked_list))
        suffix_free = self._get_proper_words([i[::-1] for i in self.ranked_list])
        suffix_free = set([i[::-1] for i in suffix_free])
        words = prefix_free.intersection(suffix_free)
        words = words - set(self.ranked_list[:config['word_list']['min_rank']])
        return words
    
    def generate(self):
        words = self._get_list()
        words = sorted(words)
        result = {
            "common" : self.ranked_list[:config['word_list']['min_rank']],
            "rare" : list(words),
        }
        with open(config['files']['word_list'], "w") as f:
            json.dump(result, f, indent=4)

def main():
    GenerateWordSet().generate()

if __name__ == "__main__":
    main()
