from read_CSV import read_csv
from plot import Plotter

class DavAuswertung:
    '''
        Main action class, loads data from online CSV and plots data
    '''

    def __init__(self, save_path, csv_url ,msid_list_path,start_date,end_date, msp_asp):
        result_IdCube = read_csv(msid_list_path, start_date, end_date, csv_url)
        pl = Plotter(save_path, result_IdCube)
        pl.plot_days()
        pl.plot_hours()