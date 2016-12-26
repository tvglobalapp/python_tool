from PyQt5 import uic, QtWidgets
import sys
from  JIRA_Handle import *
from Dev_Master import *

main_ui = uic.loadUiType('d://project//python//JIRA_Estreamer//Estreamer_JIRA_Main.ui')[0]
# main_ui = uic.loadUiType('Estreamer_JIRA_Main.ui')[0]

# 상수, GUI의 component, Function Method : 헝가리안
# class 명, 변수 : 'aa_bb_cc_...'

class Main(QtWidgets.QMainWindow, main_ui):

    table_header = ["개발Master\n행번호", "지역", "모델명"    \
                    , "개발PL", "HW PL", "기획", "DV시작"     \
                    , "DV종료", "E-Streamer 검증여부"
                    , "JIRA",   "Status"]

    def __init__(self, parent=None):
        super()
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # UI default init.
        ## set number of table column
        self.tblMaster.setColumnCount(11)
        self.tblMaster.setHorizontalHeaderLabels(Main.table_header)
        self.tblMaster.resizeColumnsToContents()

        self.lblStatus.setText('')

        # connect signals & slots
        self.btnOpenMaster.clicked.connect(self.slotOpenDevMaster)
        self.btnLogin.clicked.connect(self.slotLogin)
        self.btnCreateIssue.clicked.connect(self.slotCreateIssues)
        self.chkLowend.toggled.connect(self.slotToggleChkLowend)


        #init member
        self.jira_handler = JIRA_Handler('dev') # Dev. Tracker
        self.jira_tracker = None
        self.login_user = None

        # 개발 Master
        self.dev_master = Dev_Master()

        ## 세션 관리(read/write) 필요
        #self.txtId.setText("ybin.cho")
        #self.txtPwd.setText("@@@@@@pwd@@@@@@")
        #self.slotLogin()
        #self.dev_master.setDevMasterExcel("C:/Users/heuser/Desktop/★V2.2_17년 Global Development Master_161121.xlsx")
        #self.updateTblMaster()


    def slotToggleChkLowend(self):
        if self.dev_master.dev_master_excel!=None:
            self.updateTblMaster()

    def getDevMasterExcelFile(self):
        ## Open File Dialog (개발 Master 장표 선택)
        fDialog = QtWidgets.QFileDialog(self)
        fDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        excel = fDialog.getOpenFileName(self, '개발 Master 장표 열기',"C://Users//heuser//Desktop", filter='*.xlsx')[0]
        self.dev_master.setDevMasterExcel(excel)
        print(excel)

    def setTableData(self, row, col, txt):
        self.tblMaster.setItem(row, col, QtWidgets.QTableWidgetItem(txt))

    def setTableRowData(self, row, row_data):
        if len(row_data)<Dev_Meta.idxDvEnd+1:
            print("invalid row_data")
            return

        # table index 0 : 개발 Master 상의 Row(행) 번호
        self.setTableData(row, 0, row_data[len(row_data)-1])

        # table index 1 : Region
        self.setTableData(row, 1, row_data[Dev_Meta.idxRegion])

        # table index 2 : Model Name
        self.setTableData(row, 2, row_data[Dev_Meta.idxModelName])

        # table index 3 : 개발 PL
        self.setTableData(row, 3, row_data[Dev_Meta.idxDevPL])

        # table index 4 : HW PL
        self.setTableData(row, 4, row_data[Dev_Meta.idxHwPL])

        # table index 5 : 기획 담당자
        self.setTableData(row, 5, row_data[Dev_Meta.idxHwPL+1])

        # table index 6,7 : DV 시작/종료 일자
        self.setTableData(row, 6, row_data[Dev_Meta.idxDvStart])
        self.setTableData(row, 7, row_data[Dev_Meta.idxDvEnd])
        return

    def updateTblMaster(self):
        ## clear & init header of table.
        self.tblMaster.clear()
        self.tblMaster.setHorizontalHeaderLabels(Main.table_header)

        # reload dev_master_excel : dev_master.table_data
        self.dev_master.updateDevMaster(self.chkLowend.isChecked())

        # fill table master [Start]
        table_data = self.dev_master.table_data
        total_row = len(table_data)
        # set row count of body
        self.tblMaster.setRowCount(total_row)

        for row in range(len(table_data)):
            #print("row:"+str(self.table_data[row]))
            row_data = table_data[row]
            self.setTableRowData(row, row_data)

        self.tblMaster.resizeColumnsToContents();
        self.tblMaster.resizeRowsToContents();
        # fill table master [End]

    def slotOpenDevMaster(self):
        print("open master clicked")
        self.getDevMasterExcelFile();

        if self.dev_master.xls_file_name==None:
            return
        self.updateTblMaster()

    def slotLogin(self):
        print("login clicked ")

        if self.jira_handler==None:
            self.lblUserName.setText("Check Network status")
        else:
            self.lblUserName.setText("")

        strId = self.txtId.text()
        strPwd = self.txtPwd.text()

        if ("success"==self.jira_handler.login(strId, strPwd)):
            self.jira_tracker = self.jira_handler.jira
            users = self.jira_tracker.search_users(strId)
            if len(users)==1:   ## found user
                self.login_user = users[0]
                self.lblUserName.setText(users[0].displayName)
                print("Login success")
            else:
                self.lblUserName.setText("Found User : "+str(len(users)))
                self.login_user = None
        else:
            self.lblUserName.setText("Login Failed")
            self.login_user = None


    def formatSummary(cls, row_data):
        ## formaat : [Estreamer검증][Region][]
        return "["+row_data[cls.region_col_index]+']['+row_data[cls.model_col_index]+']'
    def slotCreateIssues(self):
        print("create issues clicked")
        if type(self.login_user) == None or len(self.dev_master.table_data)==0:
            return

        estreamer_project =  self.jira_tracker.project("ESTREAMER")
        createdNum = 0

        for model in self.dev_master.table_data:
            ## set issue info
            current_issue = self.jira_handler.issue_template.copy()
            current_issue['summary'] = current_issue['summary']+"["+model[Dev_Meta.idxRegion]+"] "+ model[Dev_Meta.idxModelName]
            current_issue['labels'].append(self.dev_master.version)
            current_issue['description']= '''
            개발 Master Ver. : {ver}\n
            엑셀 행 번호: {row}\n
            Model Name : {model}\n
            DV 시작 : {dv_start}\n
            DV 종료 : {dv_end}\n
            담당자 ===========\n
            SW : 이가영Y\n
            HW PL : {hwpl}\n
            기획 : {plan}
            '''.format(ver=self.dev_master.version, row=model[len(model)-1], model=model[Dev_Meta.idxModelName], \
                       hwpl= model[Dev_Meta.idxHwPL], plan=model[Dev_Meta.idxHwPL+1], \
                       dv_start=model[Dev_Meta.idxDvStart], dv_end=model[Dev_Meta.idxDvEnd])
            issue = self.jira_tracker.create_issue(fields=current_issue)
            # if createdNum%10000 ==1:
            #     issue.add_field_value('Watchers',[{'name':'seungyong.jun'}, {'name':'gayoung.lee'}, {'name':'sungbin.na'}])
            createdNum +=1
            self.lblStatus.setText(str(createdNum)+" / "+ str(len(self.dev_master.table_data))+" 이슈 생성 완료")

        #print("found : "+self.jira_tracker.search_issues('Project=ESTREAMER AND Summary~"'+self.table_data[0][Meta_Info.idxModelNameCol]+'"')[0].key)

app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    myWindow = Main(None)
    myWindow.show()
    app.exec_()
