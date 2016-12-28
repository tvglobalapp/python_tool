
import xlrd
from PyQt5 import uic, QtWidgets, QtGui
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import jira.client
from jira.client import JIRA


dev_address = "http://hlm.lge.com/issue/"

class MyWindowClass(QtWidgets.QMainWindow, uic.loadUiType('D://untitled.ui')[0]):
    fileName = ""
    fileName2 = ""
    dev_address = "http://hlm.lge.com/issue/"
    account = ''
    dataList = []
    totalItem = ''

    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("String JIRA Creator")

        self.StringSearchButton.clicked.connect(self.StringFileSelectWidget)
        self.VerifySearchButton.clicked.connect(self.VerifyFileSelectWidget)
        self.CreateButton.clicked.connect(self.CreateJira)

        self.tableWidget.setColumnWidth(0, 290)
        self.tableWidget.setColumnWidth(1, 300)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def VerifyFileSelectWidget(self):
        self.fileName2 = QFileDialog.getOpenFileName(self, "Open", '', "All Files(*.*)")[0]
        self.textEdit_2.setText(self.fileName2)
        self.progressBar.setValue(0)
        self.progressBar.hide()

    def StringFileSelectWidget(self):
        self.fileName = QFileDialog.getOpenFileName(self, "Open", '', "Excel Files(*.xlsx *.xls)")[0]
        # print(self.fileName)
        self.textEdit.setText(self.fileName)
        self.ReadExcel()
        self.DrawTableWidget()
        self.progressBar.setValue(0)
        self.progressBar.hide()

    def DrawTableWidget(self):

        self.tableWidget.setRowCount(0);

        for i in range(1,self.totalItem):
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)

            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(self.dataList[i][0]))
            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(self.dataList[i][4]))

        self.tableWidget.resizeRowsToContents()


    def ReadExcel(self):

        workbook = xlrd.open_workbook(self.fileName)

        worksheet_name = workbook.sheet_by_name(workbook.sheet_names()[0]) #시트이름으로 시트 가져오기

        worksheet_index = workbook.sheet_by_index(0) #시트번호(인덱스)로 시트 가져오기

        num_rows = worksheet_index.nrows #줄 수 가져오기
        self.totalItem = num_rows

        num_cols = worksheet_index.ncols #칸 수 가져오기

        self.dataList.clear()

        for i in range(num_rows):
            self.dataList.append([])
            for j in range(num_cols):
                self.dataList[i].append(worksheet_index.cell_value(i, j))


    def CreateJira(self):
        temp = 0

        try:
            for i in range(1,self.totalItem):
                currentIssue = {
                   "project": {"key": "GSWDIM"},
                   "summary": self.dataList[i][0],
                   "assignee": {"name": self.dataList[i][7]},
                   "issuetype": {"name":"String"},
                   "labels": [self.dataList[i][1], ],
                   "components": [{"name":"GSW_UI_LangTranslation"}],
                   "description":
                   "{panel}"
                   +"\nString Index : " + self.dataList[i][0]
                   +"\nProject : " + self.dataList[i][1]
                   +"\nFeature : " + self.dataList[i][2]
                   +"\nKorean : " + self.dataList[i][3]
                   +"\nEnglish : " + self.dataList[i][4]
                   +"\nPath : " + self.dataList[i][5]
                   +"\nTarget : " + self.dataList[i][6]
                   +"\n{panel}"
                   +"\n{panel}"
                   +"\n\n*[Verification Result]*"
                   +"\n*[OK] : All languages are ok."
                   +"\n*[NG] : Some languages are not ok."
                   +"\n|| ||Translation Verification||TV Image Verification||SW Version||"
                   +"\n|KR/US| | | |"
                   +"\n|BR| | | |"
                   +"\n|EU| | | |"
                   +"\n|AJ/JA/IL| | | |"
                   +"\n|TW| | | |"
                   +"\n|CN/HK| | | |"
                   +"\n{panel}"
                   +"\n{panel}"
                   +"\n\n*[NG Description]*"
                   +"\n*Attach captured Image file about all 'NG'."
                   +"\n*Change status to [RECONFIRM]."
                   +"\n||No||Country Group||Language||Detailed Path||Tanslation NG Description||TV Image NG Description||Result||"
                   +"\n| | | | | | | |"
                   +"\n{panel}"
                }
                issueNo = self.account.create_issue(fields=currentIssue)
#                file=open("D://String Verification.xlsx", "rb")

                file=open(self.fileName2, "rb")
                self.account.add_attachment(issueNo, file, "[Verification] "+self.dataList[i][0])
                file.close()

                if temp==0:
                    temp=1
                    self.progressBar.show()

                self.progressBar.setValue(i/(self.totalItem-1)*100)


            return ("a")
        except:
            print("fail")
            return "fail"
        else:
            print("success")
            return "success"
        print("a")
