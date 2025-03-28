# Alpha 5

## How to use
To run the script navigate to the directory containing containing the script and run it with the audit file as the first argument and the manual file as the second argument, like this:
```
python3 alpha5.py DISA_STIG_Red_Hat_Enterprise_Linux_9_v2r2.audit U_RHEL_9_STIG_V2R3_Manual-xccdf.xml
```
Where `alpha5.py` is the path to the script, `DISA_STIG_Red_Hat_Enterprise_Linux_9_v2r2.audit` is the path to the audit file, and `U_RHEL_9_STIG_V2R3_Manual-xccdf.xml` is the path to the manual file. These files are included in this repo to use as an example.  
  
The script will generate a csv file in the directory where the script is located called `output.csv` containing rows for every `<item>` or `<custom_item>` from the audit file and every `<group>` from the manual file that share a STIG-ID.
