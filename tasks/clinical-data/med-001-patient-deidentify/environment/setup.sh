#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE" "$WORKSPACE/deidentified" "$WORKSPACE/archive"
python3 -c "
import csv, random
random.seed(123)
names = ['John Smith','Jane Doe','Robert Johnson','Maria Garcia','David Lee','Sarah Wilson','Michael Brown','Emily Davis','James Miller','Lisa Anderson']
states = ['CA','NY','TX','FL','IL','PA','OH','GA','NC','MI']
diagnoses = ['Hypertension','Diabetes Type 2','Asthma','Hyperlipidemia','Depression']
header = ['name','dob','ssn','address','state','diagnosis','systolic_bp','diastolic_bp','glucose_mg_dl','cholesterol_mg_dl']
rows = [header]
for i,name in enumerate(names):
    year = random.randint(1955,1995)
    month = random.randint(1,12)
    day = random.randint(1,28)
    dob = f'{year}-{month:02d}-{day:02d}'
    ssn = f'{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}'
    addr = f'{random.randint(100,9999)} {random.choice([\"Main\",\"Oak\",\"Elm\",\"Pine\",\"Cedar\"])} St'
    state = states[i]
    diag = diagnoses[i % len(diagnoses)]
    sbp = random.randint(110,180)
    dbp = random.randint(60,100)
    glucose = random.randint(70,250)
    chol = random.randint(150,300)
    rows.append([name,dob,ssn,addr,state,diag,str(sbp),str(dbp),str(glucose),str(chol)])
with open('$WORKSPACE/patient_records.csv','w',newline='') as f:
    csv.writer(f).writerows(rows)
"
