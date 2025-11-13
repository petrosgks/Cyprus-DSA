import time
import glob
import csv
import pandas as pd
import os


def safe_write_csv(df, filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            df.to_csv(filepath, index=False)
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(0.1)
    return False


def merge_results(output_file, timestamp, len_dst_files, system_status, start_time):
    temp_dir = "temp_results"
    all_files = glob.glob(os.path.join(temp_dir, "temp_process_*.csv"))
    
    if not all_files:
        print("\nNo results to merge.Normal operation\n")
        return

    try:
        
        final_df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
        final_df = final_df.drop_duplicates(subset=["N-1 Disturbance"])
        
        
        with open(output_file, 'w', encoding='utf-8') as f:
            
            
            f.write("#N-1 DYNAMIC SECURITY ASSESSMENT REPORT\n")
            f.write(f"#Generated at: {timestamp}\n")
            f.write(f"#Simulation time: {time.time() - start_time:.2f}s\n")
            f.write(f"#Processed DSTs: {len_dst_files}\n")
            f.write(f"#Warnings detected: {len(final_df)}\n")
            f.write(f"#System status: {system_status}\n\n")
            
            
            final_df.to_csv(
                f, 
                sep='\t', 
                index=False, 
                quoting=csv.QUOTE_NONNUMERIC,  
                escapechar='\\'
            )
            
        print(f"LLM-optimized report generated: {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")
