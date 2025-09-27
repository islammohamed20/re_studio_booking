#!/usr/bin/env python3

import frappe
import sys
import os

# Set the current working directory to frappe  
os.chdir('/home/frappe/frappe')

try:
    # Initialize Frappe
    frappe.init('site1.local')
    frappe.connect()
    
    # Test photographer_name field
    photographers = frappe.get_all('Photographer', 
                                 fields=['name', 'photographer_name'], 
                                 limit=3)
    
    print(f'✅ Success! Found {len(photographers)} photographers')
    for p in photographers:
        print(f'  - {p.name}: {p.photographer_name}')
        
except Exception as e:
    print(f'❌ Error: {str(e)}')
    sys.exit(1)
finally:
    frappe.destroy()
