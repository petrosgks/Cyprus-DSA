import multiprocessing
import os
import time
import pandas as pd
import glob
import pyramses
import requests
import json
import csv
from process_data import SystemStatus, check_generator_frequency, check_bus_voltage, process_dst_files, load_flow_calc
from config import *
from LLM_report import *
from post_processing import *
from pre_processing_data import *
from datetime import datetime
from md_to_pdf_report import *


def run_simulation(output_trace, dyn_data, loadflow_data, solveroptions, init_trace, 
                   cont_trace, disc_trace, obs_dat, obs_trj, t_simulation, task_queue, 
                   process_id, processed_dst_files, processed_dst_lock, global_system_status):
    temp_dir = "temp_results"
    os.makedirs(temp_dir, exist_ok=True)
    local_results = []
    
    while not task_queue.empty():
        try:
            dst_file = task_queue.get_nowait()
            dst_name = os.path.splitext(os.path.basename(dst_file))[0]
            
            
            with processed_dst_lock:
                if dst_file in processed_dst_files:
                    print(f"Process {process_id} is skipping (already processed): {dst_name}")
                    continue
                processed_dst_files[dst_file] = True  
            
            print(f"\n=== Process {process_id} (PID: {os.getpid()}) processing: {dst_name} ===")
            
            
            system_status = SystemStatus(global_system_status)  
            warning_messages = []
            case = pyramses.cfg()
            case.addOut(output_trace)
            case.addData(dyn_data)
            case.addData(loadflow_data)
            case.addData(solveroptions)
            case.addInit(init_trace)
            case.addDst(dst_file)
            case.addCont(cont_trace)
            case.addDisc(disc_trace)
            case.addObs(obs_dat)
            case.addTrj(obs_trj)

           
            ram = pyramses.sim()
            ret = ram.execSim(case, t_simulation)
            ram.endSim()

            
            ext = pyramses.extractor(case.getTrj())
            
            
            sync_gener = ram.getAllCompNames("SYNC")
            for sync in sync_gener:
                time_data = ext.getSync(sync)._time
                rotor_speed = ext.getSync(sync).S.value
                check_generator_frequency(time_data, rotor_speed, sync, system_status, warning_messages)
            
            
            buses = ram.getAllCompNames("BUS")
            for bus in buses:
                time_data = ext.getBus(bus)._time
                voltage = ext.getBus(bus).mag.value
                check_bus_voltage(time_ref, voltage_ref, voltage_ref_warning, time_data, voltage, bus, system_status, warning_messages)
            
            print(f"   Local Status for {dst_name}: {system_status.get()}")  
            print(f"   Global System Status: {global_system_status.value}")  

            
            if system_status.get() != "Normal Operation":
                local_results.append({
                    "N-1 Disturbance": dst_name,
                    "Warning Messages": "\n".join(warning_messages),
                    "System Classification": system_status.get()
                })
                print(f"Process {process_id} - Results saved for {dst_name}")
            else:
                print(f"Process {process_id} - Normal Operation for {dst_name}")

        except Exception as e:
            print(f"Process {process_id} - Error in {dst_name}: {str(e)}")

   
    if local_results:
        temp_file = os.path.join(temp_dir, f"temp_process_{process_id}.csv")
        if safe_write_csv(pd.DataFrame(local_results), temp_file):
            print(f"Process {process_id} saved results to {temp_file}")



if __name__ == "__main__":


    folder = os.path.dirname(os.path.abspath(__file__))  

    for filename in os.listdir(folder):
        if filename.endswith(".trace"):
            filepath = os.path.join(folder, filename)
            os.remove(filepath)
            


        if filename.endswith(".trj"):
                filepath = os.path.join(folder, filename)
                os.remove(filepath)
                

    start_time = time.time()
    timestamp = pd.Timestamp.now().strftime("%d-%m-%Y, %H:%M:%S")
    manager = multiprocessing.Manager()

    temp_dir = "temp_results"
    if os.path.exists(temp_dir):
        for f in glob.glob(os.path.join(temp_dir, "*.csv")):
            os.remove(f)
    
    
    processed_dst_files = manager.dict()
    processed_dst_lock = manager.Lock()
    global_system_status = manager.Value('str', 'Normal Operation')  
    
    
    #load_flow_calc(exe_path, commands_file)
    pre_process()
    dst_files = process_dst_files(dyn_data, loadflow_data, t_dst)
    filtered_dst_files = [file for file in dst_files if os.path.basename(file) not in excluded_files]
    len_dst_files = len(filtered_dst_files)

    task_queue = multiprocessing.Queue()


    for file in filtered_dst_files:
        task_queue.put(file)
    
    print(f"\nStarting processing for {len(dst_files)} DST files...")
    
    
    processes = []
    for i in range(number_of_processors):  
        p = multiprocessing.Process(
            target=run_simulation,
            args=(
                f"output_{i+1}.trace", dyn_data, loadflow_data, solveroptions,
                f"init_{i+1}.trace", f"cont_{i+1}.trace", f"disc_{i+1}.trace",
                "obs.dat", f"obs_{i+1}.trj", t_simulation, task_queue, i+1, 
                processed_dst_files, processed_dst_lock, global_system_status
            ),
            name=f"DST_Worker_{i+1}"
        )
        processes.append(p)
        p.start()
    
    
    for p in processes:
        p.join()
    
    
    system_status= global_system_status.value
    merge_results(output_file,timestamp,len_dst_files,system_status,start_time)
    md_file = generate_dsa_report(api_key,results_csv_path,descriptions_csv_path,model,output_md_file)
    clean_markdown_file("dsa_report.md")
    md_to_pdf("dsa_report.md", "dsa_report.pdf")
    
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")
    print(f"Processed disturbance files: {len(processed_dst_files)}/{len(dst_files)}")
    print(f"Final System Classification: {global_system_status.value} ===")  