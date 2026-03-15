# Task: Generate STRIDE Threat Model

Analyze `workspace/architecture.json` (a system architecture description) using the STRIDE threat modeling methodology.

## STRIDE Categories

- **S**poofing: Can an attacker pretend to be someone/something else?
- **T**ampering: Can an attacker modify data in transit or at rest?
- **R**epudiation: Can actions be performed without traceability?
- **I**nformation Disclosure: Can sensitive data be exposed?
- **D**enial of Service: Can the system be made unavailable?
- **E**levation of Privilege: Can an attacker gain unauthorized access levels?

## Requirements

1. Read `workspace/architecture.json` which describes a microservice system with 6 components, 3 data stores, and external API integrations.
2. For each component, identify applicable STRIDE threats.
3. Generate `workspace/threat_model.json` with:
   - `metadata`: system name, analysis date, methodology
   - `threats`: array of objects, each with `id`, `category` (S/T/R/I/D/E), `component`, `description`, `likelihood` (high/medium/low), `impact` (high/medium/low), `mitigation`
   - `summary`: counts by category and overall risk rating
4. Generate `workspace/threat_report.md` with:
   - Executive summary
   - Architecture overview
   - Threat analysis by component
   - Risk matrix
   - Prioritized mitigation recommendations

## Notes

- All 6 STRIDE categories must be covered.
- All components must be analyzed.
- Each threat must have a specific mitigation.

## Output

Save `workspace/threat_model.json` and `workspace/threat_report.md`.
