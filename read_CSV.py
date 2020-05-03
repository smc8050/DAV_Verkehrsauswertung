import requests
from contextlib import closing
import csv
import numpy as np
import datetime
from utils import IdCube
import pickle

def read_csv(msid_path, start, end, csv_url):

    debug = False
    pickle_file = 'IdCube'
    if not debug:

        msid_list = [line.rstrip('\n') for line in open(msid_path)]
        I = len(msid_list)
        J = (end.date() - start.date()).days + 1
        K = 24
        A = np.zeros((I, J, K), dtype=np.int32)

        with closing(requests.get(csv_url, stream=True)) as r:
            f = (line.decode('utf-8') for line in r.iter_lines())
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:

                if len(row) != 0 and row[19]!='':
                    if row[0] in msid_list:
                        if start.isSmaller(row[17]) and end.isBigger(row[17]):
                            i = msid_list.index(row[0])
                            datetime_now = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S')
                            j = (datetime_now - start.date()).days
                            k = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S').hour
                            A[i, j, k] = int(row[19])

        base = start.date()
        date_list = [base + datetime.timedelta(days=x) for x in range(J)]
        new_IdCube = IdCube(A, msid_list, date_list)

        pickle_outfile = open(pickle_file, 'wb')
        pickle.dump(new_IdCube, pickle_outfile)
        pickle_outfile.close()

    if debug:
        pickle_infile = open(pickle_file, 'rb')
        new_IdCube = pickle.load(pickle_infile)
        pickle_infile.close()

    return new_IdCube