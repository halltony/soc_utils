import csv

csvfile = open('Winter Visitors.csv', 'r')
reader = csv.reader(csvfile, delimiter=',')
my_list = list(reader)
print(my_list)