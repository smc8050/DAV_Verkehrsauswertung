import os
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import pandas as pd
from utils import IdCube

class Plotter:
    def __init__(self, root_dir, cube):
        self.root_dir = 'export-'+str(date.today())
        self.sub_dirs = [self.root_dir+'/byDays', self.root_dir+'/byHours']
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        for dir in self.sub_dirs:
            if not os.path.isdir(dir):
                os.makedirs(dir)
        #self.today = date
        self.cube = cube
        self.time_interval = cube.date_list[0].strftime('%m/%d/%Y')+' - '+ \
                            cube.date_list[-1].strftime('%m/%d/%Y')

        print("Cube has shape: {:}".format(cube.A.shape))


    def _plot_row(self, df, filename, title, xlabel):
        fig, ax = plt.subplots()
        df.plot(ax=ax,kind='bar')
        fig.autofmt_xdate()
        #plt.show()
        fig.suptitle(title, fontsize=8)
        plt.xlabel(xlabel, fontsize=7)
        plt.ylabel('AnzFahrzeuge', fontsize=7)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        fig.savefig(filename, format='png', dpi=300)

    def _save_csv(df, filename):
        pass

    def plot_days(self):
        slice, msid_list, date_list = self.cube.sum_hours()
        date_list = [d.date() for d in date_list]
        # Create dataframe to plot
        df = pd.DataFrame(data=slice, index=msid_list, columns=date_list)
        for index, row in df.iterrows():
            print(index)
            #row = df.iloc[index]
            filename = os.path.join(self.sub_dirs[0], index+'.png')
            plot_title = 'Tagessumme (MSID: '+index+')\n\nZeitraum: '+self.time_interval
            self._plot_row(row, filename, title=plot_title ,xlabel='Datum')

    def plot_hours(self):
        slice, msid_list, date_list = self.cube.sum_days()
        hour_list = [str(i)+':00' for i in range(24)]
        # Create dataframe to plot
        df = pd.DataFrame(data=slice, index=msid_list, columns=hour_list)
        for index, row in df.iterrows():
            print(index)
            #print(type(row))
            #row = df.iloc[index]
            filename = os.path.join(self.sub_dirs[1], index+'.png')
            plot_title = 'Tagessumme (MSID: '+index+')\n\nZeitraum: '+self.time_interval
            self._plot_row(row, filename, title=plot_title ,xlabel='Tageszeit')