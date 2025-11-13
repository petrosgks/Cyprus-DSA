
import requests
import pandas as pd
from datetime import datetime
import sys
import os

from process_data import SystemStatus, check_generator_frequency, check_bus_voltage, process_dst_files, load_flow_calc
from config import *

from post_processing import *



def generate_dsa_report(api_key,results_csv_path,descriptions_csv_path,model,output_md_file):
    

    
    import pandas as pd

    def load_data(filepath):
    
        
        metadata = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    metadata.append(line.strip().replace('#', '').strip())  
                elif line.strip() and not line.startswith('\n'):
                    
                    df = pd.read_csv(filepath, comment='#', sep='\t', on_bad_lines='skip')
                    break  

        
        if "Warning Messages" in df.columns:
            df["Warning Messages"] = df["Warning Messages"].str.replace('¶', '<br>► ')  

        
        table_md = df.to_markdown(index=False, tablefmt="pipe")

        
        output = "\n".join(metadata) + "\n\n" + table_md
        return output

    
    

    try:
        results_data = load_data(results_csv_path)
        descriptions_data = load_data(descriptions_csv_path)
        print("\n", results_data)
        
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

    
    prompt = f"""
You are a Python and Markdown expert.

TASK:
Generate a Dynamic Security Assessment (DSA) Markdown report for a power system simulation. The report should match the exact structure and tone of a professional N-1 security assessment report.

You are provided with the following files:
1. `final_results.csv`: This contains the actual N-1 disturbances (DST) that occurred during the simulation, along with their warning messages and system classification (e.g., "Danger of collapse").
2. `Description_of_disturbances.csv`: This provides textual descriptions for all possible disturbances.

Data from final_results.csv:
{results_data}

Data from Description_of_disturbances.csv:
{descriptions_data}

Your job is to:
- Read `final_results.csv` and identify all unique disturbances (e.g., "TRIP LINELN140").
- For each disturbance found in that file, retrieve the corresponding description from `Description_of_disturbances.csv`.
- Group all warning messages per disturbance and display them as bullet points using ► in the "Warning Messages" column.
- Generate the final Markdown report using the exact same structure and formatting as the example below (see template).

Requirements:
- Only include disturbances that are present in `final_results.csv` at the output markdown file you give. Ignore all others.
- Use the section titles, table structure, and tone from the following template.
- The report must be written in valid, well-formatted Markdown.
- Sort the table beggining with the disturbance that is more severe( EMERGENCY STATE goes first Alert state goes) and has the most warning messages

Here is a structural example you must follow (reference only):

-------------
# Dynamic Security Assessment of (N-1) - Technical Report

**Report Date:** 2025-09-26 12:15

## <u>Overview</u>

This report presents the results of the Dynamic Security Assessment (N-1) performed for the Cyprus Transmission System. The assessment focused on analyzing the system's behavior following the loss of a component (transmission line,sychronous generator) by checking for violations regarding voltage and frequency .

**Assessment Key Details:**

*   **Execution Date:** 2025-09-26, 12:15:50<br>
*   **Total Simulation Time:** 159.86 seconds<br>
*   **Total Disturbance(DST) Files Processed:** 184<br>
*   **Distrurbance(DST) Files with Warnings:** 13<br>
*   **Final System Classification:** <span style="color:red">EMERGENCY STATE </span>

## <u>Detailed Results – Incident Analysis</u>

The analysis revealed several incidents causing serious concern for the network's stability. The table below summarizes the most significant findings related to the loss of various transmission lines:

<!-- pagebreak -->

| N-1 Disturbance  | Description of disturbance                            | Warning Messages                                                | Disturbance Classification |
|------------------|-------------------------------------------------------|-----------------------------------------------------------------|----------------------------|
| TRIP LINELN154   | This is an event where line LN154 is tripped at t=1.0 | ► ROCOF of generator G24 exceeds 1.0 Hz/s: 1.753 Hz/s           | <span style="color:red">EMERGENCY STATE </span>|
|                  |                                                       | ► Frequency of generator G24 exceeds collapse limits: 73.845 Hz |                            |
|                  |                                                       | ► ROCOF of generator G25 exceeds 1.0 Hz/s: 1.756 Hz/s           |                            |
|                  |                                                       | ► Frequency of generator G25 exceeds collapse limits: 73.845 Hz |                            |
|                  |                                                       | ► ROCOF of generator G26 exceeds 1.0 Hz/s: 1.762 Hz/s           |                            |
|                  |                                                       | ► Frequency of generator G26 exceeds collapse limits: 73.845 Hz |                            |
| TRIP LINELN147   | This is an event where line LN147 is tripped at t=1.0 | ► ROCOF of generator G21 exceeds 1.0 Hz/s: 1.603 Hz/s           | <span style="color:red">EMERGENCY STATE </span>           |
|                  |                                                       | ► Frequency of generator G21 exceeds collapse limits: 58.712 Hz |                            |
|                  |                                                       | ► ROCOF of generator G22 exceeds 1.0 Hz/s: 1.602 Hz/s           |                            |
|                  |                                                       | ► Frequency of generator G22 exceeds collapse limits: 58.712 Hz |                            |
|                  |                                                       | ► ROCOF of generator G23 exceeds 1.0 Hz/s: 1.532 Hz/s           |                            |
|                  |                                                       | ► Frequency of generator G23 exceeds collapse limits: 58.712 Hz |                            |
| TRIP LINELN137   | This is an event where line LN137 is tripped at t=1.0 | ► ROCOF of generator G09 exceeds 1.0 Hz/s: 2.616 Hz/s           | <span style="color:red">EMERGENCY STATE </span>           |
|                  |                                                       | ► Frequency of generator G09 exceeds collapse limits: 204.357 Hz|                            |
| TRIP LINELN113   | This is an event where line LN113 is tripped at t=1.0 | ► ROCOF of generator G03 exceeds 1.0 Hz/s: 2.356 Hz/s           | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► Frequency of generator G03 exceeds collapse limits: 67.528 Hz |                            |
| TRIP LINELN138   | This is an event where line LN138 is tripped at t=1.0 | ► ROCOF of generator G10 exceeds 1.0 Hz/s: 2.973 Hz/s           | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► Frequency of generator G10 exceeds collapse limits: 52.147 Hz |                            |
| TRIP LINELN139   | This is an event where line LN139 is tripped at t=1.0 | ► ROCOF of generator G11 exceeds 1.0 Hz/s: 2.983 Hz/s           | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► Frequency of generator G11 exceeds collapse limits: 52.111 Hz |                            |
| TRIP LINELN142   | This is an event where line LN142 is tripped at t=1.0 | ► ROCOF of generator G14 exceeds 1.0 Hz/s: 2.67 Hz/s            | <span style="color:red">EMERGENCY STATE </span>           |
|                  |                                                       | ► Frequency of generator G14 exceeds collapse limits: 52.033 Hz |                            |
| TRIP LINELN92    | This is an event where line LN92 is tripped at t=1.0  | ► UVFRT violation on bus BUS48                                  | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► UVFRT violation on bus BUS123                                 |                            |
|                  |                                                       | ► UVFRT violation on bus BUS124                                 |                            |
| TRIP LINELN18    | This is an event where line LN18 is tripped at t=1.0  | ► UVFRT violation on bus BUS21                                  | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► UVFRT violation on bus BUS22                                  |                            |
|                  |                                                       | ► UVFRT violation on bus BUS23                                  |                            |
| TRIP LINELN140   | This is an event where line LN140 is tripped at t=1.0 | ► UVFRT violation on bus BUS98                                  | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► UVFRT violation on bus BUS101                                 |                            |
| TRIP LINELN161   | This is an event where line LN161 is tripped at t=1.0 | ► UVFRT violation on bus BUS122                                 | <span style="color:red">EMERGENCY STATE </span>            |
| TRIP LINELN73    | This is an event where line LN73 is tripped at t=1.0  | ► UVFRT violation on bus BUS56                                  | <span style="color:red">EMERGENCY STATE </span>           |
| TRIP LINELN69    | This is an event where line LN69 is tripped at t=1.0  | ► UVFRT violation on bus BUS54                                  | <span style="color:red">EMERGENCY STATE </span>            |
|                  |                                                       | ► UVFRT violation on bus BUS55                                  |                            |

<!-- pagebreak -->


## <u>Key Findings and Issues</u>

(In this section you must provide an overview about the key findings and describe the issues emerged from the N-1 contigencies. Below i provide a sample to see how the structure is. However it's your choice to make your own headings and make you own review for this section)

**High ROCOF Values:** In several disturbance cases, the Rate of Change of Frequency (ROCOF) exceeded the 1.0 Hz/s limit significantly. This indicates that the power system experiences too rapid a frequency drop, threatening generator tripping and system collapse.

**Frequency Limit Violations:** Multiple generators experienced frequency excursions beyond emergency limits (e.g., 204.357 Hz), a clear violation that prompts urgent reactive measures and possible equipment damage or disconnection.

**UVFRT (Undervoltage Fault Ride-Through) Violations:** Numerous UVFRT events were detected, particularly on buses 21, 22, 23, 48, 98, 101, 122, 123 and 124. This highlights vulnerabilities in the system's ability to withstand undervoltage during disturbances.

<!-- pagebreak -->

## <u>Recommendations</u>

**Stability Enhancement Measures:**

* Implement emergency control schemes including under-frequency load shedding (UFLS) and fast generator tripping logic.
* Deploy advanced dynamic reactive support through SVCs and STATCOMs to improve voltage stabilizing response.

**Corrective Actions for ROCOF Issues:**

* Reconfigure generator protection settings to tolerate higher ROCOF values where technically feasible.
* Enhance inertia response through integration of battery storage and synchronous condensers.

**Corrective Actions for Frequency Violations:**

* Introduce tighter frequency controls on primary and secondary reserves.
* Coordinate with generation units to limit setpoint violations and sudden disconnections.

**Mitigation of UVFRT Violations:**

* Improve ride-through capabilities of inverter-based resources according to regional UVFRT standards.
* Implement grid-forming converter technologies to support voltage during fault conditions.
* Conduct relay coordination studies to ensure proper UV tripping logic.

<!-- pagebreak -->

## <u>Conclusions</u>

This assessment reveals a significant vulnerability of the network to disturbances. The final classification <span style="color:red">EMERGENCY STATE </span> emphasizes the urgent need for measures to enhance system security and reliability. Implementation of the proposed recommendations is critical to avoid serious operational outages.
-------------

The final output should include:
- Simulation metadata (execution time, number of cases, etc.) which you will take them from final_results.csv. These data are stated at the lines 2-6 of the csv file.
- A results table showing only the disturbances found in `final_results.csv`
- Technical findings and recommendations
- A conclusion section
- PLEASE FOLLOW THE EXACT FORM OF THE STRUCTURAL EXAMPLE THAT I GAVE YOU.
- Add specific corrective actions and mitigation methods for each type of disturbance (e.g., Under Voltage Fault Ride Through (UVFRT) violation,Overvoltage, overfrequency,underfrequency, ROCOF), based on the nature of the warning messages present in the final results.
- Give me a ready output md file ready to be converted to pdf file with pandoc
- Don't write any commas or any symbols at the beggining before the  headings of the report or at the end of the report of markdown output report. I want a clear structure to convert it after to pdf file with pandoc
- If Final System Classification is : EMERGENCY STATE  write it with red letters. If it's Alert state write with yellow letters and if it's Normal operation write it with green letters. 

IMPORTANT:
Output only the final `.md` content — do not include explanations or comments. Just produce the clean Markdown report
"""

    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000
    }

    

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        markdown_content = response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"🔴 Σφάλμα LLM: {str(e)}")

    
    try:
        with open(output_md_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        
        
        return output_md_file
    except Exception as e:
        raise Exception(f"Saving error {str(e)}")
    
def clean_markdown_file(file_path: str):
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    start = text.find("```markdown")
    end = text.rfind("```")

    if start != -1 and end != -1 and end > start:
        cleaned_text = text[start + len("```markdown"):end].strip()
    else:
        cleaned_text = text.strip()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)









