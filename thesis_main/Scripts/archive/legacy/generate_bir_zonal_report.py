#!/usr/bin/env python3
import os
import sys
import json
import traceback
import re

try:
    import pandas as pd
except Exception:
    print("Missing dependency 'pandas'. Please install with: python -m pip install pandas openpyxl xlrd")
    sys.exit(2)


def df_to_md_table(df, max_rows=5):
    rows = df.head(max_rows)
    cols = list(rows.columns)
    if len(cols) == 0:
        return "(no columns)\n"
    header = "| " + " | ".join([str(c) for c in cols]) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    lines = [header, sep]
    for _, r in rows.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if pd.isna(v):
                vals.append("")
            else:
                s = str(v)
                s = s.replace("\n", " ")
                if len(s) > 200:
                    s = s[:197] + "..."
                vals.append(s)
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def summarize_sheet(df):
    out = {}
    out['rows'] = int(len(df))
    out['cols'] = int(len(df.columns))
    out['columns'] = []
    for c in df.columns:
        col_info = {'name': str(c), 'dtype': str(df[c].dtype), 'missing': int(df[c].isnull().sum())}
        out['columns'].append(col_info)
    numeric_summary = {}
    try:
        num = df.select_dtypes(include=['number'])
        if not num.empty:
            numeric_summary = num.describe().to_dict()
    except Exception as e:
        numeric_summary = {"error": str(e)}
    out['numeric_summary'] = numeric_summary
    return out


def find_zonal_columns(columns):
    found = []
    for c in columns:
        name = str(c).lower()
        if re.search(r'zone|zonal|zv|zonal value|zonal_value|zonalvalue|zonal-val|zon_val|per sqm|per_sq|per_sq.m|per_sq_m|per_square', name):
            found.append(c)
        elif 'barangay' in name or 'brgy' in name:
            # barangay often relevant
            found.append(c)
        elif 'class' == name or name.endswith('class'):
            found.append(c)
    return list(dict.fromkeys(found))


def process_workbook(path, md_lines, summary):
    base = os.path.basename(path)
    md_lines.append(f"## Workbook: {base}\n")
    summary[base] = {'sheets': {}}
    try:
        # let pandas choose engine; fall back if necessary
        sheets = pd.read_excel(path, sheet_name=None)
    except Exception as e:
        # Try common engine fallbacks
        try:
            if path.lower().endswith('.xls'):
                sheets = pd.read_excel(path, sheet_name=None, engine='xlrd')
            else:
                sheets = pd.read_excel(path, sheet_name=None, engine='openpyxl')
        except Exception as e2:
            md_lines.append(f"Could not read workbook: {e2}\n\n")
            summary[base]['error'] = str(e2)
            return

    md_lines.append(f"Sheets: {', '.join(list(sheets.keys()))}\n")

    for sname, df in sheets.items():
        md_lines.append(f"### Sheet: {sname}\n")
        sheet_summary = summarize_sheet(df)
        summary[base]['sheets'][sname] = sheet_summary
        md_lines.append(f"- Rows: {sheet_summary['rows']}, Columns: {sheet_summary['cols']}\n")

        # Columns and missing
        md_lines.append("- Columns and missing counts:\n")
        col_lines = []
        for cinfo in sheet_summary['columns']:
            col_lines.append(f"  - `{cinfo['name']}`: dtype={cinfo['dtype']}, missing={cinfo['missing']}")
        md_lines.extend(col_lines)
        md_lines.append('\n')

        # Zonal-related columns
        zcols = find_zonal_columns(df.columns)
        if zcols:
            md_lines.append(f"- Potential zonal/identifier columns detected: {', '.join([str(x) for x in zcols])}\n")
            for z in zcols:
                try:
                    vc = df[str(z)].value_counts(dropna=True).head(10)
                    md_lines.append(f"  - `{z}` sample values (top 10):\n")
                    md_lines.append('')
                    md_lines.append(df_to_md_table(vc.reset_index().rename(columns={'index':str(z),'0':'count'})))
                except Exception:
                    try:
                        unique_vals = df[str(z)].dropna().unique().tolist()[:10]
                        md_lines.append(f"  - `{z}` unique sample: {unique_vals}\n")
                    except Exception:
                        md_lines.append(f"  - `{z}` (could not sample)\n")
        else:
            md_lines.append("- No obvious zonal/value columns detected by name heuristics.\n")

        # numeric summary (brief)
        if sheet_summary['numeric_summary']:
            md_lines.append("- Numeric summary (sample of stats):\n")
            # include up to 5 numeric columns' stats
            try:
                num = df.select_dtypes(include=['number'])
                for c in num.columns[:5]:
                    stats = num[c].describe()
                    md_lines.append(f"  - `{c}`: count={int(stats.get('count',0))}, mean={stats.get('mean','')}, min={stats.get('min','')}, max={stats.get('max','')}\n")
            except Exception:
                md_lines.append("  - (could not compute numeric summary)\n")

        # Sample rows
        try:
            md_lines.append("- Sample rows:\n")
            md_lines.append(df_to_md_table(df, max_rows=4))
        except Exception:
            md_lines.append("- (could not render sample rows)\n")

        md_lines.append('\n')


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(script_dir, '..', 'Data', 'BIR Zonal Values'))

    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        sys.exit(1)

    files = [f for f in os.listdir(data_dir) if f.lower().endswith(('.xls', '.xlsx', '.xlsm', '.xlsb'))]
    files = sorted(files)
    if not files:
        print(f"No Excel files found in {data_dir}")
        sys.exit(0)

    md_lines = ["# BIR Zonal Values — Workbook Summary\n"]
    summary = {'workbooks': {}}

    for fname in files:
        path = os.path.join(data_dir, fname)
        try:
            process_workbook(path, md_lines, summary['workbooks'])
        except Exception:
            md_lines.append(f"Error processing {fname}: {traceback.format_exc()}\n")
            summary['workbooks'][fname] = {'error': traceback.format_exc()}

    out_md = os.path.join(data_dir, 'BIR_Zonal_Report.md')
    out_json = os.path.join(data_dir, 'BIR_Zonal_Summary.json')

    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Report written to: {out_md}")
    print(f"Summary JSON written to: {out_json}")


if __name__ == '__main__':
    main()
