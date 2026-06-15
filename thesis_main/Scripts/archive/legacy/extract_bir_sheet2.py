#!/usr/bin/env python3
"""
Extract zonal tables from BIR Zonal Value files (XLS/HTML).
Handles hierarchical metadata (Province, City, Barangay) and merged cells.
"""
import os
import re
import sys
import json
import traceback
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def parse_html_table_to_grid(html_content):
    """
    Parses an HTML table into a 2D grid, resolving all rowspan and colspan attributes.
    Replicates text across all cells in the span (built-in forward fill).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    if not table:
        return []
    
    grid = {}
    for r_idx, row in enumerate(table.find_all('tr')):
        cols = row.find_all(['td', 'th'])
        c_idx = 0
        for col in cols:
            # Move to the next available column index
            while (r_idx, c_idx) in grid:
                c_idx += 1
                
            text = col.get_text(separator=" ", strip=True)
            rowspan = int(col.get('rowspan', 1))
            colspan = int(col.get('colspan', 1))
            
            # Fill the grid for the extent of the span
            for r in range(rowspan):
                for c in range(colspan):
                    grid[(r_idx + r, c_idx + c)] = text
            c_idx += colspan
            
    if not grid:
        return []
        
    max_r = max(r for r, c in grid.keys())
    max_c = max(c for r, c in grid.keys())
    
    return [[grid.get((r, c), "") for c in range(max_c + 1)] for r in range(max_r + 1)]

def extract_hierarchical_data(grid, source_file):
    """
    Processes a 2D grid (list of lists) to extract zonal values with full hierarchy.
    """
    extracted_data = []
    current_province = "UNKNOWN"
    current_city = "UNKNOWN"
    current_barangay = "UNKNOWN"
    effectivity_date = "UNKNOWN"
    do_no = "UNKNOWN"
    
    for row in grid:
        if not row or len(row) < 2:
            continue
        
        # Force convert cells to strings for safe comparison
        row_clean = [str(c).strip() if c is not None else "" for c in row]
        row_str = " ".join(row_clean).strip()
        
        # 1. Capture Metadata
        if "Province" in row_clean[0] and ":" in row_clean[1]:
            current_province = row_clean[1].split(":")[-1].strip() if len(row_clean[1].split(":")) > 1 else row_clean[1].strip()
        elif "City/Municipality" in row_clean[0] and ":" in row_clean[1]:
            current_city = row_clean[1].split(":")[-1].strip() if len(row_clean[1].split(":")) > 1 else row_clean[1].strip()
        elif "Zone/Barangay" in row_clean[0] and ":" in row_clean[1]:
            current_barangay = row_clean[1].split(":")[-1].strip() if len(row_clean[1].split(":")) > 1 else row_clean[1].strip()
        
        # Robust metadata detection for DO and Date (always check these)
        if "D.O. No." in row_str:
            match = re.search(r"D\.O\. No\.\s*[:\-]?\s*([0-9A-Z\-\s]+)", row_str, re.I)
            if match: do_no = match.group(1).strip()
        if "Effectivity Date" in row_str:
            match = re.search(r"Effectivity Date\s*[:\-]?\s*([0-9A-Z\/,\-\s]+)", row_str, re.I)
            if match: effectivity_date = match.group(1).strip()

        # 2. Skip headers and noise
        if "STREET NAME" in str(row[0]).upper() or "CLASSIFICATION" in str(row_str).upper():
            continue
        if "DEFINITION OF TERMS" in row_str.upper() or "CLASSIFICATION LEGEND" in row_str.upper():
            continue
            
        # 3. Target data rows
        # Data rows typically have a classification code (2-3 chars) and a numeric zonal value
        if len(row) >= 4:
            street = str(row[0]).strip()
            vicinity = str(row[1]).strip()
            classification = str(row[2]).strip()
            zonal_value_raw = str(row[3]).strip()
            
            # A valid data row MUST have a classification and something in zonal value
            if not classification or classification.lower() == "classification":
                continue
            
            # Clean zonal value
            z_val_clean = zonal_value_raw.replace(",", "").replace("*", "").strip()
            try:
                z_val = float(z_val_clean)
            except ValueError:
                continue # Not a numeric row
                
            # Clean Barangay name (remove "continuation" markers)
            clean_barangay = re.sub(r"\s*\(continuation\)\s*", "", current_barangay, flags=re.I).strip()
            
            extracted_data.append({
                "Province": current_province,
                "City": current_city,
                "Barangay": clean_barangay,
                "Street_Subdivision": street,
                "Vicinity": vicinity,
                "Classification": classification,
                "Zonal_Value": z_val,
                "DO_No": do_no,
                "Effectivity_Date": effectivity_date,
                "Source": source_file
            })
            
    return extracted_data

def process_file(file_path):
    print(f"Processing: {os.path.basename(file_path)}...")
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.htm', '.html']:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            grid = parse_html_table_to_grid(content)
            return extract_hierarchical_data(grid, os.path.basename(file_path))
    
    elif ext in ['.xls', '.xlsx']:
        # For Excel files, read all sheets
        all_data = []
        try:
            xl = pd.ExcelFile(file_path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet, header=None)
                # Forward fill merged cells for the first few columns (Street, Vicinity)
                # But only if they are actually merged. In BIR sheets, Street/Vicinity are merged.
                df.iloc[:, 0] = df.iloc[:, 0].ffill()
                df.iloc[:, 1] = df.iloc[:, 1].ffill()
                grid = df.values.tolist()
                all_data.extend(extract_hierarchical_data(grid, f"{os.path.basename(file_path)} [{sheet}]"))
        except Exception as e:
            print(f"Error reading Excel {file_path}: {e}")
        return all_data
    
    return []

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(script_dir, '..', 'Data', 'BIR Zonal Values'))
    output_dir = os.path.join(data_dir, 'extracted_v2')
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(data_dir) if f.lower().endswith(('.htm', '.html', '.xls', '.xlsx'))]
    files = sorted(files)
    
    total_rows = []
    for fname in files:
        path = os.path.join(data_dir, fname)
        data = process_file(path)
        if data:
            total_rows.extend(data)
            # Save individual file output
            df = pd.DataFrame(data)
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(fname)[0])
            df.to_csv(os.path.join(output_dir, f"{safe_name}_extracted.csv"), index=False)
            print(f"  Captured {len(data)} rows.")

    if total_rows:
        final_df = pd.DataFrame(total_rows)
        consolidated_path = os.path.join(output_dir, "BIR_Zonal_Consolidated_v2.csv")
        final_df.to_csv(consolidated_path, index=False)
        print(f"\nExtraction complete! Consolidated file: {consolidated_path}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
