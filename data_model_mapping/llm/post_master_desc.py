import pandas as pd
import os
import re

# Read the master_desc.csv file
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc.csv')
df = pd.read_csv(csv_path)

# Create 'org_tag_description' with the original 'tag_description' if it doesn't already exist
if 'org_tag_description' not in df.columns:
    df['org_tag_description'] = df['tag_description']
else :df['tag_description'] = df['org_tag_description']
# Define replacements
replacements = {
    "CYL ": "CYL.1 ",
    "CYL. ": "CYL.1 ",
    "BOILER ": "BOILER1 ",
    "BOILER_": "BOILER1 ",
    "M/E 1": "M/E",
    "M/E ": "M/E1 ",
    "M/E_": "M/E1 ",
    "M/E(": "M/E1( ",
    "NO.1 T/C": "T/C ",
    "T/C ": "T/C1 ",
    "T/C_": "T/C1 ",
    "01": "1 ",
    "NO.1 G/E_": "G/E_",
    "G/E_": "G/E1 ",
    "TC(": "T/C1( ",
    "SPS_SHAFT": "SPS SHAFT1 ",
    "M/E1 AMBIENT_": "M/E AMBIENT ",
    "G/E H.F.O_FLOW": "G/E1 H.F.O FLOW",
    "G/E LFO USE": "G/E1 LFO USE ",
    "BLR.": "BLR.1 ",
    "A/B FO FLOW": "BLR.1 A/B FO FLOW ",    
    "MP-1100": "CH",
    "MP-1101": "CH",
    "FGSS Fuel discharge temperature": "M/E1 FGSS Fuel discharge temperature",
    "M/E1 L.O INLET_TEMP": "M/E1 T/C1 L.O INLET_TEMP",
    "GE FO OUTLET FLOW": "G/E1 FO OUTLET FLOW",
    "MK-2100 ": "CH ",
    "SPS_PROPELLER THRUST": "SPS PROPELLER1 THRUST",
    "G/E FUEL OIL FLOW": "G/E1 FUEL OIL FLOW",
    "Ge FOCONSUMPTION": "G/E1 FOCONSUMPTION",
    "G/E F.O C/O SYSTEM U.L.S.F.O USE": "G/E1 F.O C/O SYSTEM U.L.S.F.O USE",
    "FWD LFO BK volume": "NO.1 L.F.O BUNKER TK (S) volume",
    "MP-1400 ": "CH ",
    "MP-1401 ": "CH ",
    "TOTAL REVOLUTION": "M/E1 TOTAL REVOLUTION",
    "ESTIMATED ENGINE POWER": "NO.1 Shaft Power + Shaft Generator Power(STBD)",
    ")_TEMP": " PHASE)_TEMP "
}

# Apply replacements to 'tag_description' while keeping 'org_tag_description' unchanged
for old, new in replacements.items():
    df['tag_description'] = df['tag_description'].str.replace(old, new, regex=False)

# Add tp_numbers and td_numbers columns
df['tp_numbers'] = df.apply(lambda row: len(re.findall(r'\d', str(row['thing']) + str(row['property']))), axis=1)
df['td_numbers'] = df['tag_description'].str.count(r'\d')

# Save the updated DataFrame to the original CSV file
df.to_csv(csv_path, index=False)

print(f"Updated DataFrame has been saved to {csv_path}")
