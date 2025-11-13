#  N-1 Dynamic Security Assessment for the Cyprus Transmission System

This project provides a **Python-based Dynamic Security Assessment (DSA)** tool implementing the **N-1 criterion** for a simplified representation of the **Cyprus Transmission System**.

The simulation is based on **Pyramses**, while the framework supports reporting, visualization, and automated analysis through Large Language Models (LLMs).

---

##  Requirements

Before running the tool, install the required Python libraries.

### Core Simulation Libraries
```bash
pip install matplotlib scipy numpy mkl jupyter ipython pyramses
```
Also install these libraries

```bash
pip install pandas requests matplotlib markdown beautifulsoup4 reportlab
```

# Configuration

All simulation settings can be edited in config.py:

 -Simulation time settings

 -Frequency protection limits

 -LVRT (Low Voltage Ride Through) curves

 -Other system-level limits

# LLM-Based Report Generation

To automatically generate an analytical report using an LLM based on simulation results:

Open config.py

Locate the LLM configuration section:
