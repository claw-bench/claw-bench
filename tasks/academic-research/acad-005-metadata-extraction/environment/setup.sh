#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE/papers"

python3 -c "import random; import os; random.seed(42)

papers = [
    {
        'title': 'Deep Learning for Natural Language Processing',
        'authors': ['Alice Smith', 'Bob Johnson'],
        'year': 2018,
        'keywords': ['deep learning', 'NLP', 'neural networks'],
        'abstract': 'This paper explores deep learning techniques applied to natural language processing tasks. We show improvements over traditional methods.',
        'references': [
            'J. Doe, Machine Learning Basics, 2015.',
            'K. Lee, Neural Networks and Applications, 2017.'
        ]
    },
    {
        'title': 'Quantum Computing: An Introduction',
        'authors': ['Carol White'],
        'year': 2020,
        'keywords': ['quantum computing', 'qubits', 'algorithms'],
        'abstract': 'Quantum computing promises to revolutionize computation by using quantum bits. This introduction covers fundamental concepts.',
        'references': [
            'A. Einstein, Quantum Theory, 1925.',
            'R. Feynman, Simulating Physics with Computers, 1982.'
        ]
    },
    {
        'title': 'Advances in Computer Vision',
        'authors': ['David Black', 'Eva Green', 'Frank Brown'],
        'year': 2019,
        'keywords': ['computer vision', 'image recognition', 'convolutional networks'],
        'abstract': 'Recent advances in computer vision have been driven by convolutional neural networks. This survey summarizes key developments.',
        'references': [
            'Y. LeCun, Deep Learning, 2015.',
            'I. Goodfellow, GANs, 2014.',
            'K. He, ResNet, 2016.'
        ]
    },
    {
        'title': 'Blockchain Technology and Applications',
        'authors': ['Grace Hopper'],
        'year': 2021,
        'keywords': ['blockchain', 'distributed ledger', 'cryptocurrency'],
        'abstract': 'Blockchain technology enables secure, decentralized ledgers. This paper discusses applications beyond cryptocurrencies.',
        'references': [
            'S. Nakamoto, Bitcoin: A Peer-to-Peer Electronic Cash System, 2008.',
            'M. Crosby, Blockchain Technology Overview, 2016.'
        ]
    },
    {
        'title': 'Ethics in Artificial Intelligence',
        'authors': ['Helen Clark', 'Ian Wright'],
        'year': 2017,
        'keywords': ['ethics', 'AI', 'machine learning'],
        'abstract': 'As AI systems become more prevalent, ethical considerations are critical. This paper reviews key ethical challenges.',
        'references': [
            'N. Bostrom, Superintelligence, 2014.',
            'T. Winfield, Ethical AI, 2016.'
        ]
    }
]

# Generate 25 papers total by repeating and modifying
for i in range(25):
    p = papers[i % len(papers)].copy()
    p['title'] += f' (Version {i+1})'
    p['year'] += i % 5  # vary year a bit
    filename = f'paper_{i+1:02d}.txt'
    path = os.path.join(os.environ['WORKSPACE'], 'papers', filename)

    # Compose file content
    content = []
    content.append(f"Title: {p['title']}")
    content.append(f"Authors: {'; '.join(p['authors'])}")
    content.append(f"Year: {p['year']}")
    content.append(f"Keywords: {'; '.join(p['keywords'])}")
    content.append("")
    content.append("Abstract:")

    # Abstract may be multiline, split into lines of max 60 chars
    abstract = p['abstract']
    abstract_lines = []
    words = abstract.split()
    line = ''
    for w in words:
        if len(line) + len(w) + 1 <= 60:
            line = (line + ' ' + w).strip()
        else:
            abstract_lines.append(line)
            line = w
    if line:
        abstract_lines.append(line)
    content.extend(abstract_lines)
    content.append("")
    content.append("References:")
    content.extend(p['references'])

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content) + '\n')
"