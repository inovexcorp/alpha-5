from typing import Optional, Tuple, List, Dict, Set, DefaultDict, Union
import re
import csv
import argparse
import xml.etree.ElementTree as ET
import logging
from collections import defaultdict

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

def normalize_result(result: str) -> str:
    """Normalize to canonical types: Passed, Failed, Warning, Error, Unknown."""
    if not result:
        return 'Unknown'
    result = result.strip().lower()
    if result == 'passed':
        return 'Passed'
    elif result == 'failed':
        return 'Failed'
    elif result == 'warning':
        return 'Warning'
    elif result == 'error':
        return 'Error'
    else:
        return 'Unknown'

def clean_text(text: str) -> str:
    """Remove newlines and excess whitespace to prevent output formatting errors."""
    return re.sub(r'\s+', ' ', text).strip() if text else ''

def extract_data(xml_file: str) -> Tuple[
    Optional[Dict[str, Union[
        DefaultDict[str, DefaultDict[str, Set[str]]],
        DefaultDict[str, Set[str]],
        DefaultDict[str, Set[str]]
    ]]],
    Optional[List[Dict[str, str]]]
]:
    """
    Parse Nessus results once and return:
    - summary_data: dict with NIST control results
    - checklist_data: list of all non-passed checks with full detail
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse results file '{xml_file}': {e}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error opening results file '{xml_file}': {e}")
        return None, None

    report = root.find('Report')
    if report is None:
        logging.error("No <Report> element found in results file.")
        return None, None

    namespaces = {'cm': 'http://www.nessus.org/cm'}

    # Summary
    nist_results = defaultdict(lambda: defaultdict(set))
    nist_stig_ids = defaultdict(set)
    # nist_solutions = defaultdict(set)

    # Checklist
    checklist_data = []

    for reportHost in report.findall('ReportHost'):
        hostname_elem = reportHost.find('./HostProperties/tag[@name="hostname"]')
        hostname = hostname_elem.text if hostname_elem is not None else ''

        for reportItem in reportHost.findall('ReportItem'):
            try:
                passOrFail_elem = reportItem.find('cm:compliance-result', namespaces)
                result_raw = passOrFail_elem.text if passOrFail_elem is not None else ''
                result_type = normalize_result(result_raw)

                nist_elem = reportItem.find('cm:compliance-reference', namespaces)
                if nist_elem is not None and nist_elem.text:
                    nist_matches = re.findall(r'800-53\|([^,]+)', nist_elem.text)
                else:
                    continue

                checkName_elem = reportItem.find('cm:compliance-check-name', namespaces)
                actualValue_elem = reportItem.find('cm:compliance-actual-value', namespaces)
                solution_elem = reportItem.find('cm:compliance-solution', namespaces)

                check_name = clean_text(checkName_elem.text if checkName_elem is not None else '')
                actual_value = clean_text(actualValue_elem.text if actualValue_elem is not None else '')
                solution_text = clean_text(solution_elem.text if solution_elem is not None else '')

                match = re.match(r'^(\S+)\s+-\s+(.*)', check_name)
                if match:
                    stigId = match.group(1)
                    description = match.group(2)
                else:
                    stigId = ''
                    description = ''

                for nist_id in nist_matches:
                    # Summary data
                    nist_results[nist_id][result_type].add(hostname)
                    nist_stig_ids[nist_id].add(stigId)
                    # if solution_text:
                    #     nist_solutions[nist_id].add(solution_text)

                    # Checklist data
                    if result_type != 'Passed':
                        checklist_data.append({
                            'Host': hostname,
                            'NIST Control ID': nist_id,
                            'Result': result_type,
                            'Stig ID': stigId,
                            'Description': description,
                            'Actual Value': actual_value,
                            'Solution': solution_text
                        })

            except Exception as e:
                logging.error(f"Error processing ReportItem in host '{hostname}': {e}")
                continue

    # Wrap up summary data
    summary_data = {
        'results': nist_results,
        'stig_ids': nist_stig_ids,
        # 'solutions': nist_solutions
    }

    return summary_data, checklist_data

def write_summary_csv(summary_data, output_file):
    """Write summary CSV from grouped NIST compliance results."""
    try:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'NIST Compliance ID', 'Result', 'Affected Hosts', 'Stig IDs'#, 'Solutions'
            ])
            writer.writeheader()

            for nist_id in sorted(summary_data['results'].keys()):
                results = summary_data['results'][nist_id]
                stig_ids = ', '.join(sorted(summary_data['stig_ids'][nist_id]))
                # solutions = ' | '.join(sorted(summary_data['solutions'][nist_id]))

                if 'Failed' in results:
                    writer.writerow({
                        'NIST Compliance ID': nist_id,
                        'Result': 'Failed',
                        'Affected Hosts': ', '.join(sorted(results['Failed'])),
                        'Stig IDs': stig_ids,
                        # 'Solutions': solutions
                    })
                elif 'Passed' in results and all(rt not in results for rt in ['Failed', 'Warning', 'Error']):
                    writer.writerow({
                        'NIST Compliance ID': nist_id,
                        'Result': 'Passed',
                        'Affected Hosts': '',
                        'Stig IDs': stig_ids,
                        # 'Solutions': solutions
                    })

                for rt in ['Warning', 'Error']:
                    if rt in results:
                        writer.writerow({
                            'NIST Compliance ID': nist_id,
                            'Result': rt,
                            'Affected Hosts': ', '.join(sorted(results[rt])),
                            'Stig IDs': stig_ids,
                            # 'Solutions': solutions
                        })
    except Exception as e:
        logging.error(f"Failed to write to output file '{output_file}': {e}")
        return False
    return True

def write_checklist_csv(checklist_data, output_file):
    """Write checklist CSV containing all non-passed compliance checks."""
    try:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'Host', 'NIST Control ID', 'Result', 'Stig ID', 'Description', 'Actual Value', 'Solution'
            ])
            writer.writeheader()
            for row in checklist_data:
                writer.writerow(row)
    except Exception as e:
        logging.error(f"Failed to write to output file '{output_file}': {e}")
        return False
    return True

def parse_args():
    """Parse command-line arguments for input and output file paths."""
    parser = argparse.ArgumentParser(
        description='Parse Nessus scan results file and output NIST Control status summary and non-passed checks.'
    )
    parser.add_argument('--input', required=True, help='Path to the input Nessus results file.', type=str)
    parser.add_argument('--summary', nargs='?', default='summary.csv', help='Summary Output CSV file (default: summary.csv)', type=str)
    parser.add_argument('--checklist', nargs='?', default='checklist.csv', help='Checklist Output CSV file (default: checklist.csv)', type=str)
    return parser.parse_args()

def main(input_file, summary_file, checklist_file):
    """Main control flow to generate both CSV outputs from a Nessus results file."""
    try:
        summary_data, checklist_data = extract_data(input_file)
        if summary_data is None or checklist_data is None:
            logging.error(f"extract_data() returned None for input file '{input_file}'.")
            exit(1)
    except Exception as e:
        logging.error(f"Error extracting data from results file '{input_file}': {e}")
        exit(1)

    try:
        success1 = write_summary_csv(summary_data, summary_file)
        success2 = write_checklist_csv(checklist_data, checklist_file)
    except Exception as e:
        logging.error(f"Unexpected error while writing CSV files: {e}")
        exit(1)

    if success1 and success2:
        print(f"CSV files '{summary_file}' and '{checklist_file}' created successfully.")
    else:
        logging.error("Error: Failed to write one or both CSV output files.")
        exit(1)

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.summary, args.checklist)
