import numpy as np
from datetime import datetime, date

class Timestamp:
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

# class evaluate:
#
#     def sum_hours(self, matrix):
#         return np.sum(matrix, axis=2)
#
#     def sum_date(self, matrix):
#         return np.sum(matrix, axis=1)
#
#
# def plot_histogramm(A_flat, MSID_list):


def calculate_entries:
    msid_count = 180
    start_year = date(datetime.now().year, 1, 1)
    now = date.today()
    delta = now - start_year
    entries_count = msid_count * delta.days * 24 + datetime.now().hour * msid_count
    return entries_count



