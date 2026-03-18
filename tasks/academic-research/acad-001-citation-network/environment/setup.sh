#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
cat > "$WORKSPACE/references.bib" << 'BIBEOF'
@article{smith2020deep,
  title={Deep Learning for Natural Language Processing},
  author={Smith, John and Doe, Jane},
  journal={Journal of AI Research},
  year={2020},
  crossref={jones2018attention,brown2019transformers}
}

@article{jones2018attention,
  title={Attention Mechanisms in Neural Networks},
  author={Jones, Robert},
  journal={Neural Computing},
  year={2018},
  crossref={vaswani2017attention}
}

@article{brown2019transformers,
  title={Transformer Architectures: A Survey},
  author={Brown, Alice},
  journal={ML Review},
  year={2019},
  crossref={vaswani2017attention,jones2018attention}
}

@article{vaswani2017attention,
  title={Attention Is All You Need},
  author={Vaswani, Ashish and others},
  journal={NeurIPS},
  year={2017},
  crossref={}
}

@article{lee2021bert,
  title={BERT and Beyond: Pre-training Methods},
  author={Lee, David},
  journal={Computational Linguistics},
  year={2021},
  crossref={smith2020deep,vaswani2017attention,brown2019transformers}
}

@article{garcia2020rl,
  title={Reinforcement Learning in Robotics},
  author={Garcia, Maria},
  journal={Robotics Journal},
  year={2020},
  crossref={silver2016alphago}
}

@article{silver2016alphago,
  title={Mastering the Game of Go with Deep RL},
  author={Silver, David and others},
  journal={Nature},
  year={2016},
  crossref={}
}

@article{wilson2021federated,
  title={Federated Learning: Challenges and Solutions},
  author={Wilson, Sarah},
  journal={Distributed Computing},
  year={2021},
  crossref={smith2020deep,chen2019privacy}
}

@article{chen2019privacy,
  title={Privacy-Preserving Machine Learning},
  author={Chen, Wei},
  journal={Security in AI},
  year={2019},
  crossref={silver2016alphago}
}

@article{kim2022gpt,
  title={GPT Models and Few-Shot Learning},
  author={Kim, Soo},
  journal={AI Advances},
  year={2022},
  crossref={brown2019transformers,vaswani2017attention,lee2021bert,smith2020deep}
}

@article{patel2020cv,
  title={Computer Vision with Convolutional Networks},
  author={Patel, Raj},
  journal={Vision Computing},
  year={2020},
  crossref={he2016resnet}
}

@article{he2016resnet,
  title={Deep Residual Learning for Image Recognition},
  author={He, Kaiming and others},
  journal={CVPR},
  year={2016},
  crossref={}
}

@article{zhang2021multimodal,
  title={Multimodal Learning: Vision and Language},
  author={Zhang, Li},
  journal={Multimodal AI},
  year={2021},
  crossref={vaswani2017attention,he2016resnet,smith2020deep}
}

@article{taylor2020ethics,
  title={Ethics in Artificial Intelligence},
  author={Taylor, Emma},
  journal={AI Ethics Review},
  year={2020},
  crossref={}
}

@article{moore2021explainable,
  title={Explainable AI: Methods and Applications},
  author={Moore, James},
  journal={XAI Journal},
  year={2021},
  crossref={taylor2020ethics,smith2020deep}
}

@article{clark2022diffusion,
  title={Diffusion Models for Image Generation},
  author={Clark, Robert},
  journal={Generative AI},
  year={2022},
  crossref={he2016resnet,vaswani2017attention}
}

@article{adams2021graph,
  title={Graph Neural Networks: A Comprehensive Survey},
  author={Adams, Lisa},
  journal={Graph ML},
  year={2021},
  crossref={jones2018attention,vaswani2017attention}
}

@article{white2022llm,
  title={Large Language Models: Scaling Laws},
  author={White, Tom},
  journal={Scaling AI},
  year={2022},
  crossref={kim2022gpt,lee2021bert,vaswani2017attention,brown2019transformers}
}

@article{harris2020automl,
  title={AutoML: Automated Machine Learning Pipelines},
  author={Harris, Nicole},
  journal={AutoML Journal},
  year={2020},
  crossref={smith2020deep}
}

@article{young2023agents,
  title={AI Agents: Autonomous Decision Making},
  author={Young, Kevin},
  journal={Agent Systems},
  year={2023},
  crossref={kim2022gpt,garcia2020rl,silver2016alphago,lee2021bert}
}
BIBEOF
