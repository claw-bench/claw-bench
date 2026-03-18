You are given a CSV file at `workspace/customers.csv` with customer transaction data.

**Your task:**
1. Read the customer data (features: annual_spending, visit_frequency, avg_transaction, loyalty_years)
2. Normalize the features using min-max scaling
3. Apply K-Means clustering with k=3, 4, and 5
4. Determine the optimal k using the elbow method (inertia values)
5. Using the optimal k, assign each customer to a segment
6. Write results to:
   - `workspace/segmentation_results.csv`: original data + segment label column
   - `workspace/analysis.json`:
     ```json
     {
       "optimal_k": 4,
       "inertia_values": {"3": ..., "4": ..., "5": ...},
       "segment_profiles": {
         "0": {"size": 25, "avg_spending": 5000, ...},
         ...
       },
       "segment_names": {"0": "High-Value Loyal", ...}
     }
     ```
7. Create a simple text-based summary at `workspace/report.md`
