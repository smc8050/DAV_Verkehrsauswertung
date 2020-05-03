import numpy as np
from datetime import datetime, date


class Timestamp:
    '''
        Class to read and store datetime read from the data csv
    '''
    def _convert(self, input_str):
        return datetime.strptime(input_str, '%Y-%m-%dT%H:%M:%S')

    def __init__(self, messungDatZeit):
        self.timestamp = self._convert(messungDatZeit)

    def isSmaller(self, input_str):
        return self.timestamp <= self._convert(input_str)

    def isBigger(self, input_str):
        return self.timestamp >= self._convert(input_str)

    def date(self):
        return self.timestamp


class IdCube:
    '''
        Datastructure to store output of read_csv function (dims: I,J,K : msid, day, hour)
    '''
    def __init__(self, A, msid_list, date_list):
        self.A = A
        self.msid_list = msid_list
        self.date_list = date_list
    
    def get_dayslice(self, interval):
        interval_matrix = self.A[:, :, interval[0]:interval[1]]
        return IdCube(interval_matrix, self.msid_list, self.date_list)

    def sum_days(self):
        return np.sum(self.A, 1), self.msid_list, self.date_list

    def sum_hours(self):
        return np.sum(self.A, 2), self.msid_list, self.date_list

    def save_cube(self, filename):
        np.savetxt(filename, self.A, delimiter=",")