import os
import subprocess
import sys
import glob

def run_command(cmd, description):
    print(f"  Running: {' '.join(cmd)}")
    try:
        print('\033[0m',end="")
        result = subprocess.run(cmd, text=True, check=True)
        print(f"  OK {description} successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  !! {description} FAILED with return code {e.returncode}")
        if e.stdout:
            print(f"    stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"    stderr: {e.stderr.strip()}")
        return False
    except FileNotFoundError as e:
        print(f"  !! Command not found: {e}")
        return False

def process_rom_test_asm():
    asm_dir = "./rom-test-asm"
    if not os.path.exists(asm_dir):
        print(f"Directory '{asm_dir}' not found, skipping...")
        return True, 0, 0
    
    asm_files = sorted(glob.glob(os.path.join(asm_dir, "*.asm")))
    if not asm_files:
        print(f"No .asm files found in '{asm_dir}', skipping...")
        return True, 0, 0
    
    print(f"\n{'='*60}")
    print(f"Processing ROM test files ({len(asm_files)} files)")
    print(f"{'='*60}")
    
    success_count = 0
    fail_count = 0
    
    for asm_file in asm_files:
        print(f"\nProcessing: {asm_file}")
        
        # Get filename without extension
        base_name = ".".join(asm_file.split(".")[:-1])
        bin_file = f"{base_name}.bin"
        
        # Step 1: Assemble
        assembler_cmd = ["./assembler/main.py", asm_file]
        if not run_command(assembler_cmd, f"Assembling {asm_file}"):
            fail_count += 1
            continue
        
        # Check if .bin file was created
        if not os.path.exists(bin_file):
            print(f"  !! Expected output file '{bin_file}' not found")
            fail_count += 1
            continue
        
        # Step 2: Run emulator with --rom
        emulator_cmd = ["./emulator/main.py", "--rom", bin_file]
        if run_command(emulator_cmd, f"Emulating {bin_file}"):
            success_count += 1
        else:
            fail_count += 1
    
    return (fail_count == 0), success_count, fail_count

def process_test_asm():
    asm_dir = "./test-asm"
    if not os.path.exists(asm_dir):
        print(f"Directory '{asm_dir}' not found, skipping...")
        return True, 0, 0
    
    asm_files = sorted(glob.glob(os.path.join(asm_dir, "*.asm")))
    if not asm_files:
        print(f"No .asm files found in '{asm_dir}', skipping...")
        return True, 0, 0
    
    print(f"\n{'='*60}")
    print(f"Processing HDA test files ({len(asm_files)} files)")
    print(f"{'='*60}")
    
    success_count = 0
    fail_count = 0
    
    for asm_file in asm_files:
        print(f"\nProcessing: {asm_file}")
        
        # Get filename without extension
        base_name = ".".join(asm_file.split(".")[:-1])
        bin_file = f"{base_name}.bin"
        
        # Step 1: Assemble
        assembler_cmd = ["./assembler/main.py", asm_file]
        if not run_command(assembler_cmd, f"Assembling {asm_file}"):
            fail_count += 1
            continue
        
        # Check if .bin file was created
        if not os.path.exists(bin_file):
            print(f"  !! Expected output file '{bin_file}' not found")
            fail_count += 1
            continue
        
        # Step 2: Run emulator with --hda
        emulator_cmd = ["./emulator/main.py", "--hda", bin_file]
        if run_command(emulator_cmd, f"Emulating {bin_file}"):
            success_count += 1
        else:
            fail_count += 1
    
    return (fail_count == 0), success_count, fail_count

def main():
    
    overall_success = True
    total_success = 0
    total_fail = 0
    
    # Process rom-test-asm files
    rom_success, rom_ok, rom_fail = process_rom_test_asm()
    overall_success = overall_success and rom_success
    total_success += rom_ok
    total_fail += rom_fail
    
    # Process test-asm files
    test_success, test_ok, test_fail = process_test_asm()
    overall_success = overall_success and test_success
    total_success += test_ok
    total_fail += test_fail
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {total_success + total_fail}")
    print(f"Successful: {total_success}")
    print(f"Failed: {total_fail}")
    
    if overall_success:
        print("\nOK All tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n!! {total_fail} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
