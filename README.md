#  N-1 Dynamic Security Assessment for the Cyprus Transmission System

This project provides a **Python-based Dynamic Security Assessment (DSA)** tool implementing the **N-1 criterion** for a simplified grid version of the **Cyprus Transmission System**.

The simulation is based on **Pyramses**, while an automated analytical report after simulations is exported  through Large Language Models (LLMs).

---

##  Requirements

Before running the tool, install the required Python libraries.

### Core Simulation Libraries
```bash
pip install matplotlib scipy numpy mkl jupyter ipython pyramses

pip install pandas requests matplotlib markdown beautifulsoup4 reportlab
```

Also you 'll need a license from the author of Pyramses (Dr.Petros Aristeidou - apetros@pm.me)

In order to enable the license go to solveroptions.dat and replace with the given license this part:

```bash
$LICENSE        (YOUR LICENSE)     ;
```


# Configuration

All simulation settings can be edited in config.py:

 -Simulation time settings

 -Frequency protection limits

 -LVRT (Low Voltage Ride Through) curves

 -Other system limits

# LLM Report Generation

To automatically generate an analytical report using an LLM based on simulation results:

 1.Open config.py

 2.Locate the LLM configuration section:
```bash
#LLM configuration

api_key = "Your Api key"
model = "Llm model"
```
 3.Insert your API key from:

 https://openrouter.ai/models

 Recommended Model
 
```bash
openai/chatgpt-4o-latest
```

# Execution Instructions

1. Put all the above files in a common folder



2. Run the Simulation

   Navigate to the folder and execute:
```bash
   python main_pyramses.py
```

   Or by double-clicking:

   Run the main_pyramses.py file from your file explorer.(Make sure the working directory is the same of the files)

# Summary

This project allows you to:

 -Simulate N-1 disturbances on a simplified Cyprus transmission grid

 -Evaluate system stability 

 -Analyze LVRT/frequency events

 -Generate automated critical findings using LLMs


 
