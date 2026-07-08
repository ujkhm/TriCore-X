import os
import re
import pcbnew

def col_to_idx(col_str):
    # Convert Excel columns (A, B, C...) to 0-based Python indices
    col_str = col_str.strip().upper()
    if not col_str:
        return 0
    exp = 0
    idx = 0
    for char in reversed(col_str):
        idx += (ord(char) - 64) * (26 ** exp)
        exp += 1
    return idx - 1

def run_automation():
    # 1. Search for CSV files using relative path (current working directory)
    cwd = os.getcwd()
    csv_files = [f for f in os.listdir(cwd) if f.lower().endswith('.csv')]
    
    if not csv_files:
        print("ERROR: No CSV files found in the current directory: " + cwd)
        return

    print("--- KiCad Pin Delay Automation Tool ---")
    print("Available CSV files:")
    for i, f in enumerate(csv_files):
        print(f"[{i + 1}] {f}")
    
    # File selection
    try:
        file_choice = int(input(f"Select a file (1-{len(csv_files)}): "))
        selected_csv = csv_files[file_choice - 1]
    except (ValueError, IndexError):
        print("ERROR: Invalid file selection.")
        return

    # Column and row definitions
    pin_col_str = input("Which column contains the PIN NUMBER? (A, B, C...): ")
    val_col_str = input("Which column contains the LENGTH / DELAY? (A, B, C...): ")
    
    pin_idx = col_to_idx(pin_col_str)
    val_idx = col_to_idx(val_col_str)
    
    try:
        start_row = int(input("Enter the starting row (Excel numbers start from 1): "))
        python_start_row = start_row - 1
    except ValueError:
        print("ERROR: Row must be an integer.")
        return

    u_ref = input("Enter the component reference designator (e.g. U1, U2): ").strip().upper()

    # 2. Parse CSV and generate temporary TXT file
    tmp_txt_name = "kicad_temp_delay_table.txt"
    delays = {}
    
    print(f"Reading data from {selected_csv}...")
    try:
        with open(selected_csv, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            
            with open(tmp_txt_name, "w", encoding="utf-8") as out_f:
                for i in range(python_start_row, len(lines)):
                    line = lines[i].strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    
                    if len(parts) > max(pin_idx, val_idx):
                        pin_num = parts[pin_idx].strip().upper()
                        val_str = parts[val_idx].strip().lower()
                        
                        # Strip unit strings to get pure float numbers
                        clean_val = val_str.replace("mil", "").replace("mm", "").replace("ps", "").strip()
                        if pin_num and clean_val:
                            try:
                                float(clean_val)
                                # Write to temporary TXT in 'PIN VALUE' format
                                out_f.write(f"{pin_num} {clean_val}mil\n")
                            except ValueError:
                                continue
    except Exception as e:
        print("ERROR: Failed to process CSV data: " + str(e))
        if os.path.exists(tmp_txt_name):
            os.remove(tmp_txt_name)
        return

    # 3. Read back the temporary TXT file to perform the injection
    print(f"Injecting data into PCB for component {u_ref}...")
    txt_delays = {}
    if os.path.exists(tmp_txt_name):
        with open(tmp_txt_name, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        p_num, v_str = parts[0], parts[1]
                        v_mil = float(v_str.replace("mil", ""))
                        # Standard unit conversion to internal units (1 mil = 25400 IU)
                        txt_delays[p_num] = int(v_mil * 25400)

    # 4. Access KiCad 9 Active Board and Footprint
    board = pcbnew.GetBoard()
    target_fp = board.FindFootprintByReference(u_ref)

    if target_fp:
        count = 0
        for pad in target_fp.Pads():
            p_num = pad.GetNumber()
            if p_num in txt_delays:
                pad.SetPadToDieLength(txt_delays[p_num])
                count += 1
        
        pcbnew.Refresh()
        print(f"SUCCESS: Injected {count} pin delay values into {u_ref}.")
        print("Please press Ctrl + S to save the changes in the PCB editor.")
    else:
        print(f"ERROR: Component {u_ref} not found on the active board layout.")

    # 5. Automatically delete the temporary file
    if os.path.exists(tmp_txt_name):
        os.remove(tmp_txt_name)
        print("Temporary file cleaned up successfully.")

# Execute the runner
run_automation()
