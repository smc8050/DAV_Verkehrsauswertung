import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressBar, QLineEdit, QMessageBox
from dav_auswertung import DavAuswertung
from utils import Timestamp
import re
import os


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        QApplication.processEvents()  # update GUI while running functions
        self.save_path = ""
        self.csv_url = ""
        self.msid_list_path = ""
        self.start_date = ""
        self.end_date = ""


        # sshFile = "dav_gui.stylesheet"
        # with open(sshFile, "r") as fh:
        #     self.setStyleSheet(fh.read())

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "MSID Liste wählen", "", "TXT Files (*.txt);;All Files (*)", options=options)
        if fileName:
            self.msid_list_path = fileName
            self.msid_path_btn.setStyleSheet("background-color: green")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
                self.run_btn.setEnabled(True)

    def selectFolderDialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.save_path = folder_path
            self.save_path_btn.setStyleSheet("background-color: green")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":
                self.run_btn.setEnabled(True)

    def run_calculation(self):
        # Check Input URL
        if self.url_textbox.text() != "":
            self.csv_url = self.url_textbox.text()
        else:
            self.csv_url = "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv"

        #Check Input date Format
        if self.start_date_textbox.text() != "" and self.end_date_textbox.text() != "":

            start_date = self.start_date_textbox.text() + "T00:00:00"
            end_date = self.end_date_textbox.text() + "T23:00:00"
            r = re.compile('[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$')
            if r.match(start_date) and r.match(end_date):

                self.run_btn.setStyleSheet("background-color: orange")
                self.run_btn.setText("Daten werden geladen...")
                self.run_btn.setEnabled(False)
                QApplication.processEvents()

                DavAuswertung(self.save_path, self.csv_url, self.msid_list_path, Timestamp(start_date),
                              Timestamp(end_date))

                self.run_btn.setStyleSheet("background-color: green")
                self.run_btn.setEnabled(True)
                self.run_btn.setText("Daten erneut auswerten")
                self.runing_label.setText("Daten sind ausgewertet!")
                self.runing_label.adjustSize()
                QApplication.processEvents()
            else:
                self.error_msg()


    def error_msg(text):
        msg = QMessageBox()
        msg.setGeometry(215, 250, 100, 100)
        msg.setBaseSize(400,150)
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
        self.url_textbox.setPlaceholderText("https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv")

        # Save Path Button
        self.save_path_btn = QtWidgets.QPushButton(self)
        self.save_path_btn.setText("Speicherort wählen")
        self.save_path_btn.move(40, 80)
        self.save_path_btn.resize(350, 50)
        self.save_path_btn.clicked.connect(self.selectFolderDialog)
        self.save_path_btn.setStyleSheet("background-color: orange")

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

        # End Datum
        self.end_label = QtWidgets.QLabel(self)
        self.end_label.setText("End Datum:")
        self.end_label.move(50, 190)
        self.end_label.adjustSize()

        self.end_date_textbox = QLineEdit(self)
        self.end_date_textbox.move(130, 190)
        self.end_date_textbox.resize(150, 20)
        self.end_date_textbox.setPlaceholderText("YYYY-MM-DD")

        # Select MSID List
        self.msid_path_btn = QtWidgets.QPushButton(self)
        self.msid_path_btn.setText("MSID Liste wählen")
        self.msid_path_btn.move(40, 220)
        self.msid_path_btn.resize(350, 50)
        self.msid_path_btn.clicked.connect(self.openFileNameDialog)
        self.msid_path_btn.setStyleSheet("background-color: orange")

        # RUN Button
        self.run_btn = QtWidgets.QPushButton(self)
        self.run_btn.setText("Daten auswerten")
        self.run_btn.move(40, 275)
        self.run_btn.resize(350, 50)
        self.run_btn.clicked.connect(self.run_calculation)
        self.run_btn.setEnabled(False)

        # Running Label
        self.runing_label = QtWidgets.QLabel(self)
        self.runing_label.setText("")
        self.runing_label.move(50, 330)
        self.runing_label.adjustSize()

        # Quit Button
        self.quit_btn = QtWidgets.QPushButton(self)
        self.quit_btn.setText("Beenden")
        self.quit_btn.move(40, 350)
        self.quit_btn.resize(350, 50)
        self.quit_btn.clicked.connect(self.close)


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())



window()
