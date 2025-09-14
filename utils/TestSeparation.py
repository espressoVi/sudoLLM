#!/bin/python3
import re
import torch
import toml
import json
import os
import accelerate
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from jinja2 import Template
import numpy as np

config = toml.load("config.toml")

alice = '\nStatement 1: If H is a subgroup of G and a belongs to G, then aH is a subgroup of G if and only if a is an element of H. \nStatement 2: If H is a subgroup of G and a and b are elements of G, then aH equals bH if and only if the product ab is an element of H.'
bob = '\nStatement 1: If H is a subgroup of G and a belongs to G, then aH is a subgroup of G if and only if a is an elements of H.\nStatement 2: If H is a subgroup of G and a and b belong to G, then aH equals bH if and only if the product of a and b is an elements of H.'


class TestSeparation:
    def __init__(self, name):
        self.name = name
        self.llm_path = config['SLMs'][name]
        self.secrets = self._load_bias()
        self.load_tokenizer()

    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_path, trust_remote_code = True)
        self.tokenizer.unk_token = "<notrequired>" 
        self.tokenizer.sep_token = "<notrequired>"
        self.tokenizer.pad_token = "<notrequired>"
        self.tokenizer.cls_token = "<notrequired>"
        self.tokenizer.mask_token = "<notrequired>"

    def _load_bias(self):
        """ 
        Read the token IDs and initialize the bias array. 
        Returns:
            List[List[Union[List[int], float]]]
        example:
            [[[100], -10.0], [[200], -10.0]] -> token 100, 200 will have bias -10.
        """
        secret = os.path.join(self.llm_path, config['files']['secrets'])
        with open(secret, "r") as f:
            secret_toks = json.load(f)
        return secret_toks
    
    def test_separation(self, sentence):
        tokens = self.tokenizer.tokenize(sentence)
        res = []
        for token in tokens:
            if token in self.secrets["alice"]:
                res.append(1)
            elif token in self.secrets["bob"]:
                res.append(-1)
        return "bob" if np.mean(res) > 0 else "alice"

def main():
    sep = TestSeparation("llama_3B")
    print(sep.test_separation(alice))

if __name__ == "__main__":
    main()
