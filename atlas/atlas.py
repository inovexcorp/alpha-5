import re
import csv
import argparse
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

def stream_result_data(xml_file, output_file):
    """
    Parses a Nessus compliance XML file and streams the extracted data into a CSV file.

    Args:
        xml_file (str): Path to the input Nessus XML file.
        output_file (str): Path to the output CSV file.

    Returns:
        bool: True if the data was successfully written, False otherwise.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML file '{xml_file}': {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error opening XML file '{xml_file}': {e}")
        return False

    report = root.find('Report')
    if report is None:
        logging.error("No <Report> element found in XML.")
        return False

    namespaces = {'cm': 'http://www.nessus.org/cm'}

    try:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'Hostname', 'Plugin ID', 'NIST Compliance ID', 'Stig ID', 'Result', 'Solution'
            ])
            writer.writeheader()

            for reportHost in report.findall('ReportHost'):
                hostname_elem = reportHost.find('./HostProperties/tag[@name="hostname"]')
                hostname = hostname_elem.text if hostname_elem is not None else ''

                for reportItem in reportHost.findall('ReportItem'):
                    try:
                        plugin = reportItem.get('pluginID')
                        passOrFail_elem = reportItem.find('cm:compliance-result', namespaces)
                        solution_elem = reportItem.find('cm:compliance-solution', namespaces)
                        checkName_elem = reportItem.find('cm:compliance-check-name', namespaces)
                        nist_elem = reportItem.find('cm:compliance-reference', namespaces)

                        if checkName_elem is not None and checkName_elem.text:
                            match = re.match(r'^(\S+)\s', checkName_elem.text)
                            stigId = match.group(1) if match else ''
                        else:
                            stigId = ''

                        if not stigId:
                            continue

                        if nist_elem is not None and nist_elem.text:
                            nist_matches = re.findall(r'800-53\|([^,]+)', nist_elem.text)
                            nist = ', '.join(nist_matches)
                        else:
                            nist = ''

                        writer.writerow({
                            'Hostname': hostname,
                            'Plugin ID': plugin,
                            'NIST Compliance ID': nist,
                            'Stig ID': stigId,
                            'Result': passOrFail_elem.text if passOrFail_elem is not None else '',
                            'Solution': solution_elem.text if solution_elem is not None else ''
                        })

                    except Exception as e:
                        logging.error(f"Error processing ReportItem in host '{hostname}': {e}")
                        continue

    except Exception as e:
        logging.error(f"Failed to write to output file '{output_file}': {e}")
        return False

    return True

def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract compliance data from a Nessus XML file and write to a CSV file.'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to the input Nessus XML file.',
        type=str
    )
    parser.add_argument(
        '--output',
        nargs='?',
        default='output.csv',
        help='Optional: Path to the output CSV file (default: output.csv).',
        type=str
    )
    return parser.parse_args()

def main(input_file, output_file):
    success = stream_result_data(input_file, output_file)

    if success:
        print(f"CSV file '{output_file}' created successfully.")
    else:
        exit(1)

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.output)
