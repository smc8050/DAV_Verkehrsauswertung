import os
from abc import ABC, abstractmethod
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import bytespdate2num, num2date
import matplotlib.ticker as ticker
import csv
import pandas as pd
import numpy as np
from utils import IdCube
import math

"""Plotter which plots data in requested format (as passed by the arguments). It employs the strategy pattern."""

class PlotStrategy:
    """Base strategy class"""
    def __init__(self, root_dir, cube, do_plots, exclude_weekends, exclude_holidays):
        # Create foder structure if not existent in location root_dir
        self.root_dir = os.path.join(root_dir,'export_'+str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))
        self.sub_dir = self.root_dir
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        """
        self.sub_dir = os.path.join(self.root_dir, 'byDays')
        if not os.path.isdir(self.sub_dir):
            os.makedirs(self.sub_dir)
        """
        self.cube = cube
        self.do_plots = do_plots
        self.exclude_weekends = exclude_weekends
        self.exclude_holidays = exclude_holidays
        
        # Create string with observed time interval (used for subtitle)
        self.time_frame_title = 'Zeitraum: ' + cube.date_list[0].strftime('%d/%m/%Y')+' - '+ \
                                cube.date_list[-1].strftime('%d/%m/%Y')
        print("Cube has shape: {:}".format(cube.A.shape))
    
    @abstractmethod
    def plot(self):
        pass

    def _plot_curve(self, df, basename, title, subtitle, xlabel, plot_kind='line'):
        fig, ax = plt.subplots()
        if plot_kind == 'line':
            df.plot(ax=ax, kind=plot_kind, color=(0, 0.3, 0.7, 1), marker='h', \
                markerfacecolor='lightgreen', markeredgewidth=1, markersize=6, markevery=1)
        else:
            df.plot(ax=ax, kind=plot_kind, color=(0, 0.3, 0.7, 1))

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
        '''
        if plot_kind != "bar":
            ax.xaxis.set_major_locator(ticker.MultipleLocator(math.ceil(len(df.T)/10)))
        
        '''


        # Dates on xaxis are tilted for more room
        fig.autofmt_xdate()

        # Titles and labels
        fig.suptitle(title, weight='bold', fontsize=8)
        plt.xlabel(xlabel, labelpad=15, fontsize=7)
        plt.ylabel('AnzFahrzeuge', labelpad=15, fontsize=7)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)

        # Custom set texts
        plt.gcf().text(0.369, 0.91, subtitle, fontsize=7)
        if self.exclude_weekends:
            plt.gcf().text(0.85, 0.95, 'keine Wochenenden', fontsize=5)
        if self.exclude_holidays:
            plt.gcf().text(0.85, 0.92, 'keine Ferientage', fontsize=5)

        # Saving figure to respective location
        fig.savefig(basename+'.png', format='png', dpi=300)
        plt.close(fig)
        #plt.show()
    
    def _save_csv(self, df, basename):
        df.to_csv(basename+'.csv', sep=',')


class PlotterContext():
    """Context to which a strategy is stored and can be executed
    """
    def __init__(self, strategy: PlotStrategy) -> None:
        self._strategy = strategy
    
    @property
    def strategy(self) -> PlotStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PlotStrategy) -> None:
        self._strategy = strategy
    
    def plot(self) -> None:
        self._strategy.plot()
    

"""Default plotting strategy which just sums over the whole day / hours in interval
"""
class DefaultPlotter(PlotStrategy):
    def __init__(self, *inputs):
        super(DefaultPlotter, self).__init__(*inputs)
    
    def plot(self):
        print("Processing sorted by days:")
        slice, msid_list, date_list = self.cube.sum_hours()
        date_list = [d.date() for d in date_list]
        # Create dataframe to plot
        df = pd.DataFrame(data=slice, index=msid_list, columns=date_list)

        if self.do_plots:
            # Plotting type depending on the number of dates
            kind = 'bar' if len(date_list) < 25 else 'line'
            for index, row in df.iterrows():
                print(index)
                basename = os.path.join(self.sub_dir, index)
                # Uncomment to save csv of data used to generate a plot
                #self._save_csv(row, basename)
                plot_title = 'Tagessumme (MSID: '+index+')'
                self._plot_curve(row, basename, title=plot_title, subtitle=self.time_frame_title, xlabel='Datum', plot_kind=kind)

        # Save the whole slice to a csv
        self._save_csv(df, os.path.join(self.sub_dir,'tage_summe'))


"""Extends the functionality of DefaultPlotter by summing also \
    MSP (Morgenspitze) and ASP (Abendspitze)
"""
class ExtendedPlotter(PlotStrategy):
    def __init__(self, *inputs):
        super(ExtendedPlotter, self).__init__(*inputs)
        self.msp_interval = [6,9]
        self.asp_interval = [16,19]
        self.msp_cube = self.cube.get_dayslice(self.msp_interval)
        self.asp_cube = self.cube.get_dayslice(self.asp_interval)

    def plot(self):
        print("Processing sorted by days:")
        slice, msid_list, date_list = self.cube.sum_hours()
        msp_slice, _, _ = self.msp_cube.sum_hours()
        asp_slice, _, _ = self.asp_cube.sum_hours()

        date_list = [d.date() for d in date_list]

        # Create dataframe to plot
        df_total = pd.DataFrame(data=slice, index=msid_list, columns=date_list)
        df_msp = pd.DataFrame(data=msp_slice, index=msid_list, columns=date_list)
        df_asp = pd.DataFrame(data=asp_slice, index=msid_list, columns=date_list)

        if self.do_plots:
            # Plotting type depending on the number of dates
            kind = 'bar' if len(date_list) < 25 else 'line'
            for (index, row), (_, row_msp), (_, row_asp) in zip(df_total.iterrows(), df_msp.iterrows(), df_asp.iterrows()):
                print(index)
                basedir = os.path.join(self.sub_dir, index)
                os.makedirs(basedir)
                # Uncomment to save csv of data used to generate a plot
                plot_title = 'Tagessumme (MSID: '+index+')'
                self._plot_curve(row, basedir+'/gesamt_'+index, title=plot_title, subtitle=self.time_frame_title, xlabel='Datum', plot_kind=kind)

                time_interval = "{0:02d} - {1:02d} Uhr".format(*self.msp_interval)
                plot_title = 'Summe Morgenspitze '+time_interval+' (MSID: '+index+')'
                self._plot_curve(row_msp, basedir+'/msp_'+index, title=plot_title, subtitle=self.time_frame_title, xlabel='Datum', plot_kind=kind)

                time_interval = "{0:02d} - {1:02d} Uhr".format(*self.asp_interval)
                plot_title = 'Summe Abendspitze '+time_interval+' (MSID: '+index+')'
                self._plot_curve(row_asp, basedir+'/asp_'+index, title=plot_title, subtitle=self.time_frame_title, xlabel='Datum', plot_kind=kind)

        # Save the whole slice to a csv
        self._save_csv(df_total, os.path.join(self.sub_dir, 'tage_summe'))
        self._save_csv(df_msp, os.path.join(self.sub_dir, 'msp_summe'))
        self._save_csv(df_asp, os.path.join(self.sub_dir, 'asp_summe'))
