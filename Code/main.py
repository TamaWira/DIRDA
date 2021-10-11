from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction, QMainWindow, QSlider, QPushButton, QToolTip, QApplication, QTableWidgetItem
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

import os
import re
import math
import pandas as pd

class Ui_MainWindow(QMainWindow):
    
    def __init__(self):

        QMainWindow.__init__(self)
        loadUi('gui.ui', self)

        # Declare Variables
        self.counter = 1
        self.listFile = [] # List file full path
        self.split_words = [] # Tokenized words
        self.list_stopwords = [] # kamus stopwords
        self.stopped_words = [] # stopped words
        self.stemmed_words = [] # stemmed words

        self.file_tampil = [] # for process
        self.split_tampil = [] # for process
        self.stop_tampil = [] # for process
        self.stem_tampil = [] # for process

        self.counter = 1

        # Link Widgets
        self.btnAddFile.clicked.connect(self.doAll)
        self.btnTf.clicked.connect(self.tf_idf)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.label.setText(_translate("MainWindow", "Original"))
        self.label_2.setText(_translate("MainWindow", "Tokenize"))
        self.label_3.setText(_translate("MainWindow", "Stopwords"))
        self.label_4.setText(_translate("MainWindow", "Stemming"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Preprocessing"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Incidence Index"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Inverted Index"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tf-Idf"))

    def openFile(self):

        # Open File
        self.fileName, fileType = QFileDialog.getOpenFileName(self.centralwidget, "Open File", "", "*.txt;;All Files(*)")
        if self.fileName not in self.listFile:
            self.listFile.append(self.fileName)

            filename = os.path.basename(self.fileName)
            self.file_tampil.append(filename)
            self.listOpenedDocument.addItem('{}. {}'.format(self.counter, filename))

            self.counter += 1

    def showOriginal(self):
        self.listDocOri.addItem('>>> {} :'.format(os.path.basename(self.fileName)))
        with open(self.fileName, 'r') as namaFile:
            for content in namaFile:
                self.listDocOri.addItem('{}\n'.format(content))

    def tokenize(self):

        # Tokenizing words
        with open(self.fileName, 'r') as namaFile:
            for content in namaFile:
                content = content.lower()
                content = re.split(r'\W+', content)
                
                self.split_words.extend(content)
                self.split_words = list(dict.fromkeys(self.split_words))

                self.split_tampil.extend(content)
                self.split_tampil = list(dict.fromkeys(self.split_tampil))
    
        self.listDocToken.addItem('>>> {} :'.format(os.path.basename(self.fileName)))
        self.listDocToken.addItem('{}\n'.format(str(self.split_tampil)))

    def removeStopwords(self):

        # Stopwords
        stopwords_path = 'stopwords_pilkada.csv'

        df = pd.read_csv(stopwords_path)
        for item in df['ada']:
            self.list_stopwords.append(item)
        
        self.stopped_words = self.split_words
        self.stop_tampil = self.split_tampil

        for x in self.stopped_words[:]:
            if x in self.list_stopwords[:]:
                self.stopped_words.remove(x)
                self.stop_tampil.remove(x)
        
        self.listDocStop.addItem('>>> {} :'.format(os.path.basename(self.fileName)))
        self.listDocStop.addItem('{}\n'.format(str(self.stop_tampil)))

    def stemming(self):

        # Stemming
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()

        for item in self.stopped_words:
            stemming = stemmer.stem(item)
            self.stemmed_words.append(stemming)
        
        for item in self.stop_tampil:
            stemming = stemmer.stem(item)
            self.stem_tampil.append(stemming)
            
        self.stemmed_words = list(dict.fromkeys(self.stemmed_words))

        self.stem_tampil = list(dict.fromkeys(self.stem_tampil))

        self.listDocStem.addItem('>>> {} :'.format(os.path.basename(self.fileName)))
        self.listDocStem.addItem('{}\n'.format(str(self.stem_tampil)))

        self.split_tampil.clear()
        self.stop_tampil.clear()
        self.stem_tampil.clear()

    def printIncidence(self):

        self.items_clear()

        panjang_col = len(self.listFile)
        panjang_row = len(self.split_words)

        self.tableWidget.setColumnCount(panjang_col)
        self.tableWidget.setRowCount(panjang_row)

        self.tableWidget.setHorizontalHeaderLabels(self.file_tampil)
        self.tableWidget.setVerticalHeaderLabels(self.stemmed_words)

        for x in range(len(self.split_words)):
            for y in range(len(self.file_tampil)):
                with open(self.listFile[y], 'r') as openFile:
                    for content in openFile:
                        if self.split_words[x] in content.lower():
                            self.tableWidget.setItem(x, y, QTableWidgetItem('<<1>>'))
                        else:
                            self.tableWidget.setItem(x, y, QTableWidgetItem('0'))

    def printInverted(self):

        # Printing
        self.listInverted.clear()

        for item in range(len(self.stopped_words)):
            exist_file = list()
            for data in self.listFile:
                with open(data, 'r') as namaFile:
                    for isi in namaFile:
                        isi = isi.lower()
                        if self.stopped_words[item] in isi:
                            exist_file.append(os.path.basename(data))
                            exist_file = list(dict.fromkeys(exist_file))
            self.listInverted.addItem('{}\t: <{}>'.format(self.stemmed_words[item], exist_file))
    
    def tf_idf(self):

        total = []
        
        userInput = self.editTf.toPlainText()
        userInput = re.split(r'\W+', userInput) # Untuk perhitungan

        labelRow = userInput.copy()
        labelRow.append(' ') # Hanya untuk verticalHeader

        print('userInput :', len(userInput))
        print('labelRow :', len(labelRow))

        # === Making Tf-Idf Table ===
        panjang_kolom = 6
        panjang_baris = len(labelRow)

        headerTabel = ['tf', 'df', 'D/df', 'IDF', 'IDF+1', 'W']

        self.tableTf.setColumnCount(panjang_kolom)
        self.tableTf.setRowCount(panjang_baris)

        self.tableTf.setHorizontalHeaderLabels(headerTabel)
        self.tableTf.setVerticalHeaderLabels(labelRow)

        for x in range((len(userInput)+1)):
            exist_in = []
            for y in range(len(self.listFile)):
                with open(self.listFile[y], 'r') as openFile:
                    for content in openFile:
                        if labelRow[x] in content.lower():
                            exist_in.append(1)
                        else:
                            exist_in.append(0)

            # === df ===
            df = 0
            for count in exist_in:
                if count > 0:
                    df = df + 1

            # === D ===

            if df != 0:
                D = round(len(self.listFile) / df, 2)
            else:
                D = 1

            # === idf ===
            idf = round(math.log(D), 2)

            # === W ===
            W = []
            for freq in range(len(exist_in)):
                W.append(round(exist_in[freq]*(idf+1), 2))

            if x < len(userInput):
                self.tableTf.setItem(x, 0, QTableWidgetItem(str(exist_in)))
                self.tableTf.setItem(x, 1, QTableWidgetItem(str(df)))
                self.tableTf.setItem(x, 2, QTableWidgetItem(str(D)))
                self.tableTf.setItem(x, 3, QTableWidgetItem(str(idf)))
                self.tableTf.setItem(x, 4, QTableWidgetItem(str(idf+1)))
                self.tableTf.setItem(x, 5, QTableWidgetItem(str(W)))
            else:
                self.tableTf.setItem(x, 0, QTableWidgetItem(''))
                self.tableTf.setItem(x, 1, QTableWidgetItem(''))
                self.tableTf.setItem(x, 2, QTableWidgetItem(''))
                self.tableTf.setItem(x, 3, QTableWidgetItem(''))
                self.tableTf.setItem(x, 4, QTableWidgetItem('Sum :'))
                self.tableTf.setItem(x, 5, QTableWidgetItem(str(total)))
        

    def items_clear(self):
        for item in self.tableWidget.selectedItems():
            newitem = QTableWidgetItem()
            self.tableWidget.setItem(item.row(), item.column(), newitem)

    def doAll(self):
        self.openFile()
        self.showOriginal()
        self.tokenize()
        self.removeStopwords()
        self.stemming()
        self.printIncidence()
        self.printInverted()

app = QApplication([])
window = Ui_MainWindow()
window.show()
app.exec_()