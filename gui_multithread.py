import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
from dav_auswertung import DavAuswertung
from utils import Timestamp
import re

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
        self.save_path = ""
        self.csv_url = ""
        self.msid_list_path = ""
        self.start_date = ""
        self.end_date = ""

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        sshFile = "dav_gui.stylesheet"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
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

        # Check ASP/MSP boolean
        msp_asp = False
        if self.check_msp_asp.isChecked(): msp_asp = True

        # Check Input date Format
        if self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
            start_date = self.start_date_textbox.text() + "T00:00:00"
            end_date = self.end_date_textbox.text() + "T23:00:00"
            r = re.compile('[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$')
            if r.match(start_date) and r.match(end_date):
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
                                Timestamp(end_date), msp_asp)
                worker.signals.finished.connect(self.thread_complete)
                # Execute
                self.threadpool.start(worker)
            else:
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

    def initUI(self):
        self.setGeometry(200, 200, 430, 450)
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
        self.save_path_btn.setIcon(QtGui.QIcon("./gui_icons/document-save-2.png"))
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
        self.start_date_textbox.setText("2020-01-01")

        # End Datum
        self.end_label = QtWidgets.QLabel(self)
        self.end_label.setText("End Datum:")
        self.end_label.move(50, 190)
        self.end_label.adjustSize()

        self.end_date_textbox = QLineEdit(self)
        self.end_date_textbox.move(130, 190)
        self.end_date_textbox.resize(150, 20)
        self.end_date_textbox.setPlaceholderText("YYYY-MM-DD")
        self.end_date_textbox.setText("2020-01-05")

        self.check_msp_asp = QCheckBox("MSP/ASP Auswerten", self)
        self.check_msp_asp.move(50, 205)
        self.check_msp_asp.resize(320, 40)
        self.check_msp_asp.setChecked(True)

        # Select MSID List
        self.msid_path_btn = QtWidgets.QPushButton(self)
        self.msid_path_btn.setText("MSID Liste wählen")
        self.msid_path_btn.move(40, 240)
        self.msid_path_btn.resize(350, 50)
        self.msid_path_btn.clicked.connect(self.openFileNameDialog)
        # self.msid_path_btn.setStyleSheet("background-color: orange")
        self.msid_path_btn.setIcon(QtGui.QIcon("./gui_icons/txt.png"))
        self.msid_path_btn.setIconSize(QtCore.QSize(30, 30))

        # RUN Button
        self.run_btn = QtWidgets.QPushButton(self)
        self.run_btn.setText("Daten auswerten")
        self.run_btn.move(40, 295)
        self.run_btn.resize(350, 50)
        self.run_btn.clicked.connect(self.start_thread)
        self.run_btn.setEnabled(False)
        self.run_btn.setIcon(QtGui.QIcon("./gui_icons/download-2.png"))
        self.run_btn.setIconSize(QtCore.QSize(30, 30))


        # Running Label
        self.running_text = QtWidgets.QLabel(self)
        self.running_text.setText("Daten werden ausgewertet...")
        self.running_text.move(70, 350)
        self.running_text.adjustSize()
        self.running_text.setVisible(False)

        self.running_spinner = QtWidgets.QLabel(self)
        movie = QtGui.QMovie("./gui_icons/pacman.gif")
        movie.setScaledSize(QtCore.QSize(30, 30))
        self.running_spinner.setMovie(movie)
        self.running_spinner.move(42, 343)
        self.running_spinner.setVisible(False)
        movie.start()




        # Done Label
        self.done_text = QtWidgets.QLabel(self)
        self.done_text.setText("")
        self.done_text.move(70, 350)
        self.done_text.adjustSize()
        self.done_icon = QLabel(self)
        self.done_icon.setPixmap(QtGui.QPixmap("./gui_icons/dialog-ok-apply-6.png").scaled(20, 20, QtCore.Qt.KeepAspectRatio))
        self.done_icon.move(43, 343)
        self.done_icon.setVisible(False)


        # Quit Button
        self.quit_btn = QtWidgets.QPushButton(self)
        self.quit_btn.setText("Beenden")
        self.quit_btn.move(40, 370)
        self.quit_btn.resize(350, 50)
        self.quit_btn.clicked.connect(self.close)
        self.quit_btn.setIcon(QtGui.QIcon("./gui_icons/application-exit-2.png"))
        self.quit_btn.setIconSize(QtCore.QSize(30, 30))

        # Version Label
        self.version_label = QtWidgets.QLabel(self)
        self.version_label.setText("V0.21")
        self.version_label.move(200, 425)
        self.version_label.adjustSize()



def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


window()
