import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from dav_auswertung import DavAuswertung
from utils import Timestamp
import re, glob, os, datetime

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    '''
    finished = pyqtSignal()
    error_exit = pyqtSignal()

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        self.fn(*self.args)
        self.signals.finished.emit()  # Done


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()

        # Helper function for debugging
        debug = True

        if debug:
            self.debug_helper()
        else:
            self.save_path = ""
            self.csv_url = ""
            self.msid_list_path = ""
            self.start_date = ""
            self.end_date = ""

        self.threadpool = QThreadPool() #Initialize threadpool

        #load stylesheet
        sshFile = "dav_gui.stylesheet"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog # <- uncomment for fancier dialog
        fileName, _ = QFileDialog.getOpenFileName(self, "MSID Liste wählen", "", "TXT Files (*.txt);;All Files (*)",
                                                options=options)
        if fileName:
            self.msid_list_path = fileName
            self.msid_path_btn.setStyleSheet("background-color: LightGreen")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
                self.run_btn.setEnabled(True)

    def selectFolderDialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.save_path = folder_path
            self.save_path_btn.setStyleSheet("background-color: LightGreen")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
                self.run_btn.setEnabled(True)

    #returns list with all paths and its names from txt files in selected directory
    def selectMSIDGroups(self):
        MSID_Groups_folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if MSID_Groups_folder:
            os.chdir(MSID_Groups_folder)
            MSID_group_paths = glob.glob(MSID_Groups_folder + '/*.txt')
            filenames = glob.glob('*.txt')
            MSID_group_names = []
            for names in filenames: MSID_group_names.append(os.path.splitext(names)[0])
            print(MSID_group_paths)
            print(MSID_group_names)
        return MSID_group_paths, MSID_group_names


    def thread_complete(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Daten erneut auswerten")
        self.done_text.setText("Daten sind ausgewertet!")
        self.done_text.setVisible(True)
        self.done_text.adjustSize()
        self.running_spinner.setVisible(False)
        self.running_text.setVisible(False)
        self.done_icon.setVisible(True)
        print("THREAD COMPLETE!")

    def start_thread(self):

        # Check Input URL
        if self.url_textbox.text() != "":
            self.csv_url = self.url_textbox.text()
        else:
            self.csv_url = "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv"

        # Check msp_asp boolean and set value
        msp_asp = False
        if self.check_msp_asp.isChecked(): msp_asp = True

        # Check do_plots boolean and set value
        do_plots = False
        if self.check_do_plots.isChecked(): do_plots = True

        # Check exclude_weekends boolean and set value
        exclude_weekends = True
        if self.check_weekends.isChecked(): exclude_weekends = False

        # Check exclude_holidays boolean and set value
        exclude_holidays = True
        if self.check_holidays.isChecked(): exclude_holidays = False

        # Check Input date Format
        if self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
            start_date = self.start_date_textbox.text() + "T00:00:00"
            end_date = self.end_date_textbox.text() + "T23:00:00"
            r = re.compile('[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$')
            if r.match(start_date) and r.match(end_date):

                #prepare GUI for loading
                self.run_btn.setText("Daten werden geladen...")
                self.run_btn.setEnabled(False)
                self.running_spinner.setVisible(True)
                self.running_text.setVisible(True)
                self.done_icon.setVisible(False)
                self.done_text.setVisible(False)

                # Pass the function and its arguments to execute
                save_path = self.save_path
                csv_url = self.csv_url
                msid_list_path = self.msid_list_path
                worker = Worker(DavAuswertung, save_path, csv_url, msid_list_path, Timestamp(start_date),
                                Timestamp(end_date), msp_asp, do_plots, exclude_weekends, exclude_holidays)
                worker.signals.finished.connect(self.thread_complete)
                # Execute in second thread
                print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
                print("Thread started...")
                self.threadpool.start(worker)
            else:
                self.error_msg()
                self.run_btn.setEnabled(True)

    def error_msg(text):
        msg = QMessageBox()
        msg.setGeometry(215, 250, 100, 100)
        msg.setBaseSize(400, 150)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Datumsformat-Fehler")
        msg.setInformativeText('Das Datum hat nicht folgendes Format:\nYYYY-MM-DD, z.B. 2020-01-31')
        msg.setWindowTitle("Format-Fehler")
        msg.exec_()

    def debug_helper(self):
        self.save_path = "/Users/steivanclagluna/Documents/Coding/Python/DAV_Verkehrsauswertung/GIT"
        self.msid_list_path = "/Users/steivanclagluna/Documents/Coding/Python/DAV_Verkehrsauswertung/GIT/MSID_Input.txt"
        self.start_date_textbox.setText("2020-01-01")
        self.end_date_textbox.setText("2020-01-10")
        self.msid_path_btn.setStyleSheet("background-color: LightGreen")
        self.save_path_btn.setStyleSheet("background-color: LightGreen")
        self.run_btn.setEnabled(True)

    def quickfill_start(self):
        d = datetime.date.today()
        year_str = '{:04d}'.format(d.year)
        month_str = '01'
        day_str = '01'
        self.start_date_textbox.setText(year_str+"-"+month_str+"-"+day_str)

    def quickfill_end(self):
        d = datetime.date.today()
        year_str = '{:04d}'.format(d.year)
        month_str = '{:02d}'.format(d.month)
        day_str = '{:02d}'.format(d.day)
        self.end_date_textbox.setText(year_str + "-" + month_str + "-" + day_str)

    def initUI(self):

        # deploy parameter
        deploy = False
        if deploy:
            self.gui_icon_folder = ""
        else:
            self.gui_icon_folder = "gui_icons/"

        self.setGeometry(200, 200, 430, 470)
        self.setWindowTitle("DAV Verkehrsauswertung")
        self.url_label = QtWidgets.QLabel(self)
        self.url_label.setText("URL zum Online CSV file\n(Leer lassen für Daten von 2020):")
        self.url_label.move(50, 10)
        self.url_label.adjustSize()

        # URL Textbox
        self.url_textbox = QLineEdit(self)
        self.url_textbox.move(50, 50)
        self.url_textbox.resize(330, 20)
        self.url_textbox.setPlaceholderText(
            "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv")

        # Save Path Button
        self.save_path_btn = QtWidgets.QPushButton(self)
        self.save_path_btn.setText("Speicherort wählen")
        self.save_path_btn.move(40, 80)
        self.save_path_btn.resize(350, 50)
        self.save_path_btn.clicked.connect(self.selectFolderDialog)
        self.save_path_btn.setIcon(QtGui.QIcon("./"+self.gui_icon_folder+"document-save-2.png"))
        self.save_path_btn.setIconSize(QtCore.QSize(30, 30))

        # Datumsformat Hinweis
        self.remark_label = QtWidgets.QLabel(self)
        self.remark_label.setText("Start und End Datum eingeben (Format beachten):")
        self.remark_label.move(50, 140)
        self.remark_label.adjustSize()
        self.remark_label.setWordWrap(True)

        # Start Datum
        self.start_label = QtWidgets.QLabel(self)
        self.start_label.setText("Start Datum:")
        self.start_label.move(50, 165)
        self.start_label.adjustSize()

        self.start_date_textbox = QLineEdit(self)
        self.start_date_textbox.move(130, 165)
        self.start_date_textbox.resize(150, 20)
        self.start_date_textbox.setPlaceholderText("YYYY-MM-DD")

        # Start Datum Quickfill Button
        self.start_date_quickfill_btn = QtWidgets.QPushButton(self)
        self.start_date_quickfill_btn.setText("Jahresbeginn")
        self.start_date_quickfill_btn.move(290, 164)
        self.start_date_quickfill_btn.resize(100, 22)
        self.start_date_quickfill_btn.clicked.connect(self.quickfill_start)

        # End Datum
        self.end_label = QtWidgets.QLabel(self)
        self.end_label.setText("End Datum:")
        self.end_label.move(50, 190)
        self.end_label.adjustSize()

        self.end_date_textbox = QLineEdit(self)
        self.end_date_textbox.move(130, 190)
        self.end_date_textbox.resize(150, 20)
        self.end_date_textbox.setPlaceholderText("YYYY-MM-DD")

        # End Datum Quickfill Button
        self.end_date_quickfill_btn = QtWidgets.QPushButton(self)
        self.end_date_quickfill_btn.setText("Heute")
        self.end_date_quickfill_btn.move(290, 189)
        self.end_date_quickfill_btn.resize(100, 22)
        self.end_date_quickfill_btn.clicked.connect(self.quickfill_end)

        # MSP/ASP checkbox
        self.check_msp_asp = QCheckBox("MSP/ASP auswerten", self)
        self.check_msp_asp.move(50, 205)
        self.check_msp_asp.resize(320, 40)
        self.check_msp_asp.setChecked(True)

        # Do plots checkbox
        self.check_do_plots = QCheckBox("Graphen erstellen", self)
        self.check_do_plots.move(240, 205)
        self.check_do_plots.resize(320, 40)
        self.check_do_plots.setChecked(True)

        # Exclude weekends checkbox
        self.check_weekends = QCheckBox("Wochenenden auswerten", self)
        self.check_weekends.move(50, 225)
        self.check_weekends.resize(320, 40)
        self.check_weekends.setChecked(False)

        # Exclude holidays checkbox
        self.check_holidays = QCheckBox("Ferientage auswerten", self)
        self.check_holidays.move(240, 225)
        self.check_holidays.resize(320, 40)
        self.check_holidays.setChecked(False)

        # Select MSID List
        self.msid_path_btn = QtWidgets.QPushButton(self)
        self.msid_path_btn.setText("MSID Liste wählen")
        self.msid_path_btn.move(40, 260)
        self.msid_path_btn.resize(350, 50)
        self.msid_path_btn.clicked.connect(self.openFileNameDialog)
        self.msid_path_btn.setIcon(QtGui.QIcon("./"+self.gui_icon_folder+"txt.png"))
        self.msid_path_btn.setIconSize(QtCore.QSize(30, 30))

        # RUN Button
        self.run_btn = QtWidgets.QPushButton(self)
        self.run_btn.setText("Daten auswerten")
        self.run_btn.move(40, 315)
        self.run_btn.resize(350, 50)
        self.run_btn.clicked.connect(self.start_thread)
        self.run_btn.setEnabled(False)
        self.run_btn.setIcon(QtGui.QIcon("./download-2.png"))
        self.run_btn.setIconSize(QtCore.QSize(30, 30))

        # Running Label
        self.running_text = QtWidgets.QLabel(self)
        self.running_text.setText("Daten werden ausgewertet")
        self.running_text.move(42, 370)
        self.running_text.adjustSize()
        self.running_text.setVisible(False)

        self.running_spinner = QtWidgets.QLabel(self)
        movie = QtGui.QMovie("./"+self.gui_icon_folder+"pacman_blue.gif")
        movie.setScaledSize(QtCore.QSize(30, 30))
        self.running_spinner.setMovie(movie)
        self.running_spinner.move(210, 363)
        self.running_spinner.setVisible(False)
        movie.start()

        # Done Label
        self.done_text = QtWidgets.QLabel(self)
        self.done_text.setText("")
        self.done_text.move(70, 370)
        self.done_text.adjustSize()
        self.done_icon = QLabel(self)
        self.done_icon.setPixmap(QtGui.QPixmap("./"+self.gui_icon_folder+"dialog-ok-apply-6.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        self.done_icon.move(43, 363)
        self.done_icon.setVisible(False)

        # Quit Button
        self.quit_btn = QtWidgets.QPushButton(self)
        self.quit_btn.setText("Beenden")
        self.quit_btn.move(40, 390)
        self.quit_btn.resize(350, 50)
        self.quit_btn.clicked.connect(self.close)
        self.quit_btn.setIcon(QtGui.QIcon("./"+self.gui_icon_folder+"application-exit-2.png"))
        self.quit_btn.setIconSize(QtCore.QSize(30, 30))

        # Version Label
        self.version_label = QtWidgets.QLabel(self)
        self.version_label.setText("V0.22.1")
        self.version_label.move(0, 445)
        self.version_label.resize(430, 20)
        self.version_label.setAlignment(Qt.AlignCenter)


def window():

    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


window()
