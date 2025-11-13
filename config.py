
#simulation parameters

dyn_data = 'dynfinalP_Q.dat'
loadflow_data = 'loadflow_pfc_output.dat'
solveroptions= 'solveroptions.dat'
number_of_processors=6
t_simulation=60.00
t_dst = 1.000                           #time where the disturbances are occured

#LLM configuration 

api_key = "YOUR_API_KEY_HERE"
model="openai/chatgpt-4o-latest"
results_csv_path = "final_results.csv"
descriptions_csv_path= "Description_of_disturbances.csv"
output_md_file= "dsa_report.md"



#pfc_data_files

exe_path = "pfc.exe"           
commands_file = "pfc_commands.txt" 




# List of excluded DST files 
excluded_files = ["TRIP LINELN161.dst",
                  "TRIP LINELN137.dst",
                  "TRIP LINELN138.dst",
                  "TRIP LINELN139.dst",
                  "TRIP LINELN140.dst",
                  "TRIP LINELN141.dst",
                  "TRIP LINELN142.dst",
                  "TRIP LINELN147.dst",
                  "TRIP LINELN154.dst",
                  "TRIP LINELN92.dst",
                  "TRIP LINELN69.dst",
                  "TRIP LINELN73.dst",
                  "TRIP LINELN18.dst",
                  "TRIP LINELN113.dst",]

#output files
output_file="final_results.csv"

  


#Voltage Ride though curve time limits
t1 = 0.2 + t_dst 
t2=3.0 + t_dst
t3=60.0


#Voltage Ride through curve voltage limits
unom=0.95
u1=0.9
u2=0.88
umin=0.05


t_end=120.0 +t_dst



# Frequency limits
frequency_upper_collapse_limit = 51.0
frequency_lower_collapse_limit = 49.0   
frequency_upper_warning_limit = 50.5
frequency_lower_warning_limit = 49.5
rocof_limit= 1.0 
t_rocof= 0.5



time_ref = [0, t_dst, t_dst, t1, t2, t3]
voltage_ref = [unom, unom, umin, umin, u2, u2]
voltage_ref_warning = [unom, unom, umin + 0.05, umin + 0.05, u2 + 0.05, u2 + 0.05]