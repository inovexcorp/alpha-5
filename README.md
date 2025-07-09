<table align="center"><tr><td align="center" width="9999">
<img src="logo.png" align="center" width="300" alt="Project icon">

A repository of Python scripts for analyzing and comparing STIG audit and scan results. These tools are designed to help security teams and system administrators efficiently process and correlate data from `.audit`, `.xml`, and `.nessus` files used in DISA STIG compliance assessments.</td></tr></table>

## 🔍 What These Scripts Do

### `alpha5.py`

This script compares a **Nessus audit file** (`.audit`) with a **manual STIG checklist XML file** (`.xml`). It extracts STIG IDs and compliance metadata from both sources and generates a CSV report showing:

-   Which items appear in both files (matched by STIG ID)
    
-   Which items are only present in the manual STIG
    
-   Which items are only found in the audit file
    
-   Severity category (CAT) and NIST 800-53 references if available
    

**Why this is useful:**  
It provides a quick way to reconcile manual and automated compliance checks, helping you identify discrepancies or gaps in coverage.

----------

### `atlas.py`

This script processes a **Nessus results file** (`.nessus`) to extract completed scan data, including:

-   STIG IDs
    
-   Whether each check passed or failed
    
-   Recommendations for remediation
    

**Why this is useful:**  
It gives you a simplified and actionable summary of a STIG scan without needing to open the Nessus GUI.

----------

## ⚙️ Requirements

These scripts are written in Python 3 and require no external dependencies — only built-in modules like `argparse`, `csv`, `re`, and `xml.etree.ElementTree`.

If you don't already have Python 3 installed, download it here: [https://www.python.org/downloads/](https://www.python.org/downloads/)

----------

## 🚀 How to Use

### 1. `alpha5.py` – Compare Manual and Audit Files

#### Usage:

```bash
python3 alpha5.py --audit_file path/to/file.audit --manual_file path/to/file.xml --output_file [optional_output_file_path.csv]
``` 

#### Example:

```bash
python3 alpha5.py --audit_file DISA_STIG_Red_Hat_Enterprise_Linux_9_v2r2.audit --manual_file U_RHEL_9_STIG_V2R3_Manual-xccdf.xml
``` 

-   `file.audit` – Nessus audit configuration file
    
-   `file.xml` – DISA manual checklist file
    
-   `optional_output.csv` – Optional name for the output CSV (defaults to `output.csv`)
    

#### Output:

A CSV file (`output.csv` by default) listing all matched and unmatched STIG items, along with severity and references.

----------

### 2. `atlas.py` – Extract Results from Nessus Scan File

#### Usage:

```bash
python3 atlas.py --input path/to/file.nessus --summary [optional_summary_file_path.csv] --checklist [optional_checklist_file_path.csv]
``` 

#### Example:


```bash
python3 atlas.py --input PLAIDRANGE-UNC_SERVER2022_DISA_STIG_20250404.nessus
``` 

-   `file.nessus` – Nessus result file from a completed STIG scan
    
-   `optional_summary_file_path.csv` – Optional name for the summary file (defaults to `summary.csv`)

-   `optional_checklist_file_path.csv` – Optional name for the checklist file (defaults to `checklist.csv`)
    

#### Output:

Two CSV files: `summary.csv` listing each NIST ID from the scan and which boxes failed and `checklist.csv` which provides a list of every check performed along with its description and the actual result if available, as well as the recommended solution.

----------

## 📦 Example Files

This repository includes example files in the `sample files/` directory that you can use to test the scripts such as:

-   `DISA_STIG_Red_Hat_Enterprise_Linux_9_v2r2.audit`
    
-   `U_RHEL_9_STIG_V2R3_Manual-xccdf.xml`
    
----------

## 🛠 Troubleshooting

-   Make sure you're using **Python 3**, not Python 2.
    
-   If you get a “File not found” error, check that the file path is correct.
    
-   Output files will be created in the same directory you run the script from if you don't specify a path and filename with the appropriate flag.
    

----------

## 🧾 License and Contribution

Feel free to modify and use these scripts to fit your workflow. If you find a bug or want to contribute improvements, open a pull request!