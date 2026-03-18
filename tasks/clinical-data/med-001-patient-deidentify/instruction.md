You are given a CSV file at `workspace/patient_records.csv` containing simulated patient data with protected health information (PHI).

**Your task:**
1. Read the patient records CSV
2. De-identify the data by:
   - Replacing patient names with anonymous IDs (P001, P002, ...)
   - Generalizing dates of birth to age ranges (e.g., "30-39")
   - Removing Social Security Numbers entirely
   - Replacing specific addresses with only state abbreviations
   - Keeping medical data (diagnosis, lab values) intact
3. Write the de-identified data to `workspace/deidentified/patients_clean.csv`
4. Generate aggregate statistics and write to `workspace/deidentified/statistics.json`:
   - Total patient count
   - Age range distribution
   - Diagnosis frequency
   - Average lab values per diagnosis
5. Move the original file to `workspace/archive/original_records.csv.bak`
6. Create `workspace/deidentified/audit_log.txt` recording what was removed/modified
