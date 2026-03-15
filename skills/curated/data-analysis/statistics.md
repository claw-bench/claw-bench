# Statistical Analysis Skill

## Overview
This skill provides guidance on performing common statistical analyses,
including descriptive statistics, correlation, and data summarization.

## Descriptive Statistics

### Central Tendency
- **Mean**: Sum of values divided by count. Sensitive to outliers.
- **Median**: Middle value when sorted. Robust to outliers.
- **Mode**: Most frequently occurring value(s).

### Python Implementation
```python
import statistics

data = [10, 20, 30, 40, 50]

mean = statistics.mean(data)
median = statistics.median(data)
mode = statistics.mode(data)  # raises StatisticsError if no unique mode
```

### With NumPy
```python
import numpy as np

data = np.array([10, 20, 30, 40, 50])

mean = np.mean(data)
median = np.median(data)
std_dev = np.std(data, ddof=1)  # sample standard deviation
variance = np.var(data, ddof=1)
```

## Measures of Spread

### Standard Deviation and Variance
- **Population std dev**: Use `ddof=0` (divides by N).
- **Sample std dev**: Use `ddof=1` (divides by N-1). Preferred for samples.

```python
import statistics

stdev = statistics.stdev(data)       # sample
pstdev = statistics.pstdev(data)     # population
variance = statistics.variance(data) # sample
```

### Range and Percentiles
```python
import numpy as np

data_range = np.max(data) - np.min(data)
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1  # interquartile range
```

## Correlation

### Pearson Correlation
Measures linear relationship between two variables. Range: [-1, 1].

```python
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])

correlation_matrix = np.corrcoef(x, y)
r = correlation_matrix[0, 1]
```

### Interpretation Guidelines
- |r| > 0.7: Strong correlation
- 0.3 < |r| < 0.7: Moderate correlation
- |r| < 0.3: Weak correlation

## Data Summarization

### Frequency Tables
```python
from collections import Counter

counts = Counter(data)
for value, freq in counts.most_common():
    print(f"{value}: {freq}")
```

### Grouping and Aggregation
```python
import csv
from collections import defaultdict

groups = defaultdict(list)
for row in data:
    groups[row["category"]].append(float(row["value"]))

for category, values in groups.items():
    print(f"{category}: mean={statistics.mean(values):.2f}, n={len(values)}")
```

## Best Practices
- Always check for empty datasets before computing statistics.
- Use sample statistics (ddof=1) unless you have the full population.
- Report precision appropriate to the data (do not over-report decimal places).
- Consider outlier detection (IQR method or z-score) before summarizing.
- When comparing groups, report both central tendency and spread.
