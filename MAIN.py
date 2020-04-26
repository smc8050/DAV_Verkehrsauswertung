from read_CSV import read_csv
from utils import Timestamp, IdCube

t0 = Timestamp('2020-01-01T00:00:00')
t1 = Timestamp('2020-01-03T12:00:00')
txt_path = 'MSID_Input.txt'
csv_url = "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv"

A, MSID_list, date_list = read_csv(txt_path, t0, t1, csv_url)

print(date_list)
