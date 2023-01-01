from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem,QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore,QtGui
import sys
import Backend.main as Backend


inversed_file = Backend.CreateInversedFile()

##MAIN CLASS 
class Main(QMainWindow):

    def __init__(self):
        super(Main,self).__init__()
        loadUi("./UI/Ri_Project.ui",self)
        Backend.InitEngine()
        ##UI LOADED
        self.search_btn.clicked.connect(self.Search_Query)
    def Clear_Results_Table(self,table):
        table.clearContents()
        table.setRowCount(0)
        return
    def Search_Query(self):
        ##clear tables
        self.Clear_Results_Table(self.term_by_document_table)
        self.Clear_Results_Table(self.stored_documents_table)

        ##get query results
        query = self.query_input.text()
        query_results = Backend.WordSearch(query,Backend.INVERSED_FILE,tokenize=True)
        results_relevence = Backend.CalculateRelevence(query_results.keys(),"jackard")
        print(results_relevence)

        ##show query results
        self.Show_Query_Results(query_results,results_relevence)
    
    def Show_Query_Results(self,query_results,results_relevence):
        terms = list(query_results.keys())
        total_docs = len(query_results[terms[0]]["DOCS"])
        for term in terms:
            for j in range(total_docs):
                ##create a new row
                rowPosition = self.term_by_document_table.rowCount()
                self.term_by_document_table.insertRow(rowPosition)
      
                ##insert data to row
                self.term_by_document_table.setItem(rowPosition , 0, QTableWidgetItem(term))
                self.term_by_document_table.setItem(rowPosition , 1, QTableWidgetItem(query_results[term]["DOCS"][j]))
                self.term_by_document_table.setItem(rowPosition , 2, QTableWidgetItem(str(query_results[term]["FREQ"][j])))
                self.term_by_document_table.setItem(rowPosition , 3, QTableWidgetItem(str(query_results[term]["PONDERATION"][j])))
        
        for i in range(total_docs):
            rowPosition = self.stored_documents_table.rowCount()
            self.stored_documents_table.insertRow(rowPosition)

            ##insert data to row
            self.stored_documents_table.setItem(rowPosition , 0, QTableWidgetItem(str(results_relevence["DOCS"][i])))
            self.stored_documents_table.setItem(rowPosition , 1, QTableWidgetItem(str(results_relevence["RELEVENCE"][i])))

            
        return
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()
