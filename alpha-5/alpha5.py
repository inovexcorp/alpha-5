import re
import csv
import argparse
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

def extract_group_data(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"XML parsing error in manual file '{xml_file}': {e}")
        return []
    except Exception as e:
        logging.error(f"Error reading manual STIG XML file '{xml_file}': {e}")
        return []

    namespaces = {
        '': 'http://checklists.nist.gov/xccdf/1.1',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    group_data = []

    for group in root.findall('.//Group', namespaces):
        try:
            group_id = group.get('id')

            group_title_elem = group.find('title', namespaces)
            group_title = group_title_elem.text if group_title_elem is not None else 'No Title'

            rule = group.find('Rule', namespaces)
            if rule is not None:
                rule_id = rule.get('id')
                severity = rule.get('severity')
                version_elem = rule.find('version', namespaces)
                version = version_elem.text if version_elem is not None else 'No Version'

                rule_title_elem = rule.find('title', namespaces)
                rule_title = rule_title_elem.text if rule_title_elem is not None else 'No Rule Title'

                group_data.append({
                    'Group ID': group_id,
                    'Group Title': group_title,
                    'Rule ID': rule_id,
                    'Severity': severity,
                    'Version (Stig-ID)': version,
                    'Rule Title': rule_title
                })
        except Exception as e:
            logging.error(f"Error extracting group data from group '{group_id}': {e}")
            continue

    return group_data

def fetch_nested_item_content(xml_data):
    item_pattern = r'<(custom_item|item)>(.*?)</\1>'
    eight_pattern = r'(?<=800-53\|)(.*?)(?=,)'
    cat_pattern = r'(?<=CAT\|)(.*?)(?=,)'
    stig_pattern = r'(?<=STIG-ID\|)(.*?)(?=,)'

    def extract_items(data):
        try:
            items = re.findall(item_pattern, data, re.DOTALL)
        except Exception as e:
            logging.error(f"Regex error extracting item blocks: {e}")
            return []

        if not items:
            return []

        nested_items = []
        for tag, content in items:
            try:
                stig1 = re.search(stig_pattern, content.strip())
                cat1 = re.search(cat_pattern, content.strip())
                eight1 = re.search(eight_pattern, content.strip())
                item_dict = {
                    'STIG': stig1.group(1) if stig1 else None,
                    'CAT': cat1.group(1) if cat1 else None,
                    '800-53': eight1.group(1) if eight1 else None
                }
                if item_dict['STIG']:
                    nested_items.append(item_dict)
                nested_items.extend(extract_items(content))
            except Exception as e:
                logging.error(f"Regex error extracting nested items: {e}")
                continue
        return nested_items

    return extract_items(xml_data)

def compare_and_write(audit_path, manual_path, output_path):
    try:
        with open(audit_path, "r") as audit_file:
            audit_content = audit_file.read()
    except Exception as e:
        logging.error(f"Error reading audit file '{audit_path}': {e}")
        return

    items = fetch_nested_item_content(audit_content)
    manual_data = extract_group_data(manual_path)

    manual_dict = {
        entry['Version (Stig-ID)']: entry
        for entry in manual_data if entry.get('Version (Stig-ID)')
    }
    audit_dict = {
        entry['STIG']: entry
        for entry in items if entry.get('STIG')
    }

    finalArr = []

    try:
        for stig_id, manual_entry in manual_dict.items():
            if stig_id in audit_dict:
                audit_entry = audit_dict[stig_id]
                combined_entry = manual_entry.copy()
                combined_entry['CAT'] = audit_entry.get('CAT', 'N/A')
                combined_entry['800-53'] = audit_entry.get('800-53', 'N/A')
                combined_entry['Status'] = 'Found in both'
                finalArr.append(combined_entry)
            else:
                manual_only_entry = manual_entry.copy()
                manual_only_entry['CAT'] = 'N/A'
                manual_only_entry['800-53'] = 'N/A'
                manual_only_entry['Status'] = 'Only in Manual'
                finalArr.append(manual_only_entry)

        for stig_id, audit_entry in audit_dict.items():
            if stig_id not in manual_dict:
                audit_only_entry = {
                    'Group ID': 'N/A',
                    'Group Title': 'N/A',
                    'Rule ID': 'N/A',
                    'Severity': 'N/A',
                    'Version (Stig-ID)': stig_id,
                    'Rule Title': 'N/A',
                    'CAT': audit_entry.get('CAT', 'N/A'),
                    '800-53': audit_entry.get('800-53', 'N/A'),
                    'Status': 'Only in Audit'
                }
                finalArr.append(audit_only_entry)
    except Exception as e:
        logging.error(f"Error during comparison and merging: {e}")
        return

    try:
        if finalArr:
            fieldnames = list(finalArr[0].keys())
            if 'Status' in fieldnames:
                fieldnames.remove('Status')
                fieldnames.append('Status')
        else:
            fieldnames = ['Group ID', 'Group Title', 'Rule ID', 'Severity',
                          'Version (Stig-ID)', 'Rule Title', 'CAT', '800-53', 'Status']

        with open(output_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(finalArr)

        print(f"CSV file '{output_path}' created successfully.")
    except Exception as e:
        logging.error(f"Error writing output CSV file '{output_path}': {e}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare a Nessus audit file with a manual STIG XML file and export results as CSV."
    )
    parser.add_argument("--audit_file", required=True, help="Path to the Nessus .audit file", type=str)
    parser.add_argument("--manual_file", required=True, help="Path to the manual STIG .xml file", type=str)
    parser.add_argument("--output_file", nargs='?', default="output.csv", type=str,
                        help="Optional: output CSV filename (defaults to output.csv if not provided)")
    return parser.parse_args()

def main(audit_file, manual_file, output_file):
    try:
        compare_and_write(audit_file, manual_file, output_file)
    except Exception as e:
        logging.error(f"Unexpected error in main(): {e}")

if __name__ == "__main__":
    args = parse_args()
    main(args.audit_file, args.manual_file, args.output_file)
