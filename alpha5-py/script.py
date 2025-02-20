from bs4 import BeautifulSoup
# pip3 install beautifulsoup4
import csv

data ="""<page>
  <title>Chapter 1</title>
  <content>Welcome to Chapter 1</content>
</page>
<page>
 <title>Chapter 2</title>
 <content>Welcome to Chapter 2</content>
</page>"""

with open('DISA_STIG_Red_Hat_Enterprise_Linux_9_v2r2.audit', "r") as xml_file:
    stig = xml_file.read()

soup = BeautifulSoup(stig, "html.parser")

########### Title #############
required0 = soup.find_all("item")
title = []
for i in required0:
    title.append(i.get_text())

########### Content #############
required0 = soup.find_all("custom_item")
content = []
for i in required0:
    content.append(i.get_text())

doc1 = list(zip(title, content))
for i in doc1:
    print(i)

filename = 'example2.csv'

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(doc1)