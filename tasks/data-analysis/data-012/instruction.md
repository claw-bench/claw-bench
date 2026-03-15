# Task: Simple Linear Regression Prediction

You are given a CSV file at `workspace/historical.csv` with columns: `x`, `y` representing a time series with a linear trend.

## Requirements

1. Read `workspace/historical.csv`.
2. Fit a simple linear regression model: `y = slope * x + intercept`.
3. Predict the `y` values for the next 3 `x` values (i.e., if data goes up to x=50, predict for x=51, 52, 53).
4. Write predictions to `workspace/predictions.json` as a list of objects with keys: `x`, `predicted_y` (rounded to 2 decimal places).
5. Write model statistics to `workspace/model.json` with keys:
   - `slope`: rounded to 4 decimal places
   - `intercept`: rounded to 4 decimal places
   - `r_squared`: rounded to 4 decimal places
   - `mse`: mean squared error, rounded to 4 decimal places

## Notes

- Use ordinary least squares (OLS) for fitting.
- You may use standard libraries (statistics, math) or numpy if available, but the task is solvable with pure Python.

## Output

Save `workspace/predictions.json` and `workspace/model.json`.
