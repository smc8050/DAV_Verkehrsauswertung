from read_CSV import read_csv
from utils import Timestamp

t0 = Timestamp('2020-01-01T00:00:00')
t1 = Timestamp('2020-01-03T00:00:00')
ID = ['Z033M002']

read_csv(ID, t0, t1)
