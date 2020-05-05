import requests
from contextlib import closing
import csv
import numpy as np
import datetime
from utils import IdCube
import pickle
import time

def read_csv(msid_path, start, end, csv_url, exclude_weekends, exclude_holidays):

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
            counter = 0
            t_start = time.time()
            for row in reader:
                if len(row) != 0 and row[19]!='':
                    if row[0] in msid_list:
                        if start.isSmaller(row[17]) and end.isBigger(row[17]):
                            datetime_now = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S')
                            i = msid_list.index(row[0])
                            j = (datetime_now - start.date()).days
                            k = datetime.datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S').hour
                            A[i, j, k] = int(row[19])
                if counter % 20000 == 0:
                    print('Fortschritt: ', counter, " Einträge verarbeitet")
                counter +=1
            t_end = time.time()
            print(str(round((t_end - t_start), 1)), " Sekunden für ",counter, "Einträge")
        base = start.date()
        date_list = [base + datetime.timedelta(days=x) for x in range(J)]


        # Delete Weekends
        if exclude_weekends:
            idx = 0
            while idx < len(date_list):
                if date_list[idx].weekday()>=5:
                    date_list.remove(date_list[idx])
                    A = np.delete(A, idx, 1)
                else:
                    idx+=1

        # Delete Holidays
        if exclude_holidays:
            holiday_list = []
            with open("Feiertage_ZH_2020.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for lines in csv_reader:
                    holiday_list.append(datetime.datetime.strptime(lines[0], '%d.%m.%y'))
            idx = 0
            while idx < len(date_list):
                if date_list[idx] in holiday_list:
                    date_list.remove(date_list[idx])
                    A = np.delete(A, idx, 1)
                else:
                    idx += 1


        new_IdCube = IdCube(A, msid_list, date_list)

        pickle_outfile = open(pickle_file, 'wb')
        pickle.dump(new_IdCube, pickle_outfile)
        pickle_outfile.close()

    if debug:
        pickle_infile = open(pickle_file, 'rb')
        new_IdCube = pickle.load(pickle_infile)
        pickle_infile.close()

    return new_IdCube