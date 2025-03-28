import re
import sys
import csv
import xml.etree.ElementTree as ET


# maybe make some logic to enforce that the first arg is a .audit and the second is a .xml for this `if`
if len(sys.argv) > 1:
    auditArg = sys.argv[1]
    manualArg = sys.argv[2]
else:
    # change this help message to reflect the final name of the script (which probably won't be `script5` lol)
    print("Please run the script with this format: python3 script5.py path/to/audit/file.audit path/to/manual/file.xml")



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
    
    def extract_items(data):
        items = re.findall(item_pattern, data, re.DOTALL)

        # recursively extract content
        nested_items = []
        for tag, content in items:
            nested_items.append(content.strip())
            nested_items.extend(extract_items(content))

        return nested_items
    return extract_items(xml_data)

with open(auditArg, "r") as xml_file:
    stig = xml_file.read()

# items is an array of the contents of every <custom_item> and <item> tag
items = fetch_nested_item_content(stig)



# populate array that will be turned into the csv file
finalArr = []
eight_pattern = r'(?<=800-53\|)(.*?)(?=,)'
cat_pattern = r'(?<=CAT\|)(.*?)(?=,)'
stig_pattern = r'(?<=STIG-ID\|)(.*?)(?=,)'
for manualEntry in manualData:
    for auditEntry in items:
        tempVar = re.search(stig_pattern, auditEntry).group(1) if re.search(stig_pattern, auditEntry) else None
        if tempVar == manualEntry['Version (Stig-ID)']:
            # Add new keys directly to the manualEntry dictionary
            manualEntry['CAT'] = re.search(cat_pattern, auditEntry).group(1) if re.search(cat_pattern, auditEntry) else None
            manualEntry['800-53'] = re.search(eight_pattern, auditEntry).group(1) if re.search(eight_pattern, auditEntry) else None
            finalArr.append(manualEntry)



# then convert finalArr into the csv file
csv_file = 'output.csv'
fieldnames = finalArr[0].keys()

with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(finalArr)

print(f"CSV file '{csv_file}' created successfully.")