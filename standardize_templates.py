#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import argparse
from datetime import datetime

def standardize_templates():
    """
    Standardize HTML templates in the www folder by applying consistent structure and styling.
    Creates backups of the original files before modifying them.
    """
    # Define the directory path
    www_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                          "re_studio_booking", "www")
    
    # Create a backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(www_dir, f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Counter for updated files
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Files to standardize - list of tuples: (source_file, target_file)
    # This directly maps each fixed template to its target file without -fixed suffix
    templates_to_update = [
        ('admin-dashboard-fixed.html', 'admin-dashboard.html'),
        ('booking-form-fixed.html', 'booking-form.html'),
        ('bookings-fixed.html', 'bookings.html'),
        ('categories-fixed.html', 'categories.html'),
        ('packages-fixed.html', 'packages.html'),
        ('photographers-fixed.html', 'photographers.html'),
        ('services-fixed.html', 'services.html'),
        ('settings-fixed.html', 'settings.html')
    ]
    
    print(f"Starting template standardization for {len(templates_to_update)} files.")
    
    for source_filename, target_filename in templates_to_update:
        try:
            source_path = os.path.join(www_dir, source_filename)
            target_path = os.path.join(www_dir, target_filename)
            
            # Check if the source file exists
            if not os.path.exists(source_path):
                print(f"⚠️ Source template not found: {source_filename}. Skipping.")
                skipped_count += 1
                continue
            
            # Check if the target file exists
            if os.path.exists(target_path):
                # Create a backup of the target file
                backup_path = os.path.join(backup_dir, target_filename)
                shutil.copy2(target_path, backup_path)
                print(f"✅ Backed up: {target_filename} → {backup_dir}/{target_filename}")
            
            # Read the source template content with proper encoding
            with open(source_path, 'r', encoding='utf-8') as source_file:
                template_content = source_file.read().strip()
            
            # Ensure proper formatting of template tags
            # Remove any BOM characters or other invisible characters
            template_content = template_content.replace('\ufeff', '')
            
            # Make sure extends tag is properly formatted
            if not template_content.startswith('{% extends'):
                # Add extends tag if missing
                template_content = '{% extends "templates/web.html" %}\n\n' + template_content
            
            # Write the content to the target file with proper encoding
            with open(target_path, 'w', encoding='utf-8') as target_file:
                target_file.write(template_content)
                
            print(f"✅ Updated: {target_filename} with standardized template")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {source_file} → {target_file}: {str(e)}")
            error_count += 1
    
    print("\nSummary:")
    print(f"  • Templates updated: {updated_count}")
    print(f"  • Templates skipped: {skipped_count}")
    print(f"  • Errors encountered: {error_count}")
    print(f"  • Backup directory: {backup_dir}")
    
    return updated_count, skipped_count, error_count

def main():
    parser = argparse.ArgumentParser(description='Standardize HTML templates in the www folder')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("Dry run mode - no files will be changed")
        # Implement dry run logic here
        return
    
    print("Starting template standardization process...")
    standardize_templates()
    print("Done!")

if __name__ == "__main__":
    main()
