# Data-Driven Email Campaign

You are a marketing automation engineer. Given customer data, email templates, and campaign rules, generate personalized emails for each qualifying customer and produce campaign summary statistics.

## Input Files

- `customers.csv` — Customer database with columns: customer_id, email, first_name, last_name, segment, lifetime_value, last_purchase_date, purchase_count, preferred_category, opted_in
- `templates/` — Directory containing email templates with `{{variable}}` placeholders:
  - `premium_offer.html` — Template for premium/VIP customers
  - `winback.html` — Template for lapsed/churning customers
  - `loyalty_reward.html` — Template for loyal regular customers
  - `welcome_series.html` — Template for new customers
- `rules.toml` — Campaign rules defining segment-to-template mapping, eligibility criteria, A/B test configuration, and variable definitions

## Requirements

### Step 1: Customer Segmentation and Filtering
- Read `customers.csv` and `rules.toml`
- Filter customers based on eligibility rules (must be opted_in=true, and meet segment-specific criteria from rules.toml)
- Assign each eligible customer to the correct template based on their segment

### Step 2: Template Variable Substitution
- For each eligible customer, process the appropriate template
- Replace all `{{variable}}` placeholders with actual customer data and computed values
- Computed variables defined in rules.toml (e.g., discount percentages based on lifetime_value tiers)

### Step 3: A/B Test Variant Generation
- For the segments marked for A/B testing in rules.toml, generate two variants (A and B) per customer
- Variant A uses the default subject line; Variant B uses the alternate subject line from rules.toml
- Assign customers to variants by: customer_id (as integer) modulo 2; even = A, odd = B

### Step 4: Output Generation
Create an `output/` directory in the workspace containing:

1. **Individual email files**: One file per customer named `{customer_id}.html`
   - Contains the fully rendered email HTML with all variables substituted
   - For A/B test segments, use the assigned variant

2. **campaign_summary.json**: A summary file with this structure:
```json
{
  "total_customers": 20,
  "eligible_customers": 15,
  "excluded_customers": 5,
  "segments": {
    "segment_name": {
      "count": 5,
      "template": "template_name.html",
      "ab_test": true
    }
  },
  "ab_test_distribution": {
    "segment_name": {
      "variant_a": 3,
      "variant_b": 2
    }
  },
  "emails_generated": 15
}
```

### Constraints
- Only customers with `opted_in` equal to `true` (case-insensitive) are eligible
- All `{{variable}}` placeholders in templates must be replaced (no raw `{{` should remain in output)
- The campaign_summary.json must accurately reflect counts
- Each generated email file must be valid HTML
