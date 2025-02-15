import csv

data = [
    ['Name', 'Age', 'Occupation'],
    ['Alice', '30', 'Engineer'],
    ['Bob', '25', 'Teacher'],
    ['Charlie', '35', 'Doctor']
]

filename = 'example.csv'

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)