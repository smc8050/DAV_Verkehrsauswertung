import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import pandas as pd
from utils import IdCube

class Plotter:
    def __init__(self, root_dir, cube):
        self.root_dir = 'export_'+str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.sub_dirs = [self.root_dir+'/byDays', self.root_dir+'/byHours']
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        for dir in self.sub_dirs:
            if not os.path.isdir(dir):
                os.makedirs(dir)
        self.cube = cube

        self.time_interval = cube.date_list[0].strftime('%d/%m/%Y')+' - '+ \
                            cube.date_list[-1].strftime('%d/%m/%Y')
        print("Cube has shape: {:}".format(cube.A.shape))


    def _plot_row(self, df, basename, title, xlabel):
        fig, ax = plt.subplots()
        df.plot(ax=ax,kind='bar', color=(0.1, 1, 1, 1))

        # Formatting of graph
        plt.rcParams['axes.edgecolor']='#333F4B'
        plt.rcParams['axes.linewidth']=0.8
        plt.rcParams['xtick.color']='#333F4B'
        plt.rcParams['ytick.color']='#333F4B'
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color='#EEEEEE')
        ax.xaxis.grid(False)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.tick_params(left=False)

        fig.autofmt_xdate()

        fig.suptitle(title, weight='bold', fontsize=8)
        plt.xlabel(xlabel, labelpad=15, fontsize=7)
        plt.ylabel('AnzFahrzeuge', labelpad=15, fontsize=7)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        fig.savefig(basename+'.png', format='png', dpi=300)

    def _save_csv(self, df, basename):
        df.to_csv(basename+'.csv', sep=',')

    def plot_days(self):
        print("Processing sorted by days:")
        slice, msid_list, date_list = self.cube.sum_hours()
        date_list = [d.date() for d in date_list]
        # Create dataframe to plot
        df = pd.DataFrame(data=slice, index=msid_list, columns=date_list)
        for index, row in df.iterrows():
            print(index)
            #row = df.iloc[index]
            basename = os.path.join(self.sub_dirs[0], index)
            #self._save_csv(row, basename)
            plot_title = 'Tagessumme (MSID: '+index+')\n\nZeitraum: '+self.time_interval
            self._plot_row(row, basename, title=plot_title ,xlabel='Datum')
        
        # Save the whole slice to a csv
        self._save_csv(df, os.path.join(self.sub_dirs[0],'tage_summe'))

    def plot_hours(self):
        print("Processing sorted by days:")
        slice, msid_list, date_list = self.cube.sum_days()
        num_days = len(date_list)
        hour_list = 24*[0]
        for i in range(24):
            hour_list[i] = str(i)+':00'
            if i < 10:
                hour_list[i] = '0'+hour_list[i]
        # Create dataframe to plot and divide by the number of days summed
        # to obtain the average frequence
        df = pd.DataFrame(data=slice, index=msid_list, columns=hour_list).div(num_days)
        for index, row in df.iterrows():
            print(index)
            basename = os.path.join(self.sub_dirs[1], index)
            #self._save_csv(row, basename)
            plot_title = 'Tagessumme Durchschnitt (MSID: '+index+')\n\nZeitraum: '+self.time_interval
            self._plot_row(row, basename, title=plot_title ,xlabel='Tageszeit')
        
        # Save the whole slice to a csv
        self._save_csv(df, os.path.join(self.sub_dirs[1],'stunden_durchschnitt'))