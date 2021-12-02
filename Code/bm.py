from math import sqrt, log
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QTableWidgetItem

import os
import re
import math
import copy
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
        self.list_file = []

        # Link Widgets
        self.btnAddFile.clicked.connect(self.doAll)
        self.btnBool.clicked.connect(self.makeBoolean)
        self.btnTf.clicked.connect(self.tf_idf)
        self.btnJacCheck.clicked.connect(self.jaccard)
        self.btnNCheck.clicked.connect(self.makeNGram)
        self.btnCosine.clicked.connect(self.makeCosineSimilarity)
        self.btnBM.clicked.connect(self.makeBM25)

    def openFile(self):

        caption = 'Open File'
        directory = './'
        filter_mask = 'Text Files (*.txt)'
        filenames = QFileDialog.getOpenFileNames(None, caption, directory, filter_mask)[0]

        # keeping opened files
        for x in range(len(filenames)):
            if filenames[x] not in self.list_file:
                self.list_file.append(filenames[x])
    
# === Show Preprocessing -start-
    def showOriginal(self):

        self.listDocOri.clear()
        
        for files in self.list_file:
            opened_file = open(files, 'r')
            file_content = opened_file.read()
            if files != self.list_file[-1]:
                self.listDocOri.addItem(f'>>> {os.path.basename(files)}\n{file_content}\n')
            else:
                self.listDocOri.addItem(f'>>> {os.path.basename(files)}\n{file_content}')
    def showTokenisasi(self):

        self.listDocToken.clear()

        self.tokenized_files = self.tokenisasi(self.list_file)
        for files in self.list_file:
            if files != self.list_file[-1]:
                self.listDocToken.addItem(f'>>> {os.path.basename(files)}\n{self.tokenized_files[files]}\n')
            else:
                self.listDocToken.addItem(f'>>> {os.path.basename(files)}\n{self.tokenized_files[files]}')
    def showStopwords(self):

        self.listDocStop.clear()

        self.stopped_files = self.stopwords(copy.deepcopy(self.tokenized_files))
        for files in self.list_file:
            if files != self.list_file[-1]:
                self.listDocStop.addItem(f'>>> {os.path.basename(files)}\n{self.stopped_files[files]}\n')
            else:
                self.listDocStop.addItem(f'>>> {os.path.basename(files)}\n{self.stopped_files[files]}') 
    def showStemming(self):

        self.listDocStem.clear()

        self.preprocessed_files = self.stemming(copy.deepcopy(self.stopped_files))
        for files in self.list_file:
            if files != self.list_file[-1]:
                self.listDocStem.addItem(f'>>> {os.path.basename(files)}\n{self.preprocessed_files[files]}\n')
            else:
                self.listDocStem.addItem(f'>>> {os.path.basename(files)}\n{self.preprocessed_files[files]}')
# === - end -

# STKI Features -start-
    def printIncidence(self):

        self.tableWidget.setRowCount(0)

        # --- Object of QFont -start-
        font = QFont()
        font.setBold(True)
        # -end-

        self.unique_words = self.findUniqueWords(self.list_file)
        
        kolom_tabel = []
        for files in self.list_file:
            basename = os.path.basename(files)
            nama_file = os.path.splitext(basename)
            kolom_tabel.append(nama_file[0])

        # --- Table Constructing -start-
        panjang_col = len(self.list_file)
        panjang_row = len(self.unique_words)

        self.tableWidget.setColumnCount(panjang_col)
        self.tableWidget.setRowCount(panjang_row)

        self.tableWidget.setHorizontalHeaderLabels(kolom_tabel)
        self.tableWidget.setVerticalHeaderLabels(self.unique_words)
        # --- -end-

        for x in range(len(self.unique_words)):
            for y in range(len(self.list_file)):
                if self.unique_words[x] in self.preprocessed_files[self.list_file[y]]:
                    newItem = QTableWidgetItem('1')
                    newItem.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tableWidget.setItem(x, y, newItem)
                    self.tableWidget.item(x,y).setFont(font)
                else:
                    newItem = QTableWidgetItem('0')
                    newItem.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tableWidget.setItem(x, y, newItem)
    def printInverted(self):

        self.listInverted.clear()

        for word in self.unique_words:
            inverted_index = []
            for files in self.list_file:
                freq = 0
                list_post = []
                files_found = []
                if word in self.preprocessed_files[files]:
                    files_found.append(os.path.basename(files))
                    for idx in range(len(self.preprocessed_files[files])):
                        if word == self.preprocessed_files[files][idx]:
                            freq += 1
                            list_post.append(idx)
                    inverted_index.append(f'{files_found}, {freq}, {list_post}')
            self.listInverted.addItem(f'{word}\t: {inverted_index}')
    def makeBoolean(self):

        stopwords_path = 'stopwords_pilkada.csv'
        kamus_stopwords = []

        df = pd.read_csv(stopwords_path)
        for item in df['ada']:
            kamus_stopwords.append(item)

        all_words = []
        dict_global = {}
        idx = 1
        files_with_index = {}

        for file in self.list_file:
            fname = file
            file = open(file , "r")
            text = file.read()
            text = re.sub(re.compile('\d'),'',text)
            words = re.split(r'\W+', text) # tokenize words
            words = [word for word in words if len(words)>1] # check if file not empty / only contains 1 word
            words = [word.lower() for word in words] # lower case
            words = [word for word in words if word not in kamus_stopwords] #stopwords
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

        for file in self.list_file:
            file = open(file, "r")
            text = file.read()
            text = re.sub(re.compile('\d'),'',text)
            words = re.split(r'\W+', text)
            words = [word for word in words if len(words)>1]
            words = [word.lower() for word in words]
            words = [word for word in words if word not in kamus_stopwords]
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

        self.tableTf.setRowCount(0)
        self.rankTf.clear()

        total = []
        for count in self.list_file:
            total.append(0)

        font = QFont()
        font.setBold(True)

        userInput = self.editTf.toPlainText()
        userInput = self.preprocessingQuery(userInput)
        userInput = list(dict.fromkeys(userInput))
        
        kolom_tf = ['df', 'D/df', 'IDF', 'IDF+1']

        jarak_W = len(self.list_file) + len(kolom_tf)
        panjang_kolom = len(self.list_file)*2 + len(kolom_tf) + 1

        self.tableTf.setColumnCount(panjang_kolom)
        self.tableTf.setRowCount(len(userInput)+3)
        
        self.tableTf.horizontalHeader().setVisible(False)
        self.tableTf.verticalHeader().setVisible(False)

        # ========== Span Tf ==========

        ''' Format bikin span : tableTf.setSpan(row, column, rowSpan, columnSpan) '''

        self.tableTf.setSpan(0, 1, 1, len(self.list_file))
        newItem = QTableWidgetItem("tf")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, 1, newItem)
        self.tableTf.item(0, 1).setFont(font)

        # ========== Span df ==========

        self.tableTf.setSpan(0, len(self.list_file)+1, 2, 1)
        newItem = QTableWidgetItem("df")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.list_file)+1, newItem)
        self.tableTf.item(0, len(self.list_file)+1).setFont(font)

        # ========== Span D/df ==========

        self.tableTf.setSpan(0, len(self.list_file)+2, 2, 1)
        newItem = QTableWidgetItem("D / df")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.list_file)+2, newItem)
        self.tableTf.item(0, len(self.list_file)+2).setFont(font)

        # ========== Span IDF ==========

        self.tableTf.setSpan(0, len(self.list_file)+3, 2, 1)
        newItem = QTableWidgetItem("IDF")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.list_file)+3, newItem)
        self.tableTf.item(0, len(self.list_file)+3).setFont(font)

        # ========== Span IDF+1 ==========

        self.tableTf.setSpan(0, len(self.list_file)+4, 2, 1)
        newItem = QTableWidgetItem("IDF+1")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.list_file)+4, newItem)
        self.tableTf.item(0, len(self.list_file)+4).setFont(font)

        # ========== Span W ==========

        self.tableTf.setSpan(0, len(self.list_file)+5, 1, len(self.list_file))
        newItem = QTableWidgetItem("W = tf*(IDF+1)")
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableTf.setItem(0, len(self.list_file)+5, newItem)
        self.tableTf.item(0, len(self.list_file)+5).setFont(font)

        # ========== MAKE TABLE ==========

        # __Print Document di kolom tf (kiri)__ 
        for y in range(len(self.list_file)):
            cell_item = QTableWidgetItem(str(os.path.basename(self.list_file[y])))
            cell_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableTf.setItem(1, y+1, cell_item)
            self.tableTf.item(1, y+1).setFont(font)
            
        # __Print Document di kolom tf (kanan)__
        for y in range(len(self.list_file)):
            cell_item = QTableWidgetItem(str(os.path.basename(self.list_file[y])))
            cell_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableTf.setItem(1, y+1+jarak_W, cell_item)
            self.tableTf.item(1, y+1+jarak_W).setFont(font)
        
        # # __Isi Tf-Idf__
        for x in range(len(userInput)):

            exist_in = []

            for y in range(panjang_kolom):

                # __Print userInput di row__
                self.tableTf.setItem(x+2, 0, QTableWidgetItem(str(userInput[x])))
                
                # __Print nilai tf per document__
                if y < len(self.list_file):
                    freq = 0
                    for z in range(len(self.preprocessed_files[self.list_file[y]])):
                        if userInput[x] == self.preprocessed_files[self.list_file[y]][z]:
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
                    D = round(len(self.list_file) / df, 2)
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

                if len(W) == len(self.list_file) and y == len(self.list_file):
                    # __SUM__
                    zipped_list = zip(total, W)
                    total = [x+y for (x, y) in zipped_list]
                                    
                # __Print nilai setelah tf dan sebelum W__
                if y == (len(self.list_file)+1) and y <= jarak_W:
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
                        total_sum = QTableWidgetItem(str(round(total[y-(jarak_W+1)],2)))
                        self.tableTf.setItem(x+3, y, total_sum)
                        self.tableTf.item(x+3, y).setFont(font)

        file_rank = self.list_file.copy()

        for i in range(len(self.list_file)-1):
            for j in range(len(self.list_file)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp

        self.rankTf.clear()
        self.rankTf.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            opened_file = open(file_rank[k], 'r')
            file_content = opened_file.read()
            self.rankTf.addItem('{} : {} => {}'.format(os.path.basename(file_rank[k]), round(total[k],2), file_content))
    def jaccard(self):

        total = []
        file_rank = self.list_file.copy()
        self.listJac.clear()
        self.rankJaccard.clear()

        jac_query = self.editJaccard.toPlainText()
        jac_query = self.preprocessingQuery(jac_query)

        for idx in range(len(self.list_file)):
            self.countJaccard(jac_query, self.preprocessed_files[self.list_file[idx]])
            hasil_jaccard = len(self.inter)/len(self.concat)
            total.append(hasil_jaccard)

            self.listJac.addItem('Q ∩ {}\t\t: {}'.format(os.path.splitext(os.path.basename(self.list_file[idx]))[0], self.inter))
            self.listJac.addItem('Q U {}\t\t: {}'.format(os.path.splitext(os.path.basename(self.list_file[idx]))[0], self.concat))
            self.listJac.addItem('Jaccard(Q , {})\t: {}'.format(os.path.splitext(os.path.basename(self.list_file[idx]))[0], round(hasil_jaccard,2)))
            self.listJac.addItem('\n========================\n')
        
        for i in range(len(self.list_file)-1):
            for j in range(len(self.list_file)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp
        
        self.rankJaccard.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            opened_file = open(file_rank[k], 'r')
            file_content = opened_file.read()
            self.rankJaccard.addItem('{} : {} => {}'.format(os.path.basename(file_rank[k]), round(total[k],2), file_content))
    def makeNGram(self):

        total = []
        n = self.editNGram.toPlainText()
        n = int(n)
        ngrammed = []

        self.listNGram.clear()
            
        for files in self.list_file:
            string = ""
            string = ' '.join(self.preprocessed_files[files])
            ngrammed.append(self.generate_N_grams(string, n))

        for x in range(len(ngrammed)):
            self.listNGram.addItem('{}\t: {}'.format(os.path.splitext(os.path.basename(self.list_file[x]))[0], ngrammed[x]))

        for i in range(1):
            for j in range(len(ngrammed)-1):
                self.countJaccard(ngrammed[i], ngrammed[j+1])
                hasilNGram = round(len(self.inter)/len(self.concat),2)
                total.append(hasilNGram)
                self.listNGram.addItem('J({},{}) = {}/{} = {}'.format(
                    os.path.splitext(os.path.basename(self.list_file[i]))[0], 
                    os.path.splitext(os.path.basename(self.list_file[j+1]))[0],
                    len(self.inter), len(self.concat), round(hasilNGram,2)))
    def makeCosineSimilarity(self):

        total = []
        file_rank = self.list_file.copy()
        zeros_keyword = []

        keyword = self.editCosine.toPlainText()
        keyword = self.preprocessingQuery(keyword)
        keyword_copy = keyword.copy()
        keyword_copy = list(dict.fromkeys(keyword_copy))

        for x in range(len(keyword_copy)):
            freq = 0
            for y in range(len(keyword)):
                if keyword_copy[x] == keyword[y]:
                    freq += 1
            zeros_keyword.append(freq)
        
                
        self.listCos.clear()
        self.rankCosine.clear()

        self.listCos.addItem('keyword  :{}\n'.format(keyword_copy))

        # Counting frequency of each keyword in each file
        for x in range(len(self.list_file)):

            self.listCos.addItem('keyword : {}'.format(zeros_keyword))

            list_freq = []
            dot_product = [1] * len(keyword_copy)

            opened_file = self.preprocessed_files[self.list_file[x]]

            for y in range(len(keyword_copy)):
                freq = 0

                for z in range(len(opened_file)):
                    if keyword_copy[y] == opened_file[z]:
                        freq += 1
                
                list_freq.append(freq)

            self.listCos.addItem('{}\t: {}'.format(os.path.splitext(os.path.basename(self.list_file[x]))[0], list_freq))

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

        for i in range(len(self.list_file)-1):
            for j in range(len(self.list_file)-i-1):
                if total[j] < total[j+1]:
                    temp_total = total[j]
                    total[j] = total[j+1]
                    total[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp
        
        self.rankCosine.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            opened_file = open(file_rank[k], 'r')
            file_content = opened_file.read()
            self.rankCosine.addItem('{} : {} => {}'.format(
                os.path.splitext(os.path.basename(file_rank[k]))[0], round(total[k],2), file_content))
    def makeBM25(self):
        total_doc_length = []
        file_rank = self.list_file.copy()
        N = len(self.list_file)

        query = self.editBM.toPlainText()
        query = self.preprocessingQuery(query)
        query = list(dict.fromkeys(query))

        # --------------- Get Recquired Parameters ---------------

        # ----- Get length of all document -start
        for file in self.list_file:
            total_doc_length.extend(self.preprocessed_files[file])
        # ===== -end-

        # ----- Get Length of all document -start-
        all_doc_len = []
        for file in self.list_file:
            all_doc_len.extend(self.preprocessed_files[file])
        len_all_doc = len(all_doc_len)
        # ===== -end-

        N = len(self.list_file)
        doc_bm_score = []

        # --------------- BM25 Scoring ---------------
        for file in self.list_file:

            bm_score = 0
            bm_total = 0
            len_document = len(self.preprocessed_files[file])
            avgdl = len_all_doc/N

            self.listBM.addItem(f'===== {os.path.basename(file)} :')

            for x in range(len(query)):
                df = 0
                freq = 0
                for y in range(len(self.preprocessed_files[file])):
                    if query[x] == self.preprocessed_files[file][y]:
                        freq += 1
                for file2 in self.list_file:
                    if query[x] in self.preprocessed_files[file2]:
                        df += 1
                
                bm_score = self.countBM(freq, len_document, N, avgdl, df)
                bm_total += bm_score
                self.listBM.addItem(f'{query[x]}\t: {bm_score}')
            self.listBM.addItem(f'Total\t: <b>{bm_total}</b>\n')
            doc_bm_score.append(bm_total)
        # ========================= -end- =================================

        # --------------- Ranking ---------------
        for i in range(len(self.list_file)-1):
            for j in range(len(self.list_file)-i-1):
                if doc_bm_score[j] < doc_bm_score[j+1]:
                    temp_total = doc_bm_score[j]
                    doc_bm_score[j] = doc_bm_score[j+1]
                    doc_bm_score[j+1] = temp_total

                    temp = file_rank[j]
                    file_rank[j] = file_rank[j+1]
                    file_rank[j+1] = temp
        
        self.rankCosine.addItem('-- File Rank --')
        for k in range(len(file_rank)):
            opened_file = open(file_rank[k], 'r')
            file_content = opened_file.read()
            self.rankBM.addItem('{} : {} => {}'.format(
                os.path.splitext(os.path.basename(file_rank[k]))[0], round(doc_bm_score[k],2), file_content))
        # ========= Ranking end =========
# - end -

# -------------------------------------------- HELPER FUNCTION --------------------------------------------

    def tokenisasi(self, kumpulan_file):

        tokenized_words_O = {}
        
        for file in kumpulan_file:
            opened_file = open(file, 'r')
            file_content = opened_file.read()

            # Tokenizing =====================================||
            file_content = file_content.lower()              #|| --> Case Folding
            file_content = re.split(r'\W+', file_content)    #|| --> Tokenize
            # ------------------------------------------------||

            tokenized_words_O[file] = file_content.copy()
        
        return tokenized_words_O
    def stopwords(self, tokenized_words_I):
        
        stopwords_path = 'stopwords_pilkada.csv'
        kamus_stopwords = []
        stopped_words_O = {}
        
        df = pd.read_csv(stopwords_path)

        for item in df['ada']:
            kamus_stopwords.append(item)

        # Stopwording ========================================================||
        for files in self.list_file:                                        # ||
            words_tokened = []                                              # ||
            for idx in range(len(tokenized_words_I[files])):                # ||
                if tokenized_words_I[files][idx] not in kamus_stopwords:    # ||
                    words_tokened.append(tokenized_words_I[files][idx])     # ||
            tokenized_words_I[files] = words_tokened                        # ||
        # --------------------------------------------------------------------||
       
        stopped_words_O = tokenized_words_I.copy()

        return stopped_words_O
    def stemming(self, stopped_words_I):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()

        # Stemming =====================================||
        for words in stopped_words_I.values():        # ||
            for idx in range(len(words)):             # ||
                words[idx] = stemmer.stem(words[idx]) # ||
        # ==============================================||

        stemmed_words_O = stopped_words_I.copy()
        return stemmed_words_O
    def preprocessing(self, nama_file):

        tokenized_words = self.tokenisasi(nama_file)
        stopped_words = self.stopwords(tokenized_words)
        stemmed_words = self.stemming(stopped_words)
        return tokenized_words, stopped_words, stemmed_words
    def findUniqueWords(self, list_file):

        unique_words = []
        for files in list_file:
            for idx in range(len(self.preprocessed_files[files])):
                if self.preprocessed_files[files][idx] not in unique_words:
                    unique_words.append(self.preprocessed_files[files][idx])
        
        return unique_words
    def doAll(self):
        self.openFile()
        self.showOriginal()
        self.showTokenisasi()
        self.showStopwords()
        self.showStemming()
        self.printIncidence()
        self.printInverted()

# --- Fungsi Preprocessing Query/Keyword
    def preprocessingQuery(self, string):

        # [[Kamus Stopwords]] =====================||
        stopwords_path = 'stopwords_pilkada.csv' # ||
        kamus_stopwords = []                     # ||
                                                # ||
        df = pd.read_csv(stopwords_path)         # ||
                                                # ||
        for item in df['ada']:                   # ||
            kamus_stopwords.append(item)         # ||
        # <> --------------------------------------||

        # [[Object Stemmer]] ======================||
        factory = StemmerFactory()               # ||
        stemmer = factory.create_stemmer()       # ||
        # <> --------------------------------------||

        string = string.lower()
        tokenized_string = re.split(r'\W+', string)
        
        for item in tokenized_string:
            if item in kamus_stopwords:
                tokenized_string.remove(item)

        stemmed_words = []
        
        for idx in range(len(tokenized_string)):
            stemmed_words.append(stemmer.stem(tokenized_string[idx]))
            
        return stemmed_words
    def items_clear(self):
        for item in self.tableWidget.selectedItems():
            newitem = QTableWidgetItem()
            self.tableWidget.setItem(item.row(), item.column(), newitem)
    def countJaccard(self, list1, list2):
        self.inter = [value for value in list1 if value in list2]
        
        self.concat = list1 + list2
        self.concat = list(dict.fromkeys(self.concat))
        self.concat.sort()
    def generate_N_grams(self, text,ngram=1):
        words=[word for word in text.split(" ")]  
        temp=zip(*[words[i:] for i in range(0,ngram)])
        ans=[' '.join(ngram) for ngram in temp]
        return ans
    def countBM(self, freq, len_document, N, avgdl, df, k=1.25, b=0.75):
        tf = ((k+1) * freq) / (k * (1 - b + b * (len_document/avgdl) + freq))
        idf = log((N - df + 0.5) / (df + 0.5))
        bm = tf*idf
        return bm
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

app = QApplication([])
window = Ui_MainWindow()
window.show()
app.exec_()