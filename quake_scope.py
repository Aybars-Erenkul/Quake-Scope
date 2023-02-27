import requests
import bs4
import time
import sys, signal
import webbrowser
import os
from gtts import gTTS
from threading import Thread
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QListWidget, QPushButton, QLabel
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QThread, QThreadPool,QObject,QRunnable, pyqtSignal, pyqtSlot


class Signals(QObject):
    started = pyqtSignal(int)
    completed = pyqtSignal(int)

class Worker(QRunnable):

    def __init__(self):
        super().__init__()
        self.n = 1
        self.signals = Signals()


    @pyqtSlot()
    def run(self):
        while(True):
            self.signals.started.emit(self.n)
            time.sleep(15)
            self.signals.completed.emit(self.n)
     
             

job_count = 0
latest_time = ''


class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Quake Scope")
        widget = QWidget()
        widget.setLayout(QGridLayout())
        self.setCentralWidget(widget)
        self.setGeometry(600, 300, 650, 400)


        self.btn_start = QPushButton('Scan', clicked = self.start_jobs)
        self.list = QListWidget()
        self.label = QLabel('「quakeScope」')

        self.authorLabel = QLabel('by Aybars Erenkul')
        self.authorLabel.mousePressEvent = self.open_author_page

        listFont = QFont("Lucida Fax", 10)
        listFont.setBold(True)
        self.list.setFont(QFont(listFont))
        self.label.setFont(QFont('Imprint MT Shadow', 28))
        self.authorLabel.setFont(QFont('Lucida Sans', 8))

        widget.layout().addWidget(self.label,0,2, alignment = Qt.AlignmentFlag.AlignCenter )
        widget.layout().addWidget(self.authorLabel,0,3)
        widget.layout().addWidget(self.list, 1, 0, 3, 5)
        widget.layout().addWidget(self.btn_start,4,2)

        self.show()

    
    def open_author_page(self, event):
        browser = webbrowser.get()
        browser.open_new('https://github.com/Aybars-Erenkul')



    def start_jobs(self):
        global job_count
        
        if job_count == 0:
            pool = QThreadPool.globalInstance()
            worker = Worker()
            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            pool.start(worker)
        else:
            self.scan_quakes()
        job_count += 1

    def closeEvent(self, event):
        print ("Closing..")
        event.accept()

    def start(self):
        self.scan_quakes()

    def complete(self):
        print("A job is Complete")

    def scan_quakes(self):
        self.list.clear()

        res = requests.get("http://www.koeri.boun.edu.tr/sismo/2/son-depremler/otomatik-cozumler/")

        soup = bs4.BeautifulSoup(res.text, 'lxml')

        latest = soup.select(".newsticker li")

        latest_five_list = list(latest)
        latest_five_list.pop()
        latest_five_list.pop()
        self.list.addItem('\n')
        for i in range(len(latest_five_list)):
            self.list.addItem('\n' + latest_five_list[i].getText())
            print(latest_five_list[i].getText())

        text_formatted = latest_five_list[0].getText().split()
        
        print (text_formatted)

        for item in range(len(text_formatted)):
            if text_formatted[item] == '(KAHRAMANMARAS)':
                text_formatted[item] = 'Kahramanmaraş'
            elif text_formatted[item] == '(ADIYAMAN)':
                text_formatted[item] = "AdIyaman"
            elif text_formatted[item] == '(GAZIANTEP)':
                text_formatted[item] = "Gaziantep"
            elif text_formatted[item] == '(IZMIR)':
                text_formatted[item] = ' izmir'
            elif text_formatted[item] == '(DENIZLI)':
                text_formatted[item] = ' denizli'
        if text_formatted[6] == '(GAZIANTEP)':
            ek = 'te'
        else:
            ek = 'da'

        text_almost_ready = text_formatted[0] + text_formatted[1] + "önçe" + text_formatted[3] + "büyüklüğünde" + str(text_formatted[6]) + ek + ' deprem oldu.' 


        print (text_almost_ready)

        text_ready = str(text_almost_ready)

        myobj = gTTS(text = text_ready, lang = 'tr', slow = False)
        myobj.save('deneme.mp3')
        global latest_time

        if latest_time != text_formatted[8]:
            os.system('start deneme.mp3')
            latest_time = text_formatted[8]
        else:
            pass
        




app = QApplication(sys.argv)
app.aboutToQuit.connect(Worker().signals.completed.disconnect)
window = MainWindow()
window.show()

sys.exit(app.exec())
    