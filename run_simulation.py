
from main_pyramses_2 import *



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
                    print(f"Process {process_id} - SKIPPING (already processed): {dst_name}")
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