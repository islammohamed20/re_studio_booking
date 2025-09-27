#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from datetime import datetime

def cleanup_fixed_files():
    """
    This script will find and remove all -fixed.html files after verifying that 
    the original files have been properly replaced.
    """
    print("Starting cleanup of -fixed.html files...")
    
    # Define the directory path
    www_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "re_studio_booking", "www")
    
    # Create a backup directory with timestamp (just in case)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(www_dir, f"fixed_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Find all files ending with -fixed.html
    fixed_files_cmd = ["find", www_dir, "-name", "*-fixed.html"]
    fixed_files_output = subprocess.check_output(fixed_files_cmd).decode("utf-8")
    fixed_files = [f.strip() for f in fixed_files_output.splitlines() if f.strip()]
    
    print(f"Found {len(fixed_files)} files with -fixed.html suffix.")
    
    removed_count = 0
    backup_count = 0
    error_count = 0
    
    for fixed_file in fixed_files:
        try:
            # Get just the filename
            fixed_filename = os.path.basename(fixed_file)
            # Get the directory
            fixed_dir = os.path.dirname(fixed_file)
            # Get the original filename (without -fixed)
            original_filename = fixed_filename.replace("-fixed.html", ".html")
            # Full path to original file
            original_file = os.path.join(fixed_dir, original_filename)
            
            # Check if original file exists and has content
            if not os.path.exists(original_file):
                print(f"⚠️ Original file {original_file} doesn't exist! Cannot delete {fixed_file}")
                error_count += 1
                continue
            
            # Check if both files have content
            with open(fixed_file, 'r', encoding='utf-8') as f:
                fixed_content = f.read()
            
            with open(original_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # If original file doesn't have proper content, don't delete
            if "{% extends" not in original_content or len(original_content) < 100:
                print(f"⚠️ Original file {original_file} may not have been properly replaced!")
                error_count += 1
                continue
            
            # If original seems right, make a backup of the fixed file just in case
            backup_file = os.path.join(backup_dir, fixed_filename)
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            backup_count += 1
            print(f"✅ Backed up: {fixed_file} → {os.path.relpath(backup_file, os.path.dirname(backup_dir))}")
            
            # Remove the fixed file
            os.remove(fixed_file)
            removed_count += 1
            print(f"✅ Removed: {fixed_file}")
            
        except Exception as e:
            print(f"❌ Error processing {fixed_file}: {str(e)}")
            error_count += 1
    
    print("\nSummary:")
    print(f"  • Files removed: {removed_count}")
    print(f"  • Files backed up: {backup_count}")
    print(f"  • Errors encountered: {error_count}")
    print(f"  • Backup directory: {backup_dir}")
    
    return removed_count, backup_count, error_count

def main():
    print("This script will remove all -fixed.html files after verifying the original files exist.")
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        cleanup_fixed_files()
        print("Done!")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
