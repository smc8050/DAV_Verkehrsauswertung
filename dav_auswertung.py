from read_CSV import read_csv
from plot import PlotterContext, DefaultPlotter, ExtendedPlotter

class DavAuswertung:
    '''
        Main action class, loads data from online CSV and plots data
    '''

    def __init__(self, save_path, csv_url ,msid_list_path,start_date,end_date, msp_asp, do_plots, exclude_weekends, exclude_holidays):
        result_IdCube = read_csv(msid_list_path, start_date, end_date, csv_url, exclude_weekends, exclude_holidays)
        if msp_asp:
            pl = PlotterContext(ExtendedPlotter(save_path, result_IdCube, do_plots, exclude_weekends, exclude_holidays))
        else:
            pl = PlotterContext(DefaultPlotter(save_path, result_IdCube, do_plots, exclude_weekends, exclude_holidays))

        pl.plot()