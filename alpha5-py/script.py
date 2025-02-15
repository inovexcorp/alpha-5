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

soup = BeautifulSoup(data, "html.parser")

########### Title #############
required0 = soup.find_all("title")
title = []
for i in required0:
    title.append(i.get_text())

########### Content #############
required0 = soup.find_all("content")
content = []
for i in required0:
    content.append(i.get_text())

doc1 = list(zip(title, content))
for i in doc1:
    print(i)