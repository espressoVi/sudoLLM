# Data for sudoLLM: On Multi-role Alignment of Language Models

All data and artifacts to reproduce results from the paper can be found [here]().
This file contains instructions and explanations for the various files.

## Explanation

Each section of the paper that has associated data corresponds to a folder, and
all data pertaining to the section is present in the folder.
```
data
├── README.md                                                                   # This file
├── Section 3.3
│   ├── bias_vocab_list.json                                                    # The vocabulary list (rare, common) described in Section 3.3 and Appendix C.
│   ├── llama31_8B_secrets.json                                                 # Vocabulary partition of each model.
│   ├── ...
│   └── qwen_25_7B_secrets.json
├── Section 4.1
│   ├── data
│   │   ├── MMLU_samples.json                                                   # The 3 sets of MMLU samples used to report results.
│   │   └── ...
│   ├── outputs
│   │   ├── embeddings_text_embedding_3_large                                   # Embeddings for rephrased queries used for cossim calculation (truncated for size restriction 200MB max).
│   │   ├── MMLU_o1_responses                                                   # Answers given by OpenAI o1 to MMLU queries
│   │   └── MMLU_rephrased_slm_responses                                        # Different versions of rephrased queries (BQ) by different models.
│   │       ├── MMLU_rephrased_llama_3B.json
│   │       ├── ...
│   │       └── MMLU_rephrased_qwen_7B_split_3.json
│   └── prompts
│       ├── MMLU_o1_query                                                       # Prompts used to generate queries from OpenAI o1.
│       │   ├── mmlu_answer_prompts_llama_3B.jsonl
│       │   ├── ...
│       │   └── mmlu_answer_prompts_qwen_7B_split_3.jsonl
│       ├── MMLU_rephrase                                                       # Prompts used to generate BQ.
│       │   └── ...
│       └── prompt.txt                                                          # Base prompt file to generate MMLU queries.
├── Section 4.2
│   ├── Table 2                                                                 # Data for Table 2 (i.e., Alignment performance)
│   │   ├── data
│   │   │   ├── eval_source.json                                                # Evaluation dataset.
│   │   │   ├── Finetune
│   │   │   │   ├── BFT.jsonl                                                   # BFT - Training dataset in ChatML format. Contains rephrased queries by Alice, Bob.
│   │   │   │   └── VFT.jsonl                                                   # VFT - Training dataset in ChatML format. Contains original queries by Alice, Bob. 
│   │   │   └── train_source.json                                               # Training dataset source (used to create BFT, VFT datasets).
│   │   ├── outputs
│   │   │   ├── BFT
│   │   │   │   ├── ...
│   │   │   │   ├── gpt4o.json                                                  # Outputs from BFT model
│   │   │   │   └── gpt4o_refusals.json                                         # Corresponding refusal output from Deepseek V3.
│   │   │   ├── Inst
│   │   │   │   ├── ...
│   │   │   │   ├── gpt4o.json                                                  # Outputs from Inst. model
│   │   │   │   └── gpt4o_refusals.json                                         # Corresponding refusal output from Deepseek V3.
│   │   │   ├── SLM_rephrased_queries                                           # Alice, Bob rephrased versions of train and test datasets.
│   │   │   └── VFT
│   │   │       ├── ...
│   │   │       ├── gpt4o.json                                                  # Outputs from VFT model
│   │   │       └── gpt4o_refusals.json                                         # Corresponding refusal output from Deepseek V3.
│   │   └── prompts
│   │       ├── rephrasing                                                      # Prompts used to generate BQ for train and eval sets.
│   │       ├── system_prompts                                                  # System prompts for refusal, VFT, Inst., and BFT.
│   │       └── templates                                                       # Prompts for various tasks, e.g., MMLU, LegalBench, etc.
│   │           ├── ...
│   │           └── triviaqa.txt                                                # e.g., prompt for TriviaQA task.
│   └── Table 3
│       ├── data
│       │   └── quality_table_3.json                                            # Evaluation set for results in Table 3.
│       └── outputs                                                             # Evaluation output from Inst., VFT, BFT (Table 3).
│           ├── ...
│           └── vft-gpt-4o.json
└─── Section 4.3
     ├── data
     │   ├── attack.json                                                        # Attack evaluation dataset.
     │   └── biased.json                                                        # Biased version of attack evaluation dataset.
     ├── outputs
     │   ├── attack
     │   │   ├── ...
     │   │   ├── gpt-4o-bft_alice.json                                          # Attack variation output (for result in Discussion Section) 
     │   │   ├── gpt-4o-bft_alice_refusals.json                                 # Corresponding refusal evaluation.
     │   │   ├── gpt-4o-bft.json                                                # Output of model under attack.
     │   │   ├── gpt-4o-bft_refusals.json                                       # Corresponding refusal evaluation result (Deepseek V3).
     │   │   ├── ...
     │   │   └── gpt-4o-vft_refusals.json
     │   └── prefix                                                             # Generated attack prefixes.
     │       ├── ...
     │       └── gpt-4o-vft.json
     └── prompts                                                                # Prompts for attack (same as Section 4.2)
         ├── ...
         └── system_safety.txt
```
