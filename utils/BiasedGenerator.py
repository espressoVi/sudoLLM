#!/bin/python3
import re
import torch
import toml
import json
import os
import accelerate
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.GenerateSecrets import Secrets
import numpy as np

config = toml.load("config.toml")


class BiasedGeneration:
    """ Base LLM class implements inference """
    def __init__(self, name):
        self.name = name
        self.llm_path = config['SLMs'][name]
        self.loaded = False
        self.load_tokenizer()
        self.secrets = self._load_bias()
        self._init_config()

    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_path, trust_remote_code = True)
        self.tokenizer.unk_token = "<notrequired>" 
        self.tokenizer.sep_token = "<notrequired>"
        self.tokenizer.pad_token = "<notrequired>"
        self.tokenizer.cls_token = "<notrequired>"
        self.tokenizer.mask_token = "<notrequired>"

    def load_model(self):
        if self.loaded:
            return
        self.model = AutoModelForCausalLM.from_pretrained(
                    self.llm_path,
                    torch_dtype = torch.bfloat16,
                    device_map = "auto",
                    trust_remote_code = True,
                )
        self.loaded = True

    def _init_config(self):
        """ Inititalize generation config. """
        self.generation_config = transformers.GenerationConfig(
                max_new_tokens = config['SLMs']['gen_config']['max_new'],
                temperature=config['SLMs']['gen_config']['temperature'],
                top_p = None,
                do_sample = True,
                num_return_sequences = config['SLMs']['gen_config']['seq_num'],
                pad_token_id = self.tokenizer.eos_token_id,
                eos_token_id = self.tokenizer.eos_token_id,
                sequence_bias = self.secrets["alice"],
                renormalize_logits = True,
                return_dict_in_generate = True,
                output_scores = True,
                output_logits = True,
        )

    def _load_bias(self):
        """ 
        Read the token IDs and initialize the bias array. 
        Returns:
            Dict[str, Dict[tuple[int], float]]
        example:
            {(100,): -10.0, (200,): -10.0} -> token 100, 200 will have bias -10.
        """
        bias = config['SLMs']['gen_config']['bias']
        secret_path = os.path.join(self.llm_path, config['files']['secrets'])
        config_path = os.path.join(self.llm_path, config['files']['config'])
        if not os.path.exists(secret_path):
            Secrets(self.name).create_secrets()
        with open(secret_path, "r") as f:
            secret_toks = json.load(f)
        with open(config_path, "r") as f:
            embedding_size = json.load(f)['vocab_size']
        alice = {(val,):bias for _, val in secret_toks["alice"].items()}
        bob = {(val,):bias for _, val in secret_toks["bob"].items()}
        alice_mask = torch.zeros(embedding_size, dtype = torch.int32)
        bob_mask = torch.zeros(embedding_size, dtype = torch.int32)
        for i in range(embedding_size):
            alice_mask[i] = 1 if (i,) in alice else 0
            bob_mask[i] = 1 if (i,) in bob else 0
        return {
                "alice":alice,
                "alice_mask":alice_mask,
                "bob":bob,
                "bob_mask":bob_mask,
        }

    def __call__(self, prompt:list[dict], name) -> list[str]:
        """ 
        Run inference and returns completions. The prompt must be in
        the following format:

        prompt = [
              {"role": "system", "content": You are a helpful AI assistant...},
              {"role": "user", "content": prompt},
        ]
        -------------------
        Args:
            list[dict] : As described above.
        Returns:
            list[str]: Completion by SLM.
        """
        assert name in [None, "alice", "bob"]
        self.generation_config.sequence_bias = None if name is None else self.secrets[name]
        self.load_model()
        torch.cuda.empty_cache()
        self.model.eval()
        # The following two lines makes sure that the prompt is passed in
        # the assistant role, i.e., the assistant has already said
        # "Re-written input: ". Remove the end of turn token.
        prompt = self.tokenizer.apply_chat_template(prompt, tokenize = False).rstrip()
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")[:,:-1]
        input_token_length = len(inputs[0])
        with torch.inference_mode():
            results = self.model.generate(
                input_ids = inputs.to("cuda"),
                attention_mask = torch.ones_like(inputs).to("cuda"),
                generation_config = self.generation_config,
            )
        probabilities = self.calculate_probabilities(
            torch.stack(results.logits).cpu(),
            results.sequences,
            input_token_length,
            name,
        )
        lengths = [
            len(result[input_token_length:]) for result in results.sequences
        ]
        completions = [
            self.tokenizer.decode(completion, skip_special_tokens=False) 
            for completion in results.sequences
        ]
        completions = [
            re.findall(r'<\|[^\|]+\|>([^<]+)', completion)[-1].strip() 
            for completion in completions
        ]
        results = []
        for completion in completions:
            if match := re.search(config['prompts']['rephrase_prefill'], completion):
                results.append(completion[match.end():].strip())
            else:
                results.append(completion)
        return results, probabilities, lengths
    
    def calculate_probabilities(self, logits, sequences, input_len, name):
        if name is None:
            return [0.5]*logits.shape[1]
        K = config['SLMs']['gen_config']['bias']
        results = []
        other = "alice" if name == "bob" else "bob"
        for logit, sequence in zip(logits.permute(1, 0, 2), sequences):
            prob_name, prob_other = 0, 0
            for token, logt in zip(sequence[input_len:], logit):
                token = int(token.detach().cpu().item())
                score = logt + K*self.secrets[f"{name}_mask"]
                score_other = logt + K*self.secrets[f"{other}_mask"]
                prob_name += torch.log_softmax(score, -1)[token].item()
                prob_other += torch.log_softmax(score_other, -1)[token].item()
            probability = (np.exp(prob_name)/(np.exp(prob_name) + np.exp(prob_other))).item()
            results.append(probability)
        return results
