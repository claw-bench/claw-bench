# Task: Word Frequency Count

You are given a text file at `workspace/article.txt`. Count the frequency of each word and produce a sorted CSV report.

## Requirements

1. Read `workspace/article.txt`.
2. Count the frequency of each word (case-insensitive).
3. Strip punctuation from words before counting (periods, commas, semicolons, colons, exclamation marks, question marks, parentheses, quotes, hyphens).
4. Produce a CSV file with two columns: `word` and `count`.
5. Sort the rows by `count` in descending order. For words with the same count, sort alphabetically (ascending).
6. All words should be lowercase in the output.
7. Write the result to `workspace/frequencies.csv`.

## Example

Given this text:

```
The cat sat on the mat. The cat was happy.
```

The output CSV should be:

```
word,count
the,3
cat,2
happy,1
mat,1
on,1
sat,1
was,1
```

## Output

Save the CSV to `workspace/frequencies.csv`.
