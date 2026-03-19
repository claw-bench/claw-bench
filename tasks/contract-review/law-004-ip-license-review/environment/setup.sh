#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
random.seed(42)

# Construct a synthetic license agreement text with various clauses
clauses = [
    "Permission is hereby granted, free of charge, to any person obtaining a copy of this software to use it for commercial purposes.",
    "Modification of the software source code is allowed under the terms of this license.",
    "Distribution of the software is permitted provided that the original copyright notice is included.",
    "Sublicensing rights are not granted under this license.",
    "Patent rights are granted to use any patents held by the licensor that are necessary to use the software.",
    "Attribution to the original author must be given in all copies or substantial portions of the software.",
    "Derivative works must be licensed under the same terms as the original (share alike).",
    "Use of the licensor's trademarks is prohibited.",
    "The licensor disclaims all liability for damages arising from the use of the software.",
    "No warranty is provided with this software.",
    "Commercial use is strictly prohibited.",
    "You may not modify the software in any way.",
    "Redistribution is allowed only in source code form.",
    "Sublicense rights are granted to third parties.",
    "Patent use is not included in this license.",
    "Attribution is optional.",
    "No share alike requirement applies.",
    "Trademark use requires prior written permission.",
    "Liability is limited to the amount paid for the software.",
    "Use of the software is subject to the terms stated herein.",
]

# Randomly select 20 clauses to simulate a license agreement
selected_clauses = random.sample(clauses, 20)

# Join with double newlines to simulate paragraphs
license_text = "\n\n".join(selected_clauses)

with open(f"{WORKSPACE}/license_agreement.txt", "w", encoding="utf-8") as f:
    f.write(license_text)
EOF
