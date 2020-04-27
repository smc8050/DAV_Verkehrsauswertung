import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressBar, QCheckBox, QLineEdit
from dav_auswertung import DavAuswertung
from utils import Timestamp

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

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "MSID Liste wählen", "", "TXT Files (*.txt);;All Files (*)", options=options)
        if fileName:
            self.msid_list_path = fileName
            self.msid_path_btn.setStyleSheet("background-color: green")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date != "" and self.end_date != "":
                self.run_btn.setEnabled(True)

    def selectFolderDialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.save_path = folder_path
            self.save_path_btn.setStyleSheet("background-color: green")
            if self.save_path != "" and self.msid_list_path != "" and self.start_date != "" and self.end_date != "":
                self.run_btn.setEnabled(True)

    def run_calculation(self):

        if self.url_textbox.text() != "":
            self.csv_url = self.url_textbox.text()
        else:
            self.csv_url = "https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv"
        self.start_date = self.start_date_textbox.text()
        self.end_date = self.end_date_textbox.text()
        DavAuswertung(self.save_path, self.csv_url, self.msid_list_path, Timestamp(self.start_date), Timestamp(self.end_date))

    def initUI(self):
        self.setGeometry(200, 200, 430, 480)
        self.setWindowTitle("DAV Verkehrsauswertung")

        self.url_label = QtWidgets.QLabel(self)
        self.url_label.setText("URL zum Online CSV file (Leer lassen für CSV File von 2020):")
        self.url_label.move(50, 10)
        self.url_label.adjustSize()

        # URL Textbox
        self.url_textbox = QLineEdit(self)
        self.url_textbox.move(50, 30)
        self.url_textbox.resize(330, 20)
        self.url_textbox.setPlaceholderText("https://data.stadt-zuerich.ch/dataset/6212fd20-e816-4828-a67f-90f057f25ddb/resource/44607195-a2ad-4f9b-b6f1-d26c003d85a2/download/sid_dav_verkehrszaehlung_miv_od2031_2020.csv")

        # Save Path Button
        self.save_path_btn = QtWidgets.QPushButton(self)
        self.save_path_btn.setText("Speicherort wählen")
        self.save_path_btn.move(40, 60)
        self.save_path_btn.resize(350, 50)
        self.save_path_btn.clicked.connect(self.selectFolderDialog)
        self.save_path_btn.setStyleSheet("background-color: orange")

        # Datumsformat Hinweis
        self.remark_label = QtWidgets.QLabel(self)
        self.remark_label.setText("Start und End Datum eingeben (Format beachten):")
        self.remark_label.move(50, 120)
        self.remark_label.adjustSize()
        self.remark_label.setWordWrap(True)

        # Start Datum
        self.start_label = QtWidgets.QLabel(self)
        self.start_label.setText("Start Datum:")
        self.start_label.move(50, 145)
        self.start_label.adjustSize()

        self.start_date_textbox = QLineEdit(self)
        self.start_date_textbox.move(130, 145)
        self.start_date_textbox.resize(150, 20)
        self.start_date_textbox.setPlaceholderText("2020-01-01T12:30:00")

        # End Datum
        self.end_label = QtWidgets.QLabel(self)
        self.end_label.setText("End Datum:")
        self.end_label.move(50, 170)
        self.end_label.adjustSize()

        self.end_date_textbox = QLineEdit(self)
        self.end_date_textbox.move(130, 170)
        self.end_date_textbox.resize(150, 20)
        self.end_date_textbox.setPlaceholderText("2020-01-01T12:30:00")

        # Select MSID List
        self.msid_path_btn = QtWidgets.QPushButton(self)
        self.msid_path_btn.setText("MSID Liste wählen")
        self.msid_path_btn.move(40, 200)
        self.msid_path_btn.resize(350, 50)
        self.msid_path_btn.clicked.connect(self.openFileNameDialog)
        self.msid_path_btn.setStyleSheet("background-color: orange")

        # RUN Button
        self.run_btn = QtWidgets.QPushButton(self)
        self.run_btn.setText("Daten auswerten")
        self.run_btn.move(40, 250)
        self.run_btn.resize(350, 50)
        self.run_btn.clicked.connect(self.run_calculation)
        self.run_btn.setEnabled(True)

        # progress Bar
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(45, 300, 340, 25)

        # Progress Label
        self.progress_label = QtWidgets.QLabel(self)
        self.progress_label.setText("-/-")
        self.progress_label.move(55, 320)
        self.progress_label.adjustSize()

        # estimated Time
        self.estimated_time = QtWidgets.QLabel(self)
        self.estimated_time.setText("Verbleibende Zeit: -")
        self.estimated_time.move(55, 340)
        self.estimated_time.adjustSize()

        # Quit Button
        self.quit_btn = QtWidgets.QPushButton(self)
        self.quit_btn.setText("Beenden")
        self.quit_btn.move(40, 380)
        self.quit_btn.resize(350, 50)
        self.quit_btn.clicked.connect(self.close)


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


window()
