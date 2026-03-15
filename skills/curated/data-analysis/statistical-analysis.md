# Statistical Analysis Skill

## Overview
This skill covers fundamental statistical methods for summarizing data,
detecting patterns, and drawing conclusions from datasets using Python.

## Descriptive Statistics

```python
import statistics, pandas as pd

data = [12, 15, 18, 22, 25, 30, 35]
mean, median, stdev = statistics.mean(data), statistics.median(data), statistics.stdev(data)

df = pd.read_csv("data.csv")
print(df.describe())  # count, mean, std, min, 25%, 50%, 75%, max
```

## Distribution Analysis

- **Histograms**: Visualize frequency distribution to spot skew or multimodality.
- **Box plots**: Identify quartiles and outliers at a glance.
- **Normality check**: Use `scipy.stats.shapiro` for small samples or
  `scipy.stats.normaltest` for larger datasets.

## Hypothesis Testing

### t-Test for Comparing Two Groups
```python
from scipy import stats

group_a = [23, 25, 28, 30, 32]
group_b = [30, 33, 35, 37, 40]
t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"p-value: {p_value:.4f}")
```
A p-value below 0.05 typically indicates a statistically significant difference.

## Correlation

```python
correlation = df["feature_a"].corr(df["feature_b"])
```
- Values near +1 or -1 indicate strong linear relationships.
- Correlation does not imply causation; always look for confounders.

## Tips
- Always inspect your data visually before computing statistics.
- Check for missing values with `df.isnull().sum()` and decide on imputation or removal.
- Use non-parametric tests (Mann-Whitney U, Kruskal-Wallis) when data is not normally distributed.
- Report confidence intervals alongside point estimates for more informative results.
- Be cautious with small sample sizes; statistical power drops sharply below n=30.
