import re
import sys
import csv
import xml.etree.ElementTree as ET

# maybe make some logic to enforce that the first arg is a .audit and the second is a .xml for this `if`
if len(sys.argv) > 1:
    auditArg = sys.argv[1]
    manualArg = sys.argv[2]
else:
    print("Please run the script with this format: python3 alpha5.py path/to/audit/file.audit path/to/manual/file.xml")



# logic for making objects from the xml in the manual file
def extract_group_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # handle namespace confusion
    namespaces = {
        '': 'http://checklists.nist.gov/xccdf/1.1',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    group_data = []

    for group in root.findall('.//Group', namespaces):  # .//Group searches recursively
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

    return group_data

# manualData is the array of xml objects from the manual file
manualData = extract_group_data(manualArg)



def fetch_nested_item_content(xml_data):
    item_pattern = r'<(custom_item|item)>(.*?)</\1>'
    eight_pattern = r'(?<=800-53\|)(.*?)(?=,)'
    cat_pattern = r'(?<=CAT\|)(.*?)(?=,)'
    stig_pattern = r'(?<=STIG-ID\|)(.*?)(?=,)'

    # recursively fetch content    
    def extract_items(data):
        items = re.findall(item_pattern, data, re.DOTALL)

        if not items:
            return []

        nested_items = []
        for tag, content in items:
            stig1 = re.search(stig_pattern, content.strip())
            cat1 = re.search(cat_pattern, content.strip())
            eight1 = re.search(eight_pattern, content.strip())
            item_dict = {
                'STIG': stig1.group(1) if stig1 else None,
                'CAT': cat1.group(1) if cat1 else None,
                '800-53': eight1.group(1) if eight1 else None
            }
            nested_items.append(item_dict)
            nested_items.extend(extract_items(content))
        return nested_items
    return extract_items(xml_data)

with open(auditArg, "r") as xml_file:
    stig = xml_file.read()

# items is an array of the contents of every <custom_item> and <item> tag
items = fetch_nested_item_content(stig)



# populate array that will be turned into the csv file
finalArr = []
for manualEntry in manualData:
    for auditEntry in items:
        if auditEntry['STIG'] == manualEntry['Version (Stig-ID)']:
            # Add new keys directly to the manualEntry dictionary
            manualEntry['CAT'] = auditEntry['CAT']
            manualEntry['800-53'] = auditEntry['800-53']
            finalArr.append(manualEntry)

# then convert finalArr into the csv file
csv_file = 'output.csv'
fieldnames = finalArr[0].keys()

with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(finalArr)

print(f"CSV file '{csv_file}' created successfully.")