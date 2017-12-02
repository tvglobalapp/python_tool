# -*- coding: utf-8 -*-
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree
import sys
from Common_Util import *

settings_ui = uic.loadUiType('Settings.ui')[0]

class Settings(QtWidgets.QDialog, settings_ui):
    def __init__(self, jira_tracker, main_ui, parent=None):
        super()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.jira_handler = jira_tracker

        # try session login
        self.jira_handler.sessionLogin(self, False)
        self.tracker = self.jira_handler.jira

        # Estreamer 담당자 설정 : Session Login Account
        self.owner_sw = self.jira_handler.jira_id
        self.txtOwnerSw.setText(self.owner_sw)

        # global 설정
        self.settings_file_name = 'Settings.xml'
        self.jira_templates = 'jira_template.xml'
        self.main_ui = main_ui

        # JIRA 설정
        self.project_id = ""
        self.max_result_cnt = ''
        self.labels = []
        self.jql_model = ""
        self.jql_spec = ""
        self.jql_test = ""
        self.watchers = []
        self.spec_desc = ''
        self.test_desc = ''

        # 개발 마스터 설정
        self.mp_year = ''
        self.grades = []
        self.mainsocs_lowend = []
        self.mainsocs_webos = []
        self.drop_model_keywords = []

        self.idx_worksheet = 0
        self.row_header = 0
        self.row_start_model = 0
        self.col_history = 0
        self.col_region = 0
        self.col_model_name = 0
        self.col_dev_pl = 0
        self.col_hw_pl = 0
        self.col_grade = 0
        self.col_mainsoc = 0
        self.col_panel_type = 0
        self.col_dv_start = 0
        self.col_dv_end = 0

        ## 기획
        self.owner_plan = {'KR':'', 'US':'', 'JP':'','BR':'', 'TW':'',\
                           'CO':'', 'EU':'','CIS':'','CN':'', 'AJ':'',\
                           'JA':'', 'HK':''}

        self.owner_plan_depart = ''

        # register event handler
        self.btnSave.clicked.connect(self.saveSettings)
        self.btnClose.clicked.connect(self.closeSettings)
        self.btnResetJqlModel.clicked.connect(self.resetJqlModel)
        self.btnResetJqlSpec.clicked.connect(self.resetJqlSpec)
        self.btnResetJqlTest.clicked.connect(self.resetJqlTest)


        self.xml = None
        self.loadSettings()

    def closeSettings(self):
        self.main_ui.updateSettings(self)
        self.close()

    # deprecated
    def clearAllTxt(self):
        self.txtProject.setText('')
        self.txtJiraMaxResultCnt.setText('')
        self.txtJiraLabels.setText('')
        self.txtWatchers.setText('')
        self.txtSpecDesc.setText('')
        self.txtTestDesc.setText('')
        self.txtMpYear.setText('')
        self.txtGrades.setText('')
        self.txtMainSoCwebOS.setText('')
        self.txtMainSoCLowend.setText('')
        self.txtDropModelKeywords.setText('')
        self.txtOwnerPlanDepart.setText('')
        self.txtOwnerPlanKR.setText('')
        self.txtOwnerPlanUS.setText('')
        self.txtOwnerPlanJP.setText('')
        self.txtOwnerPlanBR.setText('')
        self.txtOwnerPlanTW.setText('')
        self.txtOwnerPlanCO.setText('')
        self.txtOwnerPlanEU.setText('')
        self.txtOwnerPlanCIS.setText('')
        self.txtOwnerPlanCN.setText('')
        self.txtOwnerPlanHK.setText('')
        self.txtOwnerPlanAJ.setText('')
        self.txtOwnerPlanJA.setText('')
        # 개발 마스터의 Xls 메타 정보 등 누락 항목 존재

    def isValidNameOrId(self, name_id_key, depart_name):
        t = self.tracker
        users = t.search_users(name_id_key)
        if len(users)==1:
            return True
        elif len(users)==0:
            return False
        else:
            if depart_name is None or type(depart_name)!=str or depart_name=='':
                return False
            cnt_found = 0;
            for user in users:
                if user.displayName.find(depart_name)>0:
                    #found
                    cnt_found +=1
            if cnt_found==1:
                return True
        return False

    def getUserName(self, jira_id):
        t = self.tracker
        users = t.search_users(jira_id)
        if len(users)==0:
            return None
        return users[0].displayName

    def getUserId(self, name, depart_name):
        t = self.tracker
        users = t.search_users(name)
        if len(users)==1:
            return users[0].key
        elif len(users)==0:
            return ''
        else:
            if depart_name is None or type(depart_name)!=str or depart_name=='':
                return ''
            cnt_found = 0;
            jira_id = ''
            for user in users:
                if user.displayName.find(depart_name)>0:
                    #found
                    cnt_found +=1
                    jira_id = user.key
            if cnt_found==1:
                return jira_id
        return ''


    # list -> 'a, b, c, ...' format의 string으로 조합
    def getMergedClauses(self, str_list):
        result = ''
        if len(str_list)>0:
            result = str_list[0]
            for i in range(1, len(str_list)):
                if len(str_list[i])>0:
                    result += ', '+str_list[i]
        return result

    def updateToUi(self):
        # JIRA 설정
        self.txtProject.setText(self.project_id)
        self.txtJiraMaxResultCnt.setText(self.max_result_cnt)
        labels = self.getMergedClauses(self.labels)
        self.txtJiraLabels.setText(labels)
        watchers = self.getMergedClauses(self.watchers)
        self.txtWatchers.setText(watchers)
        self.txtJqlModel.setText(self.jql_model)
        self.txtJqlSpec.setText(self.jql_spec)
        self.txtJqlTest.setText(self.jql_test)
        self.txtSpecDesc.document().setPlainText(self.spec_desc)
        self.txtTestDesc.document().setPlainText(self.test_desc)

        # 개발 마스터 설정
        self.txtMpYear.setText(self.mp_year)
        grades = self.getMergedClauses(self.grades)
        self.txtGrades.setText(grades)
        mainsocs_webos = self.getMergedClauses(self.mainsocs_webos)
        self.txtMainSoCwebOS.setText(mainsocs_webos)
        mainsocs_lowend = self.getMergedClauses(self.mainsocs_lowend)
        self.txtMainSoCLowend.setText(mainsocs_lowend)
        drop_model_keywords = self.getMergedClauses(self.drop_model_keywords)
        self.txtDropModelKeywords.setText(drop_model_keywords)
        self.txtIdxWs.setText(str(self.idx_worksheet))
        self.txtRowHeader.setText(str(self.row_header))
        self.txtColHistory.setText(str(self.col_history))
        self.txtColRegion.setText(str(self.col_region))
        self.txtColModelName.setText(str(self.col_model_name))
        self.txtColDevPL.setText(str(self.col_dev_pl))
        self.txtColHwPL.setText(str(self.col_hw_pl))
        self.txtColGrade.setText(str(self.col_grade))
        self.txtColMainSoC.setText(str(self.col_mainsoc))
        self.txtColPanelType.setText(str(self.col_panel_type))
        self.txtColDvStart.setText(str(self.col_dv_start))
        self.txtColDvEnd.setText(str(self.col_dv_end))

        # 담당자 설정
        self.txtOwnerSw.setText(self.owner_sw)
        self.txtOwnerPlanDepart.setText(self.owner_plan_depart)
        self.txtOwnerPlanKR.setText(self.owner_plan['KR'])
        self.txtOwnerPlanUS.setText(self.owner_plan['US'])
        self.txtOwnerPlanJP.setText(self.owner_plan['JP'])
        self.txtOwnerPlanBR.setText(self.owner_plan['BR'])
        self.txtOwnerPlanTW.setText(self.owner_plan['TW'])
        self.txtOwnerPlanCO.setText(self.owner_plan['CO'])
        self.txtOwnerPlanEU.setText(self.owner_plan['EU'])
        self.txtOwnerPlanCIS.setText(self.owner_plan['CIS'])
        self.txtOwnerPlanCN.setText(self.owner_plan['CN'])
        self.txtOwnerPlanHK.setText(self.owner_plan['HK'])
        self.txtOwnerPlanAJ.setText(self.owner_plan['AJ'])
        self.txtOwnerPlanJA.setText(self.owner_plan['JA'])

    def loadSettings(self):
        try:
            tree = ET.parse(self.settings_file_name)
        except FileNotFoundError:
            print(settings_file_name+' load failed')
            return

        root = tree.getroot()

        # 1. load jira settings
        jira_setting = root.find('jira_setting')
        self.project_id = jira_setting.findtext('project_id')
        self.max_result_cnt = jira_setting.findtext('max_result_cnt')
        self.labels=[]
        labels = jira_setting.findall('label')
        for label in labels:
            self.labels.append(label.text)
        self.watchers=[]
        watchers = jira_setting.findall('watcher')
        for watcher in watchers:
            self.watchers.append(watcher.text)
        self.jql_model = jira_setting.findtext('jql_model_issue')
        self.jql_spec = jira_setting.findtext('jql_spec_issue')
        self.jql_test = jira_setting.findtext('jql_test_issue')
        self.spec_desc = jira_setting.findtext('spec_desc')
        self.test_desc = jira_setting.findtext('test_desc')


        # 2. Load dev. master settings
        dev_master = root.find('dev_master_setting')
        self.mp_year = dev_master.findtext('mp_year')
        self.grades = []
        grades = dev_master.findall('grade')
        for grade in grades:
            self.grades.append(grade.text)
        self.mainsocs_webos = []
        mainsocs_webos = dev_master.findall('mainsoc_webos')
        for mainsoc in mainsocs_webos:
            self.mainsocs_webos.append(mainsoc.text)
        self.mainsocs_lowend = []
        mainsocs_lowend = dev_master.findall('mainsoc_lowend')
        for mainsoc in mainsocs_lowend:
            self.mainsocs_lowend.append(mainsoc.text)
        self.drop_model_keywords = []
        drop_model_keywords = dev_master.findall('drop_model_keyword')
        for keyword in drop_model_keywords:
            self.drop_model_keywords.append(keyword.text)
        self.idx_worksheet      = int(dev_master.findtext('idx_worksheet'))
        self.row_header         = int(dev_master.findtext('row_header'))
        self.col_history        = int(dev_master.findtext('col_history'))
        self.col_region         = int(dev_master.findtext('col_region'))
        self.col_model_name     = int(dev_master.findtext('col_model_name'))
        self.col_dev_pl         = int(dev_master.findtext('col_dev_pl'))
        self.col_hw_pl          = int(dev_master.findtext('col_hw_pl'))
        self.col_grade          = int(dev_master.findtext('col_grade'))
        self.col_mainsoc        = int(dev_master.findtext('col_mainsoc'))
        self.col_panel_type     = int(dev_master.findtext('col_panel_type'))
        self.col_dv_start       = int(dev_master.findtext('col_dv_start'))
        self.col_dv_end         = int(dev_master.findtext('col_dv_end'))

        # 3. Load 담당자 settings
        owners = root.find('owners')
        self.owner_sw = owners.findtext('estreamer_sw')
        self.owner_plan_depart = owners.findtext('plan_dept')
        self.owner_plan.clear()
        self.owner_plan['KR'] = owners.findtext('plan_KR')
        self.owner_plan['US'] = owners.findtext('plan_US')
        self.owner_plan['JP'] = owners.findtext('plan_JP')
        self.owner_plan['BR'] = owners.findtext('plan_BR')
        self.owner_plan['TW'] = owners.findtext('plan_TW')
        self.owner_plan['CO'] = owners.findtext('plan_CO')
        self.owner_plan['EU'] = owners.findtext('plan_EU')
        self.owner_plan['CIS'] = owners.findtext('plan_CIS')
        self.owner_plan['CN'] = owners.findtext('plan_CN')
        self.owner_plan['AJ'] = owners.findtext('plan_AJ')
        self.owner_plan['JA'] = owners.findtext('plan_JA')
        self.owner_plan['HK'] = owners.findtext('plan_HK')

        # 4. Update to UI
        self.updateToUi()

        print("Settings loading success")

    def resetJqlModel(self):
        jql_default = 'project='+self.project_id
        labels = self.labels.copy()
        for label in labels:
            jql_default = jql_default + ' and labels='+label
        self.jql_model = jql_default+' and labels='+'model'
        self.txtJqlModel.setText(self.jql_model)

        self.saveSettings()

    def resetJqlSpec(self):
        jql_default = 'project='+self.project_id
        labels = self.labels.copy()
        for label in labels:
            jql_default = jql_default + ' and labels='+label
        self.jql_spec = jql_default+' and labels='+'spec'
        self.txtJqlSpec.setText(self.jql_spec)

        self.saveSettings()

    def resetJqlTest(self):
        jql_default = 'project='+self.project_id
        labels = self.labels.copy()
        for label in labels:
            jql_default = jql_default + ' and labels='+label
        self.jql_test = jql_default+' and labels='+'test'
        self.txtJqlTest.setText(self.jql_test)

        self.saveSettings()

    def saveSettings(self):
        settings = Element('settings')

        # 1. JIRA 설정
        jira = Element('jira_setting')
        ## project id
        SubElement(jira, 'project_id').text = self.txtProject.text()

        ## max result count
        SubElement(jira, 'max_result_cnt').text \
                                    = self.txtJiraMaxResultCnt.text()

        ## labels
        for label in self.txtJiraLabels.text().split(','):
            SubElement(jira, 'label').text = label.strip()

        ## watchers
        for watcher in self.txtWatchers.text().split(','):
            w = watcher.strip()
            if len(w)==0:
                break;
            if self.isValidNameOrId(w, None):
                SubElement(jira, 'watcher').text = w

        # JQL to inquiry jira by issue type
        ## Model Issue
        SubElement(jira, 'jql_model_issue').text = self.txtJqlModel.text()
        ## Subtask : Spec Issue
        SubElement(jira, 'jql_spec_issue').text = self.txtJqlSpec.text()
        ## Subtask : 실물검증 Issue
        SubElement(jira, 'jql_test_issue').text = self.txtJqlTest.text()

        ## spec issue description
        SubElement(jira, 'spec_desc').text  \
            = self.txtSpecDesc.document().toPlainText()

        ## test issue description
        SubElement(jira, 'test_desc').text  \
            = self.txtTestDesc.document().toPlainText()

        indent(jira)
        settings.append(jira)

        # 2. 개발 마스터 설정
        dev_master_setting = Element('dev_master_setting')
        ## product year
        SubElement(dev_master_setting, 'mp_year').text=self.txtMpYear.text()
        ## grades
        for grade in self.txtGrades.text().split(','):
            SubElement(dev_master_setting, 'grade').text = grade.strip()
        ## Main SoC : webOS
        for mainsoc in self.txtMainSoCwebOS.text().split(','):
            SubElement(dev_master_setting, 'mainsoc_webos').text \
                = mainsoc.strip().upper()
        ## Main SoC : Lowend
        for mainsoc in self.txtMainSoCLowend.text().split(','):
            SubElement(dev_master_setting, 'mainsoc_lowend').text \
                = mainsoc.strip().upper()
        ## Drop Model Keywords
        for dropKeywords in self.txtDropModelKeywords.text().split(','):
            SubElement(dev_master_setting, 'drop_model_keyword').text \
                = dropKeywords.strip()
        ## 엑셀 메타 정보 (행/열 index)
        SubElement(dev_master_setting, 'idx_worksheet').text \
                = self.txtIdxWs.text().strip()
        SubElement(dev_master_setting, 'row_header').text \
                = self.txtRowHeader.text().strip()
        SubElement(dev_master_setting, 'col_history').text \
                = self.txtColHistory.text().strip()
        SubElement(dev_master_setting, 'col_region').text \
                = self.txtColRegion.text().strip()
        SubElement(dev_master_setting, 'col_model_name').text \
                = self.txtColModelName.text().strip()
        SubElement(dev_master_setting, 'col_dev_pl').text \
                = self.txtColDevPL.text().strip()
        SubElement(dev_master_setting, 'col_hw_pl').text \
                = self.txtColHwPL.text().strip()
        SubElement(dev_master_setting, 'col_grade').text \
                = self.txtColGrade.text().strip()
        SubElement(dev_master_setting, 'col_mainsoc').text \
                = self.txtColMainSoC.text().strip()
        SubElement(dev_master_setting, 'col_panel_type').text \
                = self.txtColPanelType.text().strip()
        SubElement(dev_master_setting, 'col_dv_start').text \
                = self.txtColDvStart.text().strip()
        SubElement(dev_master_setting, 'col_dv_end').text \
                = self.txtColDvEnd.text().strip()

        settings.append(dev_master_setting)

        # 3. 담당자 설정
        owners = Element('owners')
        ## estreamer s/w 담당자
        owner_sw = self.txtOwnerSw.text().strip()
        if self.isValidNameOrId(owner_sw, None):
            SubElement(owners, 'estreamer_sw').text = owner_sw
        else:
            SubElement(owners, 'estreamer_sw').text = self.estreamer_sw


        ## 향별 기획 담당자
        ### 기획 부서명 Prefix
        depart_name = self.txtOwnerPlanDepart.text().strip()
        SubElement(owners, 'plan_dept').text = depart_name

        ### KR
        owner_plan = self.txtOwnerPlanKR.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['KR'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_KR').text = self.owner_plan['KR']

        ### US
        owner_plan = self.txtOwnerPlanUS.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['US'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_US').text = self.owner_plan['US']

        ### JP
        owner_plan = self.txtOwnerPlanJP.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['JP'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_JP').text = self.owner_plan['JP']

        ### BR
        owner_plan = self.txtOwnerPlanBR.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['BR'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_BR').text = self.owner_plan['BR']

        ### TW
        owner_plan = self.txtOwnerPlanTW.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['TW'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_TW').text = self.owner_plan['TW']

        ### CO
        owner_plan = self.txtOwnerPlanCO.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['CO'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_CO').text = self.owner_plan['CO']

        ### EU
        owner_plan = self.txtOwnerPlanEU.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['EU'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_EU').text = self.owner_plan['EU']

        ### CIS
        owner_plan = self.txtOwnerPlanCIS.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['CIS'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_CIS').text = self.owner_plan['CIS']

        ### CN
        owner_plan = self.txtOwnerPlanCN.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['CN'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_CN').text = self.owner_plan['CN']

        ### AJ
        owner_plan = self.txtOwnerPlanAJ.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['AJ'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_AJ').text = self.owner_plan['AJ']

        ### JA
        owner_plan = self.txtOwnerPlanJA.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['JA'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_JA').text = self.owner_plan['JA']

        ### HK
        owner_plan = self.txtOwnerPlanHK.text().split('/')[0].strip()
        if self.isValidNameOrId(owner_plan, depart_name):
            ## jira id
            self.owner_plan['HK'] = self.getUserId(owner_plan, depart_name)
            SubElement(owners, 'plan_HK').text = self.owner_plan['HK']

        settings.append(owners)
        indent(settings)

        # write to xml file
        ElementTree(settings).write(self.settings_file_name)

        # update to settings instance
        self.loadSettings()

app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    myWindow = Settings(None)
    myWindow.show()
    sys.exit(app.exec_())
