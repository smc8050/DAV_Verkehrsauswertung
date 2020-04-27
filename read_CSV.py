import requests
from contextlib import closing
import csv
import numpy as np
import datetime
import os.path
from os import path
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

        msid_count = 185
        start_year = datetime.date(datetime.datetime.now().year, 1, 1)
        now = datetime.date.today()
        delta = now - start_year
        entries_count = msid_count * delta.days * 24 + datetime.datetime.now().hour * msid_count
        progress = 0

        with closing(requests.get(csv_url, stream=True)) as r:
            f = (line.decode('utf-8') for line in r.iter_lines())
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:
                progress += 1
                progress_percent = progress / entries_count * 100
                #Update progressbar here!

                if len(row) != 0:
                    if row[0] in msid_list:
                        if start.isSmaller(row[17]) and end.isBigger(row[17]):
                            i = msid_list.index(row[0])
                            datetime_now = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S')
                            j = (datetime_now - start.date()).days
                            k = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S').hour
                            A[i, j, k] = int(row[19])

        base = start.date()
        date_list = [base + datetime.timedelta(days=x) for x in range(J)]
        pickle_outfile = open(pickle_file, 'wb')
        pickle.dump(IdCube(A, msid_list, date_list), pickle_outfile)
        pickle_outfile.close()

    pickle_infile = open(pickle_file, 'rb')
    pickled_IdCube = pickle.load(pickle_infile)
    pickle_infile.close()

    return pickled_IdCube

    # with open('outfile.txt', 'wb') as f:
    #     for line in A:
    #         np.savetxt(f, line, fmt='%.2f')
