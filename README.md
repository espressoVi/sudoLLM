![sudoLLM](data/logo.png)

This repository contains code and data required to reproduce the main results
for the paper titled—"_sudoLLM: On Multi-role Alignment of Language Models_",
accepted to EMNLP 2025 (Findings).  
[:notebook: Paper](https://arxiv.org/abs/2505.14607) | [:email: Contact](mailto:soumadeep.saha97@gmail.com)

## Citation

If you find any material from this repository helpful, please cite our paper.

> [!WARNING]
> Update citation after anthology.

```
@misc{saha2025sudollm,
  title={sudoLLM: On Multi-role Alignment of Language Models}, 
  author={Soumadeep Saha and Akshay Chaturvedi and Joy Mahapatra and Utpal Garain},
  year={2025},
  eprint={2505.14607},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2505.14607}, 
}
```
## Usage

> [!NOTE]
> Tested with ```python 3.13.0```

* Install the requirements:
```
pip install -r requirements.txt
```

* Download the requisite models (e.g., Qwen 2.5 7B). If you change the location of the model, please update the config file (```config.toml```).
```
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir LLM/qwen25-7B-instruct
```

## Data

## Authors / Contributors

* [Soumadeep Saha](https://espressovi.github.io)
* [Akshay Chaturvedi](https://scholar.google.com/citations?user=28DvXUAAAAAJ&hl=en)
* [Joy Mahapatra](https://dblp.org/pid/188/9220.html)
* [Utpal Garain](https://isical.ac.in/~utpal)
