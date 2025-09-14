import toml
import numpy as np
import json
import os
from transformers import AutoTokenizer

config = toml.load("config.toml")


class Secrets:
    """
    Class that implements vocabulary partitioning.
    """
    def __init__(self, lm):
        self.lm_path = config['SLMs'][lm]
        self.word_list = self._read_json(config["files"]["word_list"])
        self.tokenizer = AutoTokenizer.from_pretrained(self.lm_path, trust_remote_code = True)
        self.tokenizer.unk_token = "<notrequired>" 
        self.tokenizer.sep_token = "<notrequired>"
        self.tokenizer.pad_token = "<notrequired>"
        self.tokenizer.cls_token = "<notrequired>"
        self.tokenizer.mask_token = "<notrequired>"

    def create_secrets(self):
        """
        Calls _create_secrets if secrets not created.
        """
        secrets_path = os.path.join(self.lm_path, config["files"]["secrets"])
        if os.path.exists(secrets_path):
            return
        tokenizer_path = os.path.join(
                self.lm_path,
                config["files"]["tokenizer"]
        )
        secrets = self._create_secrets()
        with open(secrets_path, "w") as f:
            json.dump(secrets, f, indent=4)
        return

    def _create_secrets(self):
        """
        Creates a random partition of appropriately chosen vocabulary tokens.
        """
        common_tokens = set()
        for word in self.word_list["common"]:
            tokens = self.tokenizer.tokenize(f" {word}")
            tokens += self.tokenizer.tokenize(word)
            word = self._capitalize(word)
            tokens += self.tokenizer.tokenize(f" {word}")
            tokens += self.tokenizer.tokenize(word)
            common_tokens.update(tokens)
        usable_tokens = set()
        for word in self.word_list["rare"]:
            tokens = self.tokenizer.tokenize(f" {word}")
            tokens += self.tokenizer.tokenize(word)
            word = self._capitalize(word)
            tokens += self.tokenizer.tokenize(f" {word}")
            tokens += self.tokenizer.tokenize(word)
            usable_tokens.update(tokens)
        usable_tokens = list(usable_tokens - common_tokens)
        idx = set(
                np.random.choice(
                        len(usable_tokens),
                        len(usable_tokens)//2,
                        replace=False
                ).tolist()
        )
        alice, bob = {}, {}
        for i, token in enumerate(usable_tokens):
            tok_id = self.tokenizer.convert_tokens_to_ids([token])[0]
            if i in idx:
                alice[token] = tok_id
            else:
                bob[token] = tok_id
        result = {
                "alice":alice,
                "bob":bob,
        }
        return result

    @staticmethod
    def _read_json(path):
        with open(path, "r") as f:
            ret = json.load(f)
        return ret

    @staticmethod
    def _capitalize(word):
        return word[0].upper()+word[1:]
