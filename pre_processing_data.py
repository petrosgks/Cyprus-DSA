import csv
import subprocess
from column_to_bus import *
import platform
from pathlib import Path
import os

def get_last_row_power_values(index_column_to_generator_MW, index_column_to_bus_loads_MW, 
                             index_column_to_shunts_MVAR, index_column_to_wind_farm_loads_MW,
                             index_column_to_bus_loads_MVAR, file_path, delimiter=';'):
    
    generator_results_MW = {}
    load_values_MW = {}
    shunt_values_MVAR = {}
    wind_farm_results_MW = {}
    load_values_MVAR = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            rows = list(reader)
            
            
            last_row = None
            for row in reversed(rows):
                if any(field.strip() for field in row):
                    last_row = row
                    break
            
            if last_row is None:
                print(f"Data not found: {file_path}")
               
                generator_results_MVAR = {k: v * 0.3287 for k, v in generator_results_MW.items()}
                
                generator_combined = {k: {"MW": v, "MVAR": generator_results_MVAR[k]} for k, v in generator_results_MW.items()}
                load_combined = {k: {"MW": v, "MVAR": 0.0} for k, v in load_values_MW.items()}
                return generator_combined, load_combined, shunt_values_MVAR, wind_farm_results_MW
            
            
            def convert_value(value_str, negative=False):
                if delimiter == ';':
                    value_str = value_str.replace(',', '.')
                try:
                    value = float(value_str)
                    return -value if negative else value
                except ValueError:
                    return 0.0
            
           
            if index_column_to_generator_MW:
                for column_index, generator_name in index_column_to_generator_MW.items():
                    if column_index < len(last_row) and last_row[column_index].strip():
                        generator_results_MW[generator_name] = convert_value(last_row[column_index].strip())
                    else:
                        generator_results_MW[generator_name] = 0.0
            
            
            if index_column_to_bus_loads_MW:
                for column_index, bus_name in index_column_to_bus_loads_MW.items():
                    if column_index < len(last_row) and last_row[column_index].strip():
                        load_values_MW[bus_name] = convert_value(last_row[column_index].strip())
                    else:
                        load_values_MW[bus_name] = 0.0
            
           
            if index_column_to_shunts_MVAR:
                for column_index, shunt_name in index_column_to_shunts_MVAR.items():
                    if column_index < len(last_row) and last_row[column_index].strip():
                        shunt_values_MVAR[shunt_name] = convert_value(last_row[column_index].strip(), negative=True)
                    else:
                        shunt_values_MVAR[shunt_name] = 0.0
            
            
            if index_column_to_wind_farm_loads_MW:
                for column_index, wind_farm_name in index_column_to_wind_farm_loads_MW.items():
                    if column_index < len(last_row) and last_row[column_index].strip():
                        wind_farm_results_MW[wind_farm_name] = convert_value(last_row[column_index].strip(), negative=True)
                    else:
                        wind_farm_results_MW[wind_farm_name] = 0.0
            
            
            if index_column_to_bus_loads_MVAR:
                for column_index, bus_name in index_column_to_bus_loads_MVAR.items():
                    if column_index < len(last_row) and last_row[column_index].strip():
                        load_values_MVAR[bus_name] = convert_value(last_row[column_index].strip())
                    else:
                        load_values_MVAR[bus_name] = 0.0
        
       
        generator_results_MVAR = {k: v * 0.3287 for k, v in generator_results_MW.items()}
        
     
        generator_combined = {k: {"MW": v, "MVAR": generator_results_MVAR[k]} for k, v in generator_results_MW.items()}
        load_combined = {k: {"MW": load_values_MW[k], "MVAR": load_values_MVAR[k]} for k in load_values_MW.keys()}
        
        return generator_combined, load_combined, shunt_values_MVAR, wind_farm_results_MW
    
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return {}, {}, {}, {}
    except Exception as e:
        print(f"Error during reading {file_path}: {e}")
        return {}, {}, {}, {}

def update_dat_file(generator_combined, load_combined, shunt_values_MVAR, wind_farm_results_MW, dat_file_path):
    
    
    shunt_to_bus_mapping = {
        'SHUNT01': 'BUS32',
        'SHUNT02': 'BUS38', 
        'SHUNT03': 'BUS40',
        'SHUNT04': 'BUS58',
        'SHUNT05': 'BUS122'
    }
    
    try:
       
        with open(dat_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            
            
            if not stripped_line or stripped_line.startswith('#'):
                new_lines.append(line)
                continue
            
            parts = stripped_line.split()
            
           
            if parts[0] == 'GENER' and len(parts) >= 5:
                gen_name = parts[1]
                if gen_name in generator_combined:
                    gen_values = generator_combined[gen_name]
                    parts[3] = f"{gen_values['MW']:.6f}"   # P
                    parts[4] = f"{gen_values['MVAR']:.6f}" # Q
                new_lines.append(' '.join(parts) + '\n')
                continue
            
           
            elif parts[0] == 'BUS' and len(parts) >= 6:
                bus_name = parts[1]
                
               
                if bus_name in load_combined:
                    bus_values = load_combined[bus_name]
                    parts[3] = f"{bus_values['MW']:.6f}"
                    parts[4] = f"{bus_values['MVAR']:.6f}"
                
                
                if bus_name in wind_farm_results_MW:
                    parts[3] = f"{wind_farm_results_MW[bus_name]:.6f}"
                    parts[4] = "0.0"
                
          
                for shunt_name, shunt_bus in shunt_to_bus_mapping.items():
                    if shunt_bus == bus_name and shunt_name in shunt_values_MVAR:
                        if len(parts) >= 6:
                            parts[5] = f"{shunt_values_MVAR[shunt_name]:.6f}"
                        else:
                           
                            while len(parts) < 5:
                                parts.append("0.0")
                            parts.append(f"{shunt_values_MVAR[shunt_name]:.6f}")
                
                new_lines.append(' '.join(parts) + '\n')
                continue
            
           
            new_lines.append(line)
        
        
        with open(dat_file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        
        print(f"File {dat_file_path} updated")
    
    except FileNotFoundError:
        print(f"file {dat_file_path} !")
    except Exception as e:
        print(f"Error during updating {dat_file_path}: {e}")





def run_pfc():
    
    base_dir = Path(__file__).resolve().parent

    
    if platform.system() == "Windows":
        program_path = base_dir / "PFC.exe"
    else:
        program_path = base_dir / "PFC"
        
        if not os.access(program_path, os.X_OK):
            os.chmod(program_path, 0o755)

    
    commands = base_dir / "pfc_commands.txt"

    
    process = subprocess.Popen(
        [str(program_path)],
        stdin=subprocess.PIPE,
        text=True)

    with commands.open("r") as f:
        for line in f:
            process.stdin.write(line)
            process.stdin.flush()

    process.stdin.close()
    process.wait()


def read_pfc_generator_values(pfc_file_path, delimiter=';'):
  
    pfc_generator_values = {}
    
    try:
        with open(pfc_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                
                parts = stripped_line.split()
                if parts[0] == 'GENER' and len(parts) >= 5:
                    gen_name = parts[1]  
                    
                    try:
                        
                        mw_value = float(parts[3])
                        mvar_value = float(parts[4])
                        pfc_generator_values[gen_name] = {'MW': mw_value, 'MVAR': mvar_value}
                    except ValueError:
                        print(f"Error during conversion {gen_name}")
                        continue
        
        print("Pfc output file data:")
        for gen_name, values in pfc_generator_values.items():
            print(f"{gen_name}: {values['MW']} MW, {values['MVAR']} MVAR")
        
        return pfc_generator_values
    
    except FileNotFoundError:
        print(f"File {pfc_file_path} not found")
        return {}
    except Exception as e:
        print(f"Error during reading {pfc_file_path}: {e}")
        return {}


def update_dyn_file(pfc_generator_values, load_combined, shunt_values_MVAR, dyn_file_path):
    
    try:
        with open(dyn_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            
            if not stripped_line:
                new_lines.append(line)
                i += 1
                continue

            parts = stripped_line.lstrip("#").split()

           
            if parts and parts[0] == "SYNC_MACH" and len(parts) >= 7:
                gen_name = parts[1]

                if gen_name in pfc_generator_values:
                    gen_values = pfc_generator_values[gen_name]
                    mw_val = gen_values["MW"]
                    mvar_val = gen_values["MVAR"]

                  
                    block_lines = lines[i:i+4]

                    if mw_val == 0 and mvar_val == 0:
                       
                        for bl in block_lines:
                            if not bl.lstrip().startswith("#"):
                                new_lines.append("#" + bl)
                            else:
                                new_lines.append(bl)
                    else:
                     
                     
                        sync_parts = block_lines[0].lstrip("#").split()
                        if len(sync_parts) >= 7:
                            sync_parts[5] = f"{mw_val:.6f}"   
                            sync_parts[6] = f"{mvar_val:.6f}" 
                        new_lines.append(" ".join(sync_parts) + "\n")

                        
                        for bl in block_lines[1:]:
                            new_lines.append(bl.lstrip("#"))

                    i += 4
                    continue

          
            elif parts and parts[0] == "SHUNT" and len(parts) >= 4:
                shunt_name = parts[1]
                if shunt_name in shunt_values_MVAR:
                    parts[3] = f"{shunt_values_MVAR[shunt_name]:.6f}"
                new_lines.append(" ".join(parts) + "\n")
                i += 1
                continue

            
            elif parts and parts[0] == "INJEC" and len(parts) >= 8:
                bus_name = parts[3]
                if bus_name in load_combined:
                    bus_values = load_combined[bus_name]
                    if bus_name == "BUS87":
                        p_val = bus_values["MW"] / 2
                        q_val = bus_values["MVAR"] / 2
                    else:
                        p_val = bus_values["MW"]
                        q_val = bus_values["MVAR"]
                    parts[6] = f"{-p_val:.6f}"
                    parts[7] = f"{-q_val:.6f}"
                new_lines.append(" ".join(parts) + "\n")
                i += 1
                continue

          
            new_lines.append(line)
            i += 1

        
        with open(dyn_file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)

        print(f"File {dyn_file_path} updated successfully")

    except FileNotFoundError:
        print(f"File {dyn_file_path} not found")
    except Exception as e:
        print(f"Error during updating {dyn_file_path}: {e}")

        
    except FileNotFoundError:
        print(f"File {dyn_file_path} not found")
    except Exception as e:
        print(f"Error during updating {dyn_file_path}: {e}")

        
def pre_process():
    
    generator_combined = {}
    load_combined = {}
    shunt_results = {}
    wind_farm_results_MW = {}
    
    
    
    result1 = get_last_row_power_values(
        index_column_to_generator_MW,
        {},  
        {},  
        {},  
        {},  
        "SSLOAD_GENUNITS_RES_30MIN_2024 _EDITED_LOADS_AND_GENERATORS_FOUND.csv",
        delimiter=';'
    )
    
    if result1:
        generator_combined, _, _, _ = result1
        print("----GENERATORS----")
        for generator, values in generator_combined.items():
            print(f"{generator}: {values['MW']} MW, {values['MVAR']} MVAR")
    
    
    
    result2 = get_last_row_power_values(
        {},  
        index_column_to_bus_loads_MW,
        index_column_to_shunts_MVAR,
        index_column_to_wind_farm_loads_MW,
        index_column_to_bus_loads_MVAR,
        "all_power_data_2024-07.csv",
        delimiter=','
    )
    
    if result2:
        _, load_combined, shunt_results, wind_farm_results_MW = result2
        print("----LOADS----")
        for bus, values in load_combined.items():
            print(f"{bus}: {values['MW']} MW, {values['MVAR']} MVAR")
        
        print("\n----SHUNTS----")
        for shunt, value in shunt_results.items():
            print(f"{shunt}: {value} MVAR")
        
        print("\n----WIND FARMS----")
        for wind_farm, value in wind_farm_results_MW.items():
            print(f"{wind_farm}: {value} MW")
    
    
    
    update_dat_file(generator_combined, load_combined, shunt_results, wind_farm_results_MW, "loadflowfinal.dat")

    exe_path = "pfc.exe"           
    commands_file = "pfc_commands.txt" 

    run_pfc()

    
    
    pfc_generator_values = read_pfc_generator_values("loadflow_pfc_output.dat")
    
    
    
    update_dyn_file(pfc_generator_values, load_combined, shunt_results, "dynfinalP_Q.dat")








