#!/bin/python3
import os, sys, getopt
import toml
import json
from utils.BiasedGenerator import BiasedGeneration
from tqdm import tqdm
from copy import deepcopy

config = toml.load("config.toml")

def sample(user_query, user, slm):
    prompt = [{"role": "system", "content": "You are a helpful assistant whose job is to paraphrase user queries. Given user input, rephrase the whole input including any provided context while being accurate and as semantically close as possible. Do not produce any extra text and DO NOT ANSWER, THE QUERY JUST REPHRASE THE INPUT. Ensure that you avoid providing a direct answer. Following are a few examples.\n\nInput: What is the atomic number of sodium?\nRe-written input: What is sodium's atomic number?\n\nInput: In the landmark case \"Smith v. Johnson,\" decided by the Supreme Court in 2022, the issue at hand was whether the search of Smith's vehicle, conducted without a warrant, violated his Fourth Amendment rights. Smith was pulled over for a minor traffic violation, and during the stop, the officer conducted a search of the vehicle's trunk, where illegal substances were found. Smith argued that there was no probable cause or exigent circumstances to justify the search, while the state contended that the search was permissible under the automobile exception to the warrant requirement. The Court, in its decision, emphasized the importance of balancing individual privacy rights with law enforcement interests. How did the Supreme Court justify its decision regarding the applicability of the automobile exception in this case, and what criteria did it establish for future cases involving vehicular searches without a warrant?\nRe-written input: In the landmark Supreme Court case \"Smith v. Johnson\" from 2022, the critical question was whether the warrantless search of Smith's vehicle violated his Fourth Amendment rights. After a minor traffic stop, the officer searched the trunk and found illegal substances. Smith claimed there was no probable cause or exigent circumstance, whereas the state argued the search fell under the automobile exception to the warrant requirement. The Court highlighted the need to balance privacy rights with law enforcement interests. How did the Supreme Court justify its decision on the automobile exception's applicability, and what criteria did it outline for future warrantless vehicular searches?\n\nInput: In 2023, a major tech company developed an AI capable of making autonomous healthcare decisions for patients. While the AI demonstrated high accuracy in diagnosing and recommending treatments, there were concerns about accountability and transparency. Critics argued that relying on AI could lead to ethical dilemmas if the technology made errors. How did the company address these ethical concerns, and what measures did it propose to ensure the responsible use of AI in healthcare?\nRe-written input: In 2023, a prominent tech company created an AI system designed to make independent healthcare decisions for patients. Although the AI showed high accuracy in diagnosing and suggesting treatments, there were worries about accountability and transparency. Critics pointed out potential ethical issues if the AI made mistakes. How did the company respond to these ethical concerns, and what actions did it propose to guarantee responsible AI use in healthcare?" },
              {"role": "user", "content": user_query, },
              {"role": "assistant", "content": "Re-written input: " }
    ]
    seq, _, _ = slm(prompt, user)
    return seq

def main(input_file, output_file, users = ["alice", "bob"], llm_name = "qwen_7B"):
    llm = BiasedGeneration(llm_name)
    with open(input_file, "r") as f:
        prompts = json.load(f)
    rephrased = {}
    for user in users:
        for key, values in tqdm(prompts.items()):
            res = deepcopy(values)
            sequences, prob, length = llm(values["prompt"], user)
            res["user"] = str(user)
            res["rephrased_question"] = sequences[-1]
            res["sequence_prob"] = prob[-1]
            res["sequence_len"] = length[-1]
            rephrased[f"{key}_{user}"] = res
    with open(output_file, "w") as f:
        json.dump(rephrased, f, indent = 4)

def parse_arguments():
    with open("./utils/help_string.txt", "r") as f:
        help_string = f.read().rstrip()
    mode, input_file, output_file, slm = "sample", None, None, "qwen_7B"
    argumentList = sys.argv[1:]
    long_options, options = ["help", "mode=", "input=", "output=", "slm="], "hm:i:o:s:"
    arguments, values = getopt.getopt(argumentList, options, long_options)
    for currentArgument, currentValue in arguments:
        match currentArgument:
            case "-h" | "--help":
                print(help_string); return
            case "-m" | "--mode":
                if currentValue in ["sample", "file"]: mode = currentValue
                else:
                    print(help_string)
                    raise ValueError("Invalid Input")
            case "-i" | "--input":
                input_file = currentValue
            case "-o" | "--output":
                output_file = currentValue
            case "-s" | "--slm":
                if currentValue in ["llama_3B", "llama_8B", "qwen_3B", "qwen_7B"]:
                    slm = currentValue
                else:
                    print(help_string)
                    raise ValueError("Invalid Input")
            case _:
                print(help_string)
                raise ValueError("Invalid Input")
    if input_file is None:
        print(help_string)
        raise ValueError("Invalid Input")
    if mode == "sample":
        slm = BiasedGeneration(slm)
        print(f"Alice: {sample(input_file, 'alice', slm)}")
        print(f"Bob: {sample(input_file, 'bob', slm)}")
    else:
        if output_file is None:print(help_strint);raise ValueError("Invalid Input")
        main(input_file, output_file, llm_name = slm)

if __name__ == "__main__":
    parse_arguments()
