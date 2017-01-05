from PyQt5 import uic, QtWidgets
import sys
from  JIRA_Handle import *
from Dev_Master import *

main_ui = uic.loadUiType(GetPath()+'Estreamer_JIRA_Main.ui')[0]

# 상수, GUI의 component, Function Method : 헝가리안
# class 명, 변수 : 'aa_bb_cc_...'

class Main(QtWidgets.QMainWindow, main_ui):

    ## Define UI constants
    # 1. 개발 Master Table
    table_header_master = ["개발Master\n행번호", "지역", "모델명"
                           , "개발PL", "HW PL", "기획", "DV시작"
                           , "DV종료", "JIRA",  "변경점"]
    idxDevMasterRow_TBL_MASTER  = 0
    idxRegion_TBL_MASTER        = 1
    idxModelName_TBL_MASTER     = 2
    idxDevPL_TBL_MASTER         = 3
    idxHwPL_TBL_MASTER          = 4
    idxPlan_TBL_MASTER          = 5
    idxDvStart_TBL_MASTER       = 6
    idxDvEnd_TBL_MASTER         = 7
    idxJiraIssueNo_TBL_MASTER   = 8
    idxDiff_TBL_MASTER          = 9

    # 2. JIRA Table
    table_header_jira = ["모델명","모델JIRA","Spec.확인JIRA"
                         , "실물검증JIRA", "개발Master 버전"
                         , "개발Master\n행번호", "DV종료"
                         , "Spec. Name", "Image Ver."]
    idxModelName_TBL_JIRA       = 0
    idxModelJIRA_TBL_JIRA       = 1
    idxSpecConfimJIRA_TBL_JIRA  = 2
    idxTestJIRA_TBL_JIRA        = 3
    idxDevMasterVer_TBL_JIRA    = 4
    idxDevMasterRow_TBL_JIRA    = 5
    idxDvEnd_TBL_JIRA           = 6
    idxSpecName_TBL_JIRA        = 7
    idxImageVer_TBL_JIRA        = 8
    idxTestJiraObject           = 9

    def __init__(self, parent=None):
        super()
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # UI default init.
        ## set number of table column
        self.tblMaster.setColumnCount(len(Main.table_header_master))
        self.tblMaster.setHorizontalHeaderLabels(Main.table_header_master)
        self.tblMaster.resizeColumnsToContents()

        self.tblJira.setColumnCount(len(Main.table_header_jira))
        self.tblJira.setHorizontalHeaderLabels(Main.table_header_jira)
        self.tblJira.resizeColumnsToContents()
        self.jira_table_data={}

        self.lblStatus.setText('')

        # connect signals & slots
        self.btnOpenMaster.clicked.connect(self.slotOpenDevMaster)
        self.btnLogin.clicked.connect(self.slotLogin)
        self.btnLogout.clicked.connect(self.slotLogout)
        #self.btnCreateIssue.clicked.connect(self.slotCreateIssues)
        self.chkLowend.toggled.connect(self.slotToggleChkLowend)
        self.btnInqIssue.clicked.connect(self.slotInquiryIssues)
        self.btnChkDiff.clicked.connect(self.slotChkDiff)
        self.btnUpdate.clicked.connect(self.slotCreateAndUpdateAllIssues)


        #init member
        self.jira_handler = JIRA_Handler('dev') # Dev. Tracker
        self.jira_tracker = None
        self.login_user = None
        self.jira_diff_conents = None

        # 개발 Master
        self.dev_master = Dev_Master()

        # trye session login
        self.jira_handler.sessionLogin(self)
        self.dev_master.setDevMasterExcel("C:/Users/heuser/Desktop/★V2.3_17년 Global Development Master_161209.xlsx")
        #self.dev_master.setDevMasterExcel("C:/Users/heuser/Desktop/★V2.4_17년 Global Development Master_161227.xlsx")
        self.updateTblMaster()
        self.slotInquiryIssues()

    def setNeedLoginState(self, isNeedLogin):
        self.chkSession.setVisible(isNeedLogin)
        self.lblId.setVisible(isNeedLogin)
        self.txtId.setVisible(isNeedLogin)
        self.lblPwd.setVisible(isNeedLogin)
        self.txtPwd.setVisible(isNeedLogin)
        self.btnLogin.setVisible(isNeedLogin)
        self.lblUserName.setVisible(not isNeedLogin)
        self.btnLogout.setVisible(not isNeedLogin)
        if isNeedLogin is True:
            self.chkSession.setChecked(False)
            self.txtId.setText(self.jira_handler.jira_id)
            self.txtPwd.setText(self.jira_handler.pwd)

    def slotToggleChkLowend(self):
        if self.dev_master.dev_master_excel!=None and self.dev_master.xls_file_name!=None:
            self.updateTblMaster()

    def getDevMasterExcelFile(self):
        ## Open File Dialog (개발 Master 장표 선택)
        fDialog = QtWidgets.QFileDialog(self)
        fDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        excel = fDialog.getOpenFileName(self, '개발 Master 장표 열기',"C://Users//heuser//Desktop", filter='*.xlsx')[0]
        if len(excel)>0:
            self.dev_master.setDevMasterExcel(excel)
        print(excel)
        return excel

    def setTableData(self, tbl, row, col, txt):
        tbl.setItem(row, col, QtWidgets.QTableWidgetItem(txt))

    def setDevTableRowData(self, row, row_data):
        if len(row_data)<Dev_Meta.idxDvEnd+1:
            print("invalid row_data")
            return

        # column index 0 : 개발 Master 상의 Row(행) 번호
        self.setTableData(self.tblMaster
                          , row, Main.idxDevMasterRow_TBL_MASTER
                          , row_data[len(row_data)-1])

        # column index 1 : Region
        self.setTableData(self.tblMaster
                          , row, Main.idxRegion_TBL_MASTER
                          , row_data[Dev_Meta.idxRegion])

        # column index 2 : Model Name
        self.setTableData(self.tblMaster
                          , row, Main.idxModelName_TBL_MASTER
                          , row_data[Dev_Meta.idxModelName])

        # column index 3 : 개발 PL
        self.setTableData(self.tblMaster
                          , row, Main.idxDevPL_TBL_MASTER
                          , row_data[Dev_Meta.idxDevPL])

        # column index 4 : HW PL
        self.setTableData(self.tblMaster
                          , row, Main.idxHwPL_TBL_MASTER
                          , row_data[Dev_Meta.idxHwPL])

        # column index 5 : 기획 담당자
        self.setTableData(self.tblMaster
                          , row, Main.idxPlan_TBL_MASTER
                          , row_data[Dev_Meta.idxHwPL+1])

        # column index 6,7 : DV 시작/종료 일자
        self.setTableData(self.tblMaster
                          , row, Main.idxDvStart_TBL_MASTER
                          , row_data[Dev_Meta.idxDvStart])
        self.setTableData(self.tblMaster
                          , row, Main.idxDvEnd_TBL_MASTER
                          , row_data[Dev_Meta.idxDvEnd])
        return

    def updateTblMaster(self):
        ## clear & init header of table.
        self.tblMaster.clear()
        self.tblMaster.setHorizontalHeaderLabels(Main.table_header_master)

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
            self.setDevTableRowData(row, row_data)

        self.tblMaster.resizeColumnsToContents();
        self.tblMaster.resizeRowsToContents();
        # fill table master [End]

        # set Dev. Master Version to Label
        self.lblVer.setText(self.dev_master.version)


    def slotOpenDevMaster(self):
        print("open master clicked")
        if len(self.getDevMasterExcelFile())==0:
            return
        if self.dev_master.xls_file_name is None:
            return
        self.updateTblMaster()

        if self.tblJira.rowCount()>0:
            # JIRA 와 변경점을 check하고 master table의 변경점 column에
            # 변경사항 내용을 채운다
            self.checkDiffAndFillMasterTbl()

    def slotLogin(self):
        print("login clicked ")

        if self.jira_handler is None:
            self.lblUserName.setText("Check Network status")
            return
        else:
            self.lblUserName.setText("")

        strId = self.txtId.text()
        strPwd = self.txtPwd.text()
        isSaveAccount = self.chkSession.isChecked()
        login_user = self.jira_handler.login(strId, strPwd, isSaveAccount)
        if login_user is not None:
            self.jira_tracker = self.jira_handler.jira
            self.login_user = login_user
            self.lblUserName.setText(login_user.displayName)
            print("Login success")
            self.setNeedLoginState(False)
        else:
            self.lblUserName.setText("Found User : "+str(len(users)))
            self.lblUserName.setText("Login Failed")
            self.login_user = None
            self.setNeedLoginState(True)

    def slotLogout(self):
        print("logout clicked")
        self.txtPwd.setText("")
        self.login_user = None
        self.setNeedLoginState(True)
        self.jira_handler.clearSession()

    def formatSummary(cls, row_data):
        ## formaat : [Estreamer검증][Region][]
        return "["+row_data[cls.region_col_index]+']['+row_data[cls.model_col_index]+']'

    def parseDescriptionField(self, desc):
        lines = desc.split('\r')
        if len(lines)==1:
            lines = desc.split('\n')
        for row in range(len(lines)-1, 0, -1):
            lines[row] = lines[row].strip()   ## trim string
            if len(lines[row])==0:
                del(lines[row])

        return_value={'version':'', 'xls_row':'', 'model_name':'', 'dv_end':''}
        for line in lines:
            tokens = line.strip().split(":")
            if len(tokens)!=2:
                continue
            if tokens[0].strip().endswith('개발 Master Ver.'):
                return_value['version'] = tokens[1].strip()
            elif tokens[0].strip().endswith('엑셀 행 번호'):
                return_value['xls_row'] = tokens[1].strip()
            elif tokens[0].strip().endswith('Model Name'):
                return_value['model_name'] = tokens[1].strip()
            elif tokens[0].strip().endswith('DV 종료'):
                return_value['dv_end'] = tokens[1].strip()
            else:
                ## TBD
                continue
        return return_value

    # JIRA issue가 존재하지 않을 경우 해당 row에 값을 채워넣는다
    def fillNoJIRAtoMasterTbl(self, row):
        # fill JIRA column
        self.setTableData(self.tblMaster, row
                          , self.idxJiraIssueNo_TBL_MASTER
                          , "No Issue:모델")

        # fill 변경점 column
        self.setTableData(self.tblMaster, row
                          , self.idxDiff_TBL_MASTER
                          , "JIRA 생성 필요(모델/Spec. 확인/실물확인)")

    def checkDiffAndFillMasterTbl(self):
        print('checkDiffAndFillMAsterTbl starts')
        # let alias tables and jira data
        tbl_master = self.tblMaster
        tbl_jira   = self.tblJira
        jira_data = self.jira_table_data

        # if there is no issue
        if jira_data is None:
            for row in range(0, tbl_mastser.rowCount()):
                self.fillNoJIRAtoMasterTbl(row)
                self.jira_diff_conents = {}
            tbl_master.resizeColumnsToContents();
            tbl_master.resizeRowsToContents();
            return

        self.jira_diff_conents = {}
        idxModelName = self.idxModelName_TBL_MASTER
        prev_model_name_list = self.dev_master.prev_model_names
        # 개발 Master Table에 JIRA issue No.와 변경사항을 채워넣는다
        for row in range(0, tbl_master.rowCount()):
            model_name = tbl_master.item(row, idxModelName).text()
            model_jira = jira_data.get(model_name)

            ## init. diff contents
            diff_fields = {}
            diff_text = ''

            previous_model_name = ''
            if model_jira is None:
                # Model Name이 변경된 것은 아닌지 점검해보자
                print("check model name 변경 : "+model_name)
                prev_model_names = prev_model_name_list.get(model_name)
                print("prev model lists : "+str(prev_model_names))
                if (prev_model_names is not None) and len(prev_model_names)>0:
                    for prev_name in prev_model_names:
                        print("check prev name : "+prev_name)
                        model_jira = jira_data.get(prev_name)
                        if model_jira is not None:
                            previous_model_name = prev_model_name
                            break;

                # Not found in jira even prev. model name
                if model_jira is None:
                    self.fillNoJIRAtoMasterTbl(row)
                    diff_fields['model_jira'] = 'NoIssue'
                    self.jira_diff_conents[model_name] = diff_fields
                    continue;

                ## Model Name 변경된 Case이다.
                diff_fields['Model Name'] = previous_model_name
                diff_text += ('모델명 변경 : '
                              +previous_model_name
                              +'→'
                              +model_name+'\n')

            idxJira = self.idxJiraIssueNo_TBL_MASTER

            ## fill Jira Issue No.
            self.setTableData(tbl_master
                              , row, idxJira
                              , model_jira[self.idxModelJIRA_TBL_JIRA])


            # check 개발 Master Version and set to Header 'V -> V 변경점'
            dev_version         = self.dev_master.version
            dev_version_jira    = model_jira[Main.idxDevMasterVer_TBL_JIRA]
            if dev_version != dev_version_jira:
                diff_ver = dev_version_jira+'→'+dev_version
                label_header_diff = Main.table_header_master[Main.idxDiff_TBL_MASTER]
                label_header_diff = diff_ver+' '+label_header_diff
                new_header = Main.table_header_master.copy()
                new_header[Main.idxDiff_TBL_MASTER] = label_header_diff
                self.tblMaster.setHorizontalHeaderLabels(new_header)
            else:
                self.tblMaster.setHorizontalHeaderLabels(Main.table_header_master)

                # diff_fields['개발 Master Ver.'] = dev_version
                # diff_text += ('개발 Master Ver. : '
                #               +dev_version_jira
                #               +'→'
                #               +dev_version+'\n')

            # check 개발 Master 행번호
            idxDevRow = self.idxDevMasterRow_TBL_MASTER
            dev_master_row      = tbl_master.item(row, idxDevRow).text()
            dev_master_row_jira = model_jira[self.idxDevMasterRow_TBL_JIRA]
            if dev_master_row != dev_master_row_jira:
                diff_fields['엑셀 행 번호'] = dev_master_row
                diff_text += ('엑셀 행 번호 : '
                              +dev_master_row_jira
                              +'→'
                              +dev_master_row+'\n')

            # check DV 종료 일자
            idxDvEnd = self.idxDvEnd_TBL_MASTER
            dv_end      = tbl_master.item(row, idxDvEnd).text()
            dv_end_jira = model_jira[self.idxDvEnd_TBL_JIRA]
            if dv_end.endswith(dv_end_jira)==False:
                diff_fields['DV 종료'] = dv_end
                diff_text += ('DV 종료 : '+dv_end_jira
                              +'→'+dv_end+'\n')
            if diff_text == '':
                diff_text = '변경점 없음'
                self.jira_diff_conents[model_name] = 'No Change'
            else:
                self.jira_diff_conents[model_name] = diff_fields

            self.setTableData(tbl_master, row, self.idxDiff_TBL_MASTER, diff_text.strip())

        # End of Loop
        tbl_master.resizeColumnsToContents();
        tbl_master.resizeRowsToContents();

    ## type : 'model_jira', 'spec_jira', 'test_jira'
    def fillNoJIRAtoJiraTbl(self, row, type):
        if type == "model_jira":
            self.setTableData(self.tblJira, row
                              , self.idxModelJIRA_TBL_JIRA
                              , 'No Issue:모델')
        elif type == 'spec_jira':
            self.setTableData(self.tblJira, row
                              , self.idxSpecConfimJIRA_TBL_JIRA
                              , 'No Issue:Spec.확인')
        else:             ## test_jira
            self.setTableData(self.tblJira, row
                              , self.idxTestJIRA_TBL_JIRA
                              , 'No Issue:실물확인')
            self.setTableData(self.tblJira, row
                              , self.idxSpecName_TBL_JIRA
                              , 'No Issue:실물확인')
            self.setTableData(self.tblJira, row
                              , self.idxImageVer_TBL_JIRA
                              , 'No Issue:실물확인')

    # 이슈 목록 조회하기 버튼 click slot
    def slotInquiryIssues(self):
        print("Inquiry Issue clicked")
        if self.jira_handler is None or self.jira_tracker is None:
            return
        if self.login_user is None:
            return

        #get all issues of model jira and sub-tasks
        tracker = self.jira_tracker
        jira_handler = self.jira_handler
        all_jira_models = tracker.search_issues(jira_handler.jql_model)
        all_jira_spec   = tracker.search_issues(jira_handler.jql_spec)
        all_jira_test   = tracker.search_issues(jira_handler.jql_test)
        num_all_models = len(all_jira_models)

        self.tblJira.clear()
        self.tblJira.setRowCount(num_all_models)
        self.tblJira.setHorizontalHeaderLabels(Main.table_header_jira)

        if num_all_models==0:
            # TBD : clear diff clause on maser
            self.checkDiffAndFillMasterTbl()
            return

        # header : ["모델명","모델JIRA","Spec.확인JIRA", "실물검증JIRA",
        #           ,"개발Master 버전", "개발Master 행번호"
        #           , "DV종료", "Spec. Name", "Image Ver."]
        # jira_table_data 변수에 모델 별로 데이터를 채워 넣는다
        self.jira_table_data = {}
        for issue in all_jira_models:
            description = issue.raw['fields']['description']
            issue_parsed = self.parseDescriptionField(description)
            model_name = issue_parsed['model_name']
            row_data = []
            # 모델명
            row_data.append(model_name)
            # 모델JIRA
            row_data.append(issue.key)

            # Spec.확인 JIRA : 같은 Model Name이 Summary에 포함된
            # JIRA issue는 유일하다고 가정한다. (2개 이상 존재하여선 안됨)
            for spec_issue in all_jira_spec:
                summary = spec_issue.fields.summary
                ## if found model in spec jira issues
                if summary.find(model_name)>=0:
                    # 일단 Spec.확인 JIRA index에  issue객체를 넣어둔다
                    # string 아니므로 주의가 필요하다.
                    row_data.append(spec_issue)
                    break;
            else:
                row_data.append(None)


            # 실물확인 JIRA
            for test_issue in all_jira_test:
                summary = test_issue.fields.summary
                ## if found model in test jira issues
                if summary.find(model_name)>=0:
                    # 일단 실물확인 Test JIRA index에  issue객체를 넣어둔다
                    # string 아니므로 주의가 필요하다.
                    row_data.append(test_issue)
                    break;
            else:
                row_data.append(None)

            row_data.append(issue_parsed['version'])
            row_data.append(issue_parsed['xls_row'])
            row_data.append(issue_parsed['dv_end'])

            test_issue = row_data[self.idxTestJIRA_TBL_JIRA]

            # Spec. Name과 Image Ver. : Test Issue의 Label들
            row_data.append('') # spec. Name
            row_data.append('') # Image Ver
            if test_issue is None:
                row_data[self.idxSpecName_TBL_JIRA]='No issue:실물확인'
                row_data[self.idxImageVer_TBL_JIRA]='No issue:실물확인'
            else:
                for label in test_issue.fields.labels:
                    if label is None:
                        break;
                    # Image capture ver.은 'capture'로 시작하는 조건을 사용한다
                    if label.lower().find('capture')>=0:
                        row_data[self.idxImageVer_TBL_JIRA]=label

                    # spec. Name은 Lowend 모델명으로 L로 시작하는 조건을 사용한다
                    elif len(label)>0 and label.upper().startswith('L'):
                        row_data[self.idxSpecName_TBL_JIRA] =label

            self.jira_table_data[issue_parsed['model_name']] = row_data

        ## 여기서 부터는 JIRA Table Widget에 채워 넣는다.
        dev_table = self.tblMaster
        jira_table = self.tblJira

        for row in range(0, dev_table.rowCount()):
            model_data_jira = None
            try:
                # try get model name from 개발 Master table
                idxModelName = self.idxModelName_TBL_MASTER
                model_name = self.tblMaster.item(row, idxModelName).text()
                model_data_jira = self.jira_table_data.get(model_name)
            except:
                if model_data_jira is None:
                    self.fillNoJIRAtoMasterTbl(row)
                print("model name : "+model_name+", "+model_data_jira[self.idxModelName_TBL_JIRA])
                continue
            else:
                # set Model Name
                self.setTableData(jira_table, row
                                  , self.idxModelName_TBL_JIRA
                                  , model_name)

                if model_data_jira is None or model_name != model_data_jira[self.idxModelName_TBL_JIRA] or len(model_name)==0:
                    self.fillNoJIRAtoJiraTbl(row, 'model_jira')
                    self.fillNoJIRAtoJiraTbl(row, 'spec_jira')
                    self.fillNoJIRAtoJiraTbl(row, 'test_jira')

                    if model_data_jira is not None:
                        print("Need to check !!!! : "+model_name+", "
                              + model_data_jira[self.idxModelName_TBL_JIRA])
                    continue

                # 하나의 row에 대해 column 단위로 반복 loop하여 UI에 값을 set한다
                for idx_table_jira in range(self.idxModelJIRA_TBL_JIRA
                                            , self.idxImageVer_TBL_JIRA+1):
                    if idx_table_jira in (self.idxTestJIRA_TBL_JIRA
                                          , self.idxSpecConfimJIRA_TBL_JIRA):
                        # set Test JIRA Issue No.
                        # 일단 실물 검증 JIRA index에  issue객체를 넣어두었다
                        # string 아니었므로 주의가 필요 (key 멤버로 출력)
                        if model_data_jira[idx_table_jira] is None:
                            if idx_table_jira == self.idxSpecConfimJIRA_TBL_JIRA:
                                self.fillNoJIRAtoJiraTbl(row, 'spec_jira')
                            else:
                                self.fillNoJIRAtoJiraTbl(row, 'test_jira')
                        else:
                            self.setTableData(jira_table, row
                                              , idx_table_jira
                                              , model_data_jira[idx_table_jira].key)
                    else:
                        # set Model Name, 개발 Master Ver., ...
                        self.setTableData(jira_table, row
                                          , idx_table_jira
                                          , model_data_jira[idx_table_jira])

        if self.tblJira.rowCount()>0:
            self.lblStatus.setText("No JIRA issues for E-Streamer 검증")
        else:
            self.tblJira.resizeColumnsToContents();
            self.tblJira.resizeRowsToContents();
            self.checkDiffAndFillMasterTbl()
            self.lblStatus.setText(str(self.tblJira.rowCount())+" issues found")

    def slotChkDiff(self):
        self.checkDiffAndFillMasterTbl()
        pass

    def slotCreateAndUpdateAllIssues(self):
        # let alias
        dev_table = self.tblMaster
        jira_table = self.tblJira
        jira_table_data = self.jira_table_data
        dev_master = self.dev_master
        dev_table_data = dev_master.table_data
        diff_contents = self.jira_diff_conents
        ver = dev_master.version
        jira_handler = self.jira_handler
        jira = self.jira_tracker

        # for statistics of result
        num_created_model_jira = 0;
        num_created_test_jira = 0;
        num_created_spec_check_jira = 0;
        num_modified_model_jira = 0;
        created_model_jira = []
        created_test_jira = []
        created_spec_check_jira = []
        modified_model_jira = {}


        for row in range(0, dev_table.rowCount()):
            print("row : "+str(row)+" / "+str(dev_table.rowCount()))
            model_name = dev_table.item(row, Main.idxModelName_TBL_MASTER).text()
            issue_no = dev_table.item(row, Main.idxJiraIssueNo_TBL_MASTER).text()
            model_data = dev_master.getModelDataFromModelName(model_name)
            is_model_name_changed = False
            is_create_model_jira = False
            model_issue = None

            if model_data is None:
                print("Need to check. why model data not exist : "+model_name)
                continue

            # 1. model name 변경 check한다
            model_data_jira = jira_table_data.get(model_name)

            if model_data_jira is None:
                diffs = diff_contents.get(model_name)
                if diffs is not None:
                    prev_model_name = diffs.get('Model Name')
                    if (prev_model_name is not None) and len(prev_model_name)>0:
                        # model 명이 변경된 경우
                        print("changed model name : "
                              +prev_model_name+"→"+model_name)
                        model_data_jira = jira_table_data.get(prev_model_name)
                        if model_data_jira is None:
                            print("can't find model data of jira with prev. name")
                            print("need to check !!!")
                            is_create_model_jira = True
                        else:
                            ## model name 변경 case
                            ## : prev_model_name존재 && jira_model data도 존재
                            is_model_name_changed = True
                    else:
                        is_create_model_jira = True
                else:
                    is_create_model_jira = True

            # 2. model jira를 생성해야하는 경우 check & create jira & sub-tasks
            if is_create_model_jira or issue_no.startswith('No Issue'):
                result = self.jira_handler.createModelIssueAndSubTasks(ver, model_data)
                if result is True:
                    num_created_model_jira+=1
                    created_model_jira.append(model_name)
                    print(str(num_created_model_jira)+' issue created.')
                    continue;
                else:
                    print("try to create model jira but failed to create")
                    print("Need check. Skip create or update : "+model_name)
                    continue

            # 3. field를 update한다
            try:
                if is_model_name_changed :
                    # model_name 변경
                    model_issue = jira_handler.inquiryModelIssue(prev_model_name)
                else:
                    model_issue = jira_handler.inquiryModelIssue(model_name)
            except:
                # do nothing
                pass

            if model_issue is None:
                print("model issue is None. Need to check !! ")
                if is_model_name_changed :
                    print("prev_model : "
                          +prev_model_name
                          +", model name : "
                          +model_name)
                else:
                    print("model name : "+model_name)
                continue;

            ## 2-1. check & create sub-task1 : spec.확인요청 JIRA
            if model_data_jira[self.idxSpecConfimJIRA_TBL_JIRA] is None:
                spec_fields = self.getFieldsForSpecCheckIssue(model, model_issue)
                jira.create_issue(fields=spec_fields)
            ## 3.의 model issue update 진행 필요

            ## 2-2. check & create sub-task2 : 실물확인 JIRA
            if model_data_jira[self.idxTestJIRA_TBL_JIRA] is None:
                test_fields = self.getFieldsForTestIssue(model, model_issue)
                jira.create_issue(fields=test_fields)
            ## 3.의 model issue update 진행 필요

            # 3. Update fields of model issue
            model_fields = jira_handler.getFieldsForModelIssue(ver, model_data)
            model_issue.update(fields=model_fields)

            num_modified_model_jira +=1
            modified_model_jira[model_name] = self.jira_diff_conents.get(model_name)

            self.lblStatus.setText(str(num_modified_model_jira)
                                  +" / "+str(len(self.jira_diff_conents.keys()))
                                  + ' modified')

        print('modified jira contents')
        print(str(modified_model_jira))

        self.lblStatus.setText(str(num_created_model_jira)
                               +' issue(s) created. '
                               + str(num_modified_model_jira)
                               +' issue(s) modified')

        self.slotInquiryIssues()
        if self.tblJira.rowCount()>0:
            self.slotChkDiff()

    # @deprecated : replaced with slotCreateAndUpdateAllIssues
    # def slotCreateIssues(self):
    #     print("create issues clicked")
    #     if self.login_user is None or len(self.dev_master.table_data)==0:
    #         return
    #
    #     created_num = 0
    #     jira = self.jira_handler
    #     for model in self.dev_master.table_data:
    #         result = jira.createModelIssueAndSubTasks(self.dev_master.version
    #                                                   , model)
    #         if result is True:
    #             created_num +=1
    #
    #         print(str(created_num)+ " / "
    #               +str(len(self.dev_master.table_data))+" 생성 완료")
    #
    #         self.lblStatus.setText(str(created_num)+" / "
    #                                + str(len(self.dev_master.table_data))
    #                                +" 이슈 생성 완료")
    #
    #     self.slotInquiryIssues()
    #     #print("found : "+self.jira_tracker.search_issues('Project=ESTREAMER AND Summary~"'+self.table_data[0][Meta_Info.idxModelNameCol]+'"')[0].key)

app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    myWindow = Main(None)
    myWindow.show()
    app.exec_()
