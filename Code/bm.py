from math import cos, sqrt
from typing import KeysView, List
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QTableWidgetItem
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

import os
import re
import math
import pandas as pd

class Node:
    def __init__(self ,docId, freq = None):
        self.freq = freq
        self.doc = docId
        self.nextval = None
    
class SlinkedList:
    def __init__(self ,head = None):
        self.head = head

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
        self.btnBool.clicked.connect(self.makeBoolean)
        self.btnTf.clicked.connect(self.tf_idf)
        self.btnJacCheck.clicked.connect(self.jaccard)
        self.btnNCheck.clicked.connect(self.makeNGram)
        self.btnCosine.clicked.connect(self.makeCosineSimilarity)

    def openFile(self):

        counter = 1
        self.listOpenedDocument.clear()

        caption = 'Open File'
        directory = './'
        filter_mask = 'Text Files (*.txt)'
        filenames = QFileDialog.getOpenFileNames(None, caption, directory, filter_mask)[0]

        # keeping opened files
        for x in range(len(filenames)):
            if filenames[x] not in self.listFile:
                self.listFile.append(filenames[x])

                file = os.path.basename(filenames[x])
                file = os.path.splitext(file)
                self.file_tampil.append(file[0])
        
        # Print Opened Files
        for y in self.file_tampil:
            self.listOpenedDocument.addItem('{}. {}'.format(counter, y))
            counter += 1

# Preprocessing -start-
    def showOriginal(self):

        for file in self.listFile:
            self.listDocOri.addItem('>>> {} :'.format(os.path.basename(file)))

            openedFile = open(file, 'r')
            content = openedFile.read()
            self.listDocOri.addItem('{}\n'.format(content))
    def tokenize(self):

        for file in self.listFile:

            openedFile = open(file, 'r')
            content = openedFile.read()
            content = content.lower()
            content = re.split(r'\W+', content)

            self.split_words.extend(content)
            self.split_words = list(dict.fromkeys(self.split_words))

            self.split_tampil.extend(content)
            self.split_tampil = list(dict.fromkeys(self.split_tampil))
        
            self.listDocToken.addItem('>>> {} :'.format(os.path.basename(file)))
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
        
        for files in self.listFile:
            self.listDocStop.addItem('>>> {} :'.format(os.path.basename(files)))
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

        for files in self.listFile:
            self.listDocStem.addItem('>>> {} :'.format(os.path.basename(files)))
            self.listDocStem.addItem('{}\n'.format(str(self.stem_tampil)))

        self.split_tampil.clear()
        self.stop_tampil.clear()
        self.stem_tampil.clear()
# -end-

# STKI Features -start-
    def printIncidence(self):

        self.items_clear()

        font = QFont()
        font.setBold(True)

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
                            newItem = QTableWidgetItem('1')
                            newItem.setTextAlignment(QtCore.Qt.AlignCenter)
                            self.tableWidget.setItem(x, y, newItem)
                            self.tableWidget.item(x,y).setFont(font)
                        else:
                            newItem = QTableWidgetItem('0')
                            newItem.setTextAlignment(QtCore.Qt.AlignCenter)
                            self.tableWidget.setItem(x, y, newItem)
    def printInverted(self):

        # Printing
        self.listInverted.clear()

        for x in range(len(self.stopped_words)):
            exist_file = list()
            freq = 0

            for data in self.listFile:
                post = list()

                with open(data, 'r') as namaFile:
                    for isi in namaFile:
                        isi = isi.lower()
                        list_isi = re.split(r'\W+', isi)

                        for y in range(len(list_isi)):
                            if self.stopped_words[x] == list_isi[y]:
                                    
                                exist_file.append(os.path.basename(data))
                                exist_file = list(dict.fromkeys(exist_file))

                                freq += 1

                                post.append(y)

                inverted_show = list()
                for z in range(len(exist_file)):
                    inverted_show.append('{}'.format(exist_file[z]))

            self.listInverted.addItem('{}\t: {}'.format(self.stemmed_words[x], inverted_show))
    def makeBoolean(self):
        all_words = []
        dict_global = {}
        idx = 1
        files_with_index = {}

        for file in self.listFile:
            fname = file
            file = open(file , "r")
            text = file.read()
            text = re.sub(re.compile('\d'),'',text)
            words = re.split(r'\W+', text) # tokenize words
            words = [word for word in words if len(words)>1] # check if file not empty / only contains 1 word
            words = [word.lower() for word in words] # lower case
            words = [word for word in words if word not in self.list_stopwords] #stopwords
            dict_global.update(self.finding_all_unique_words_and_freq(words))
            files_with_index[idx] = os.path.basename(fname)
            idx = idx + 1
    
        unique_words_all = set(dict_global.keys())

        linked_list_data = {}
        for word in unique_words_all:
            linked_list_data[word] = SlinkedList()
            linked_list_data[word].head = Node(1,Node)

        word_freq_in_doc = {}
        idx = 1

        for file in self.listFile:
            file = open(file, "r")
            text = file.read()
            text = re.sub(re.compile('\d'),'',text)
            words = re.split(r'\W+', text)
            words = [word for word in words if len(words)>1]
            words = [word.lower() for word in words]
            words = [word for word in words if word not in self.list_stopwords]
            word_freq_in_doc = self.finding_all_unique_words_and_freq(words)
            for word in word_freq_in_doc.keys():
                linked_list = linked_list_data[word].head
                while linked_list.nextval is not None:
                    linked_list = linked_list.nextval
                linked_list.nextval = Node(idx ,word_freq_in_doc[word])
            idx = idx + 1

        query = self.editBool.toPlainText()
        query = re.split(r'\W+', query)
        connecting_words = []
        cnt = 1
        different_words = []
        for word in query:
            if word.lower() != "and" and word.lower() != "or" and word.lower() != "not":
                different_words.append(word.lower())
            else:
                connecting_words.append(word.lower())
        total_files = len(files_with_index)
        zeroes_and_ones = []
        zeroes_and_ones_of_all_words = []
        for word in (different_words):
            if word.lower() in unique_words_all:
                zeroes_and_ones = [0] * total_files
                linkedlist = linked_list_data[word].head
                while linkedlist.nextval is not None:
                    zeroes_and_ones[linkedlist.nextval.doc - 1] = 1
                    linkedlist = linkedlist.nextval
                zeroes_and_ones_of_all_words.append(zeroes_and_ones)
            else:
                print(word," not found")
        for word in connecting_words:
            word_list1 = zeroes_and_ones_of_all_words[0]
            word_list2 = zeroes_and_ones_of_all_words[1]
            if word == "and":
                bitwise_op = [w1 & w2 for (w1,w2) in zip(word_list1,word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op);
            elif word == "or":
                bitwise_op = [w1 | w2 for (w1,w2) in zip(word_list1,word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op);
            elif word == "not":
                bitwise_op = [not w1 for w1 in word_list2]
                bitwise_op = [int(b == True) for b in bitwise_op]
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.remove(word_list1)
                bitwise_op = [w1 & w2 for (w1,w2) in zip(word_list1,bitwise_op)]
        zeroes_and_ones_of_all_words.insert(0, bitwise_op);
                
        files = []    
        lis = zeroes_and_ones_of_all_words[0]
        cnt = 1
        for index in lis:
            if index == 1:
                files.append(files_with_index[cnt])
            cnt = cnt+1
            
        self.boolIncidence.setText(str(files))
        self.boolInverted.setText(str(files))
    def tf_idf(self):

        total = []
        for count in self.listFile:
            total.append(0)

        font = QFont()
        font.setBold(True)

        userInput = self.editTf.toPlainText()
        userInput = re.split(r'\W+', userInput.lower())
        
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
        newItem = QTableWidgetItem("IDF+1")
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
                    freq = 0
                    with open(self.listFile[y], 'r') as openFile:
                        for content in openFile:
                            content = re.split(r'\W+', content.lower())
                            for z in range(len(content)):
                                if userInput[x] == content[z]:
                                    freq += 1
                            exist_in.append(freq)

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

        self.rankTf.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            self.rankTf.addItem('{} : {}'.format(file_rank[k], total[k]))
    def jaccard(self):

        total = []
        file_rank = self.file_tampil.copy()
        self.listJac.clear()

        jac_query = self.editJaccard.toPlainText()
        jac_query = re.split(r'\W+', jac_query)

        for x in range(len(self.listFile)):
            with open(self.listFile[x], 'r') as namaFile:
                for isi_file in namaFile:
                    isi_file = re.split(r'\W+', isi_file)
                    for item in range(len(isi_file)):
                        isi_file[item] = isi_file[item].lower()
                    self.countJaccard(jac_query, isi_file)
                    hasilJaccard = len(self.inter)/len(self.concat)
                    total.append(hasilJaccard)

                self.listJac.addItem('Q ∩ {}\t    : {}'.format(self.file_tampil[x], self.inter))
                self.listJac.addItem('Q U {}\t    : {}'.format(self.file_tampil[x], self.concat))
                self.listJac.addItem('Jaccard(Q , {}) : {}'.format(self.file_tampil[x], round(hasilJaccard,2)))
                self.listJac.addItem('\n========================\n')
        
        for i in range(len(self.listFile)-1):
            for j in range(len(self.listFile)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp
        
        self.rankJaccard.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            self.rankJaccard.addItem('{} : {}'.format(file_rank[k], round(total[k],2)))
    def countJaccard(self, list1, list2):
        self.inter = [value for value in list1 if value in list2]
        
        self.concat = list1 + list2
        self.concat = list(dict.fromkeys(self.concat))
        self.concat.sort()
    def makeNGram(self):

        total = []
        ngram = self.editNGram.toPlainText()
        ngram = int(ngram)
        ngrammed = []

        self.listNGram.clear()

        for data in self.listFile:
            with open(data, 'r') as openFile:
                for isi_file in openFile:
                    ngrammed.append(self.generate_N_grams(isi_file, ngram))
            

        for x in range(len(ngrammed)):
            self.listNGram.addItem('{}\t: {}'.format(self.file_tampil[x], ngrammed[x]))

        for i in range(1):
            for j in range(len(ngrammed)-1):
                self.countJaccard(ngrammed[i], ngrammed[j+1])
                hasilNGram = round(len(self.inter)/len(self.concat),2)
                total.append(hasilNGram)
                self.listNGram.addItem('J({},{}) = {}/{} = {}'.format(
                    self.file_tampil[i], self.file_tampil[j+1], len(self.inter), len(self.concat), round(hasilNGram,2)))
        
        print('hasil N-Gram :', total)
    def generate_N_grams(self, text, ngram=1):

        words = [word for word in text.split(" ") if word not in self.list_stopwords]  
        temp=zip(*[words[i:] for i in range(0,ngram)])
        ans=[' '.join(ngram) for ngram in temp]
        return ans
    def makeCosineSimilarity(self):

        total = []
        file_rank = self.file_tampil.copy()
        zeros_keyword = []

        self.keyword = self.editCosine.toPlainText()
        self.keyword = re.split(r'\W+', self.keyword.lower())
        zeros_keyword = [1] * len(self.keyword)
        print(zeros_keyword)
        
        self.listCos.clear()
        self.listCos.addItem('keyword  :{}\n'.format(self.keyword))

        # Counting frequency of each keyword in each file
        list_freq = []
        for x in range(len(self.listFile)):

            self.listCos.addItem('keyword : {}'.format(zeros_keyword))

            list_freq = []
            
            dot_product = []
            dot_product = [1] * len(self.keyword)

            file = open(self.listFile[x], 'r')
            opened_file = file.read()
            opened_file = re.split(r'\W+', opened_file.lower())

            for y in range(len(self.keyword)):
                freq = 0

                for z in range(len(opened_file)):
                    if self.keyword[y] == opened_file[z]:
                        freq += 1
                
                list_freq.append(freq)

            print(list_freq)
            self.listCos.addItem('{}\t: {}'.format(self.file_tampil[x], list_freq))

            # --- Perhitungan Cosine Similarity
            dot_product = [a * b for a, b in zip(zeros_keyword, list_freq)]
            summed = sum(dot_product)
            bawah_f = []
            bawah_f2 = []
            for i in range(len(zeros_keyword)):
                bawah_f.append(zeros_keyword[i]**2)
                bawah_f2.append(list_freq[i]**2)
                    
            bawah = sqrt(sum(bawah_f)) * sqrt(sum(bawah_f2))
            if bawah == 0:
                bawah = 1
            hasil = summed/bawah

            total.append(hasil)

            self.listCos.addItem('hasil : {}\n'.format(round(hasil,2)))

        for i in range(len(self.listFile)-1):
            for j in range(len(self.listFile)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp
        
        self.rankCosine.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            self.rankCosine.addItem('{} : {}'.format(file_rank[k], round(total[k],2)))
# -end-

# Helper Function -start-
    def finding_all_unique_words_and_freq(self, words):
        words_unique = []
        word_freq = {}
        for word in words:
            if word not in words_unique:
                words_unique.append(word)
        for word in words_unique:
            word_freq[word] = words.count(word)
        return word_freq      
    def finding_freq_of_word_in_doc(self, word, words):
        freq = words.count(word)
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
        # self.makeCosineSimilarity()
# -end-

app = QApplication([])
window = Ui_MainWindow()
window.show()
app.exec_()
