from typing import List
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QTableWidgetItem
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
        self.inter = 0
        self.concat = 0

        # Link Widgets
        self.btnAddFile.clicked.connect(self.doAll)
        self.btnTf.clicked.connect(self.tf_idf)
        self.btnCheck.clicked.connect(self.jaccard)

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
        for count in self.listFile:
            total.append(0)

        font = QFont()
        font.setBold(True)

        userInput = self.editTf.toPlainText()
        userInput = re.split(r'\W+', userInput)
        
        kolom_tf = ['df', 'D/df', 'IDF', 'IDF+1']

        jarak_W = len(self.listFile) + len(kolom_tf)
        panjang_kolom = len(self.listFile)*2 + len(kolom_tf) + 1

        self.tableTf.setColumnCount(panjang_kolom)
        self.tableTf.setRowCount(len(userInput)+3)
        
        self.tableTf.horizontalHeader().setVisible(False)
        self.tableTf.verticalHeader().setVisible(False)

        # ========== Span Tf ==========

        ''' Format bikin span : tableTf.setSpan(row, column, rowSpan, columnSpan) '''

        self.tableTf.setSpan(0, 1, 1, len(self.listFile))
        newItem = QTableWidgetItem("tf")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, 1, newItem)
        self.tableTf.item(0, 1).setFont(font)

        # ========== Span df ==========

        self.tableTf.setSpan(0, len(self.listFile)+1, 2, 1)
        newItem = QTableWidgetItem("df")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.listFile)+1, newItem)
        self.tableTf.item(0, len(self.listFile)+1).setFont(font)

        # ========== Span D/df ==========

        self.tableTf.setSpan(0, len(self.listFile)+2, 2, 1)
        newItem = QTableWidgetItem("D / df")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.listFile)+2, newItem)
        self.tableTf.item(0, len(self.listFile)+2).setFont(font)

        # ========== Span IDF ==========

        self.tableTf.setSpan(0, len(self.listFile)+3, 2, 1)
        newItem = QTableWidgetItem("IDF")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.listFile)+3, newItem)
        self.tableTf.item(0, len(self.listFile)+3).setFont(font)

        # ========== Span IDF+1 ==========

        self.tableTf.setSpan(0, len(self.listFile)+4, 2, 1)
        newItem = QTableWidgetItem("IDF")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.listFile)+4, newItem)
        self.tableTf.item(0, len(self.listFile)+4).setFont(font)

        # ========== Span W ==========

        self.tableTf.setSpan(0, len(self.listFile)+5, 1, len(self.listFile))
        newItem = QTableWidgetItem("W = tf*(IDF+1)")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.listFile)+5, newItem)
        self.tableTf.item(0, len(self.listFile)+5).setFont(font)

        # ========== MAKE TABLE ==========

        # __Print Document di kolom tf (kiri)__ 
        for y in range(len(self.listFile)):
            cell_item = QTableWidgetItem(str(self.file_tampil[y]))
            cell_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableTf.setItem(1, y+1, cell_item)
            self.tableTf.item(1, y+1).setFont(font)
            
        # __Print Document di kolom tf (kanan)__
        for y in range(len(self.listFile)):
            cell_item = QTableWidgetItem(str(self.file_tampil[y]))
            cell_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableTf.setItem(1, y+1+jarak_W, cell_item)
            self.tableTf.item(1, y+1+jarak_W).setFont(font)
        
        # # __Isi Tf-Idf__
        for x in range(len(userInput)):

            exist_in = []

            for y in range((panjang_kolom)):

                # __Print userInput di row__
                self.tableTf.setItem(x+2, 0, QTableWidgetItem(str(userInput[x])))
                
                # __Print nilai tf per document__
                if y < len(self.listFile):
                    with open(self.listFile[y], 'r') as openFile:
                        for content in openFile:
                            if userInput[x] in content.lower():
                                exist_in.append(1)
                            else:
                                exist_in.append(0)

                    self.tableTf.setItem(x+2, y+1, QTableWidgetItem(str(exist_in[y])))

                # __df__
                df = 0
                for count in exist_in:
                    if count > 0:
                        df = df + 1

                # __D/df__
                if df != 0:
                    D = round(len(self.listFile) / df, 2)
                else:
                    D = 1

                # __idf__
                idf = round(math.log(D), 2)

                # __idf+1__
                idf_1 = round(idf+1,2)

                # __W__
                W = []
                for freq in range(len(exist_in)):
                    W.append(round(exist_in[freq]*(idf+1), 2))

                if len(W) == len(self.listFile) and y == len(self.listFile):
                    # __SUM__
                    zipped_list = zip(total, W)
                    total = [x+y for (x, y) in zipped_list]
                                    
                # __Print nilai setelah tf dan sebelum W__
                if y == (len(self.listFile)+1) and y <= jarak_W:
                    self.tableTf.setItem(x+2, y, QTableWidgetItem(str(df)))
                    self.tableTf.setItem(x+2, y+1, QTableWidgetItem(str(D)))
                    self.tableTf.setItem(x+2, y+2, QTableWidgetItem(str(idf)))
                    self.tableTf.setItem(x+2, y+3, QTableWidgetItem(str(idf_1)))
                
                # __Print nilai W per dokumen__
                if y > jarak_W:
                    self.tableTf.setItem(x+2, y, QTableWidgetItem(str(W[y-(jarak_W+1)])))
                
                if x == len(userInput)-1:

                    if y == jarak_W:
                        item_sum = QTableWidgetItem('Sum :')
                        self.tableTf.setItem(x+3, y, item_sum)
                        self.tableTf.item(x+3, y).setFont(font)
                    elif y > jarak_W:
                        total_sum = QTableWidgetItem(str(total[y-(jarak_W+1)]))
                        self.tableTf.setItem(x+3, y, total_sum)
                        self.tableTf.item(x+3, y).setFont(font)

        file_rank = self.file_tampil.copy()

        for i in range(len(self.listFile)-1):
            for j in range(len(self.listFile)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp

        # print(total)
        # print(file_rank)

        self.rankingTf.setText('Ranking Tf : {} : {}'.format(file_rank, total))

    def jaccard(self):

        self.listJac.clear()

        list_A = self.editA.toPlainText()
        list_A = list(str(list_A))
        list_A = [int(a) for a in list_A]

        list_B = self.editB.toPlainText()
        list_B = list(str(list_B))
        list_B = [int(b) for b in list_B]

        list_C = self.editC.toPlainText()
        list_C = list(str(list_C))
        list_C = [int(c) for c in list_C]

        # print('A :', list_A)
        # print('Type A :', type(list_A))
        # print('B :', list_B)
        # print('Type B :', type(list_B))
        # print('C :', list_C)
        # print('Type C :', type(list_C))

        list_jac = self.editJaccard.toPlainText()
        list_jac = re.split(r'\W+', list_jac)

        for x in range(len(list_jac)):
            list_jac[x] = list_jac[x].upper()
        
        # print('list_jac :', list_jac)
        # print('type list_jac :', type(list_jac))
        
        if list_jac[0] == 'A' and list_jac[1] == 'B':
            self.countJaccard(list_A, list_B)
        elif list_jac[0] == 'A' and list_jac[1] == 'C':
            self.countJaccard(list_A, list_C)
        elif list_jac[0] == 'B' and list_jac[1] == 'C':
            self.countJaccard(list_B, list_C)
        else:
            self.listJac.addItem('Error')

        hasilJaccard = len(self.inter)/len(self.concat)

        self.listJac.addItem('{} ∩ {}\t    : {}'.format(list_jac[0], list_jac[1], self.inter))
        self.listJac.addItem('{} U {}\t    : {}'.format(list_jac[0], list_jac[1], self.concat))
        self.listJac.addItem('Jaccard({},{}) : {}'.format(list_jac[0], list_jac[1], round(hasilJaccard,2)))

    def countJaccard(self, list1, list2):
        self.inter = [value for value in list1 if value in list2]
        # if bool(self.inter):
        #     self.inter.append(0)
        
        self.concat = list1 + list2
        self.concat = list(dict.fromkeys(self.concat))
        self.concat.sort()


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