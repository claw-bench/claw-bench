#!/usr/bin/env bash
# Oracle solution for mem-005-long-document-summarization
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/summary.txt" << 'EOF'
The Meridian Solar Energy Project (MSEP) is a large-scale photovoltaic installation planned for Clearwater Valley, Nevada.
The project aims to deliver 125 megawatts (MW) of clean solar energy to the regional power grid, serving approximately 37,500 households.
The total project budget is estimated at $47.3 million, with construction expected to begin in Q2 2026.
Full operational capacity is targeted for Q4 2027, with a Commercial Operation Date of November 2027.
The installation will use approximately 312,500 monocrystalline silicon panels on single-axis tracking systems across 640 acres.
A 25 MW / 100 MWh battery energy storage system using lithium iron phosphate chemistry will provide grid services.
The environmental assessment found manageable impacts, with mitigation measures for desert tortoise and migratory birds.
The project has secured a 20-year Power Purchase Agreement with Sierra Nevada Power Cooperative at $0.038 per kWh.
Key financial metrics include a 12.4% internal rate of return, 6.8-year payback period, and $18.7 million net present value.
Eight key stakeholders are involved, including the Nevada Energy Commission, Bureau of Land Management, and TechSolar Inc. as the primary EPC contractor.
EOF

cat > "$WORKSPACE/key_points.txt" << 'EOF'
STAKEHOLDERS:
- Nevada Energy Commission (NEC) - regulatory oversight and permitting
- Bureau of Land Management (BLM) - environmental review and right-of-way grant
- Clearwater Valley Municipal Authority (CVMA) - local government zoning and water supply
- Sierra Nevada Power Cooperative (SNPC) - power purchaser under 20-year PPA
- TechSolar Inc. - primary EPC contractor with 3.2 GW experience
- Desert Conservation Alliance (DCA) - environmental advocacy group
- Clearwater Valley Community Coalition (CVCC) - local community group
- First Solar Finance LLC - lead financial institution for debt financing

RISKS:
- R1: Panel degradation at approximately 0.5% per year (LOW)
- R2: Inverter failure with 10-year MTBF, mitigated by N+2 redundancy (MEDIUM)
- R3: Battery degradation retaining 80% capacity after 6,000 cycles (LOW)
- R4: Grid curtailment of 2-5% annually during high solar periods (MEDIUM)
- R5: Extreme weather including dust storms and heat events (LOW)
- R6: Water availability in over-appropriated groundwater basin (MEDIUM)
- R7: Desert tortoise encounters during construction (LOW)
- R8: Supply chain disruption for solar panels (MEDIUM)
- R9: Interest rate fluctuation affecting 5.2% debt rate (MEDIUM)
- R10: Policy changes to federal tax credits (LOW)
- R11: BLM permitting delays averaging 14 months (MEDIUM)
- R12: Interconnection queue and grid upgrade requirements (LOW)

MILESTONES:
- M1: Final Environmental Approval - March 2026
- M2: Construction Start - June 2026
- M3: Foundation and Racking Installation - September 2026
- M4: Panel Installation Complete - March 2027
- M5: Inverter and Electrical Commissioning - June 2027
- M6: Grid Interconnection Energization - August 2027
- M7: Battery Storage Commissioning - September 2027
- M8: Commercial Operation Date (COD) - November 2027

METRICS:
- Total capacity: 125 MW serving 37,500 households
- Total budget: $47.3 million
- Site area: 640 acres at 2,340 feet elevation
- Solar irradiance: 6.2 kWh/m2/day with 292 clear days per year
- Panel count: 312,500 monocrystalline silicon panels at 400 Wp each
- Panel efficiency: 21.3% under Standard Test Conditions
- Battery storage: 25 MW / 100 MWh with 92.5% round-trip efficiency
- PPA rate: $0.038 per kWh escalating 1.5% annually for 20 years
- LCOE: $0.032 per kWh
- IRR: 12.4% with 6.8-year payback period
- NPV: $18.7 million at 8% discount rate
- Annual water consumption: 12.5 million gallons
EOF

echo "Solution written to $WORKSPACE/"
