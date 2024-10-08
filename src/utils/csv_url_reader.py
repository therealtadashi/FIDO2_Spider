import csv

file_path = '../assets/top-1m.csv'
csv_list = []

def read_url():
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                csv_list.append(row[1])
            return csv_list
    except Exception as e:
        print(f"[csv_url_reader] Error opening file {file_path}: {e}")