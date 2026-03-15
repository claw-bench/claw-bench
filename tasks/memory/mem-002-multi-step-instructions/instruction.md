# Task: Multi-Step Instruction Following

Execute the following 5 instructions **in order**. Each step depends on the previous one. Record your work in `workspace/steps.txt` by appending one line per step as you complete it.

## Instructions

**Step 1:** Read `workspace/words.txt`. Find the 3rd word on each line and collect them into a list. Write these words (one per line) to `workspace/extracted.txt`.

**Step 2:** Sort the words in `workspace/extracted.txt` alphabetically (case-insensitive). Overwrite `workspace/extracted.txt` with the sorted list. Append the line `STEP 2: sorted extracted.txt` to `workspace/steps.txt`.

**Step 3:** Count the total number of characters (excluding newlines) across all words in the now-sorted `workspace/extracted.txt`. Write just the number to `workspace/char_count.txt`. Append the line `STEP 3: counted N characters` to `workspace/steps.txt` (replace N with the actual count).

**Step 4:** Take the character count from Step 3 and compute its remainder when divided by 7. Write the remainder to `workspace/remainder.txt`. Append the line `STEP 4: remainder is R` to `workspace/steps.txt` (replace R with the actual remainder).

**Step 5:** Create a final summary file `workspace/summary.txt` containing exactly 3 lines:
- Line 1: The first word from the sorted extracted list
- Line 2: The last word from the sorted extracted list
- Line 3: The remainder from Step 4

Append the line `STEP 5: wrote summary.txt` to `workspace/steps.txt`.

## Important

- You must append `STEP 1: extracted third words` to `workspace/steps.txt` after completing Step 1.
- Steps must be completed in order and each recorded in `workspace/steps.txt`.
- All output goes in the `workspace/` directory.
