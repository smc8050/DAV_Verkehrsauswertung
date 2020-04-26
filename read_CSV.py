import requests
from contextlib import closing
import csv
import numpy as np
import datetime

def read_csv(MSID, start, end):
    url = "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv"

    I = len(MSID)
    J = (end.date() - start.date()).days + 1
    K = 24
    A = np.zeros((I, J, K), dtype = np.int32)

    with closing(requests.get(url, stream=True)) as r:
        f = (line.decode('utf-8') for line in r.iter_lines())
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for row in reader:
            if len(row) != 0:
                if row[0] in MSID:
                    if start.isSmaller(row[17]) and end.isBigger(row[17]):
                        i = MSID.index(row[0])
                        datetime_now = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S')
                        j = (datetime_now - start.date()).days
                        k = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S').hour
                        A[i, j, k] = int(row[19])

    with open('outfile.txt', 'wb') as f:
        for line in A:
            np.savetxt(f, line, fmt='%.2f')
