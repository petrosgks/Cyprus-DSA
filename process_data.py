import os
import pyramses
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from config import *
import subprocess
import shutil
class SystemStatus:
    def __init__(self, shared_value=None):
        self.classification = 'Normal Operation'
        self.shared_value = shared_value  
    
    def update(self, new_classification):
        if self.classification == 'EMERGENCY STATE':
            return
        
        if new_classification == 'EMERGENCY STATE':
            self.classification = 'EMERGENCY STATE'
        elif new_classification == 'Alert state' and self.classification != 'EMERGENCY STATE':
            self.classification = 'Alert state'
        
        
        if self.shared_value is not None:
            if new_classification == 'EMERGENCY STATE':
                self.shared_value.value = 'EMERGENCY STATE'
            elif (new_classification == 'Alert state' and 
                  self.shared_value.value != 'EMERGENCY STATE'):
                self.shared_value.value = 'Alert state'
    
    def get(self):
        return self.classification

def check_generator_frequency(time, rotor_speed, sync, system_status, warning_messages):
    k = 0
    for i in range(len(time)):
        if time[i] > (t_dst + t_rocof):
            k = i
            break

    frequency_deviation = (( rotor_speed[k]-1.0) * 3000) / 60 
    rocof = round((frequency_deviation) / (time[k] - t_dst), 3)
    index_end_simulation = len(time) - 1
    frequency_end_simulation = round(((rotor_speed[index_end_simulation] * 3000) / 60), 3)

    if abs(rocof) > 1.0:
        msg = f"► ROCOF of generator {sync} exceeds 1.0 Hz/s: {rocof} Hz/s"
        print(msg)
        warning_messages.append(msg)
        system_status.update('EMERGENCY STATE')
    if frequency_end_simulation > frequency_upper_collapse_limit or frequency_end_simulation < frequency_lower_collapse_limit:
        msg = f"► Frequency of generator {sync} exceeds collapse limits: {frequency_end_simulation} Hz"
        print(msg)
        warning_messages.append(msg)
        system_status.update('EMERGENCY STATE')
    elif frequency_end_simulation > frequency_upper_warning_limit or frequency_end_simulation < frequency_lower_warning_limit:
        msg = f"► Frequency of generator {sync} exceeds warning limits: {frequency_end_simulation} Hz"
        print(msg)
        warning_messages.append(msg)
        system_status.update('Alert state')

def check_bus_voltage(time_ref, voltage_ref, voltage_ref_warning, time, voltage, bus, system_status, warning_messages):
    interp_func_collapse = interpolate.interp1d(time_ref, voltage_ref, kind='linear', fill_value='extrapolate')
    interp_func_warning = interpolate.interp1d(time_ref, voltage_ref_warning, kind='linear', fill_value='extrapolate')
    voltage_ref_collapse_interpolated = interp_func_collapse(time)
    voltage_ref_warning_interpolated = interp_func_warning(time)

    collapse_flag = np.any(voltage < voltage_ref_collapse_interpolated)
    warning_flag = np.any(voltage < voltage_ref_warning_interpolated)

    if collapse_flag:
        msg = f"► UVFRT violation on bus {bus}"
        print(msg)
        warning_messages.append(msg)
        system_status.update('EMERGENCY STATE')
    elif warning_flag:
        msg = f"► UVFRT warning on bus {bus}"
        print(msg)
        warning_messages.append(msg)
        system_status.update('Alert state')

def load_flow_calc(exe_path, commands_file):
    try:
        with open(commands_file, "r") as f:
            commands = f.read()
        process = subprocess.Popen(exe_path, stdin=subprocess.PIPE, text=True)
        stdout_data, stderr_data = process.communicate(commands)
        return process.returncode
    except Exception as e:
        print(f"Error: {e}")
        return -1



def process_dst_files(dyn_data, loadflow_data, t_dst):
    try:
        working_directory = os.getcwd()
        dst_directory = os.path.join(working_directory, "DST")
        
        
        if os.path.exists(dst_directory):
            shutil.rmtree(dst_directory)
            print(f"\nCleared existing DST directory: {dst_directory}")
        
        
        os.makedirs(dst_directory, exist_ok=True)
        dst_files = []

        
        try:
            with open(dyn_data, 'r') as file:
                lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("SYNC_MACH"):
                    parts = line.split()
                    if len(parts) > 1:
                        machine_name = parts[1]
                        output_file_name = os.path.join(dst_directory, f"TRIP GENERATOR {machine_name}.dst")
                        dst_files.append(output_file_name)
                        file_content = (
                            f" 0.000 CONTINUE SOLVER BD 0.020 0.001 0.0 ABL\n"
                            f" {t_dst:.3f} BREAKER SYNC_MACH {machine_name} 0\n"
                            f" 60.000 STOP"
                        )
                        with open(output_file_name, 'w') as output_file:
                            output_file.write(file_content)
                        print(f"Created file: {output_file_name}")
        except FileNotFoundError:
            print(f"Error: Dynamics data file '{dyn_data}' not found.")
            return []

        # Process loadflow data
        try:
            with open(loadflow_data, 'r') as file:
                line_lines = file.readlines()
            for line in line_lines:
                line = line.strip()
                if line.startswith("LINE"):
                    parts = line.split()
                    if len(parts) > 1:
                        line_number = parts[1]
                        output_file_name = os.path.join(dst_directory, f"TRIP LINE{line_number}.dst")
                        dst_files.append(output_file_name)
                        file_content = (
                            f" 0.000 CONTINUE SOLVER BD 0.020 0.001 0. ABL\n"
                            f" {t_dst:.3f} BREAKER BRANCH {line_number} 0 0\n"
                            f" 60.000 STOP"
                        )
                        with open(output_file_name, 'w') as output_file:
                            output_file.write(file_content)
                        print(f"Created file: {output_file_name}")
        except FileNotFoundError:
            print(f"Error: Loadflow data file '{loadflow_data}' not found.")
            return []

        return dst_files
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []