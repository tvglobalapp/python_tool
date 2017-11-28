from jira.client import JIRA
import jira.config
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree
from Settings import *


event = 'dev'     ## dev / release
#dev_local_path = 'd://project//python//JIRA_Estreamer//'

#jira_usr = jira.config.get_jira('hlm')

# HLM Dev. Tracker
hlm_dev_url = "http://hlm.lge.com/issue"

issue_url_prefix = hlm_dev_url+"/browse/"

# Jira Login을 위한 session file name
session_file_name = 'jira_session.xml'

# jira issue query
# Settings 통해 project id와 label로 query 생성
# setSettings() 참조 (2017. 9)

# jql_default = 'project='+project_id+' and '
# jql_model_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물검증)'
# jql_test_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물확인)'
# jql_spec_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_SPEC확인)'
# jql_model_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물검증_TEST)'
# jql_test_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물확인_TEST)'
# jql_spec_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_SPEC확인_TEST)'

# E-Streamer S/W 담당자 : JIRA reporter & default assignee
#estreamer_sw = 'gayoung.lee'
# settings 통해 참조 (settings.owner_sw)

# Jira 에서 issue 조회 시 maxResult개수를 지정해야 한다
# @ jira_tracker.search_issues [default:50]
# settings에서 가져 온다 (2017. 9)
# maxResult = 200

# Fileter : 실물검증TEST -> 실물검증
# project_id = 'SSP' -> 'ESTREAMER'
# filter name : L17_ESTREAMER_D_VA_XXXX_TEST -> L17_ESTREAMER_D_VA_XXXX

class JIRA_Handler:
    main_issue_watchers = ['ybin.cho'] #, 'gayoung.lee']

    def __init__(self):
        # jira server url
        global hlm_dev_url
        global session_file_name

        self.jira_id=''
        self.pwd=''

        #default dev tracker
        self.url = hlm_dev_url

        self.issue_model_template = None
        self.issue_spec_template = None
        self.issue_test_template = None
        self.create_issue_list = []


        self.jira=None
        self.jira_project_id=''

        self.jql_model =''
        self.jql_test = ''
        self.jql_spec = ''
        self.maxResultJira = 50

        self.session_file = session_file_name
        self.settings = None

    def setSettings(self, settings):
        self.settings = settings
        self.jira_project_id = settings.project_id
        # construct issue templates
        self.default_labels = settings.labels
        labels = self.default_labels.copy()
        labels.append('model')
        self.issue_model_template = {'project':{"key":settings.project_id}
                                   ,"assignee":{"name":settings.owner_sw}
                                   ,'summary': '[Estreamer검증]'
                                   ,'description':'Test 중'
                                   ,'labels':labels
                                   ,'issuetype':{'name':'Task'}}

        labels = self.default_labels.copy()
        labels.append('spec')
        self.issue_spec_template = {'project':{"key":settings.project_id}
                                   ,"assignee":{"name":settings.owner_sw}
                                   ,'summary': '[Estreamer검증]'
                                   ,'description':'Test 중'
                                   ,'labels':labels}

        labels = self.default_labels.copy()
        labels.append('test')
        self.issue_test_template = {'project':{"key":settings.project_id}
                                   ,"assignee":{"name":settings.owner_sw}
                                   ,'summary': '[Estreamer검증]'
                                   ,'description':'Test 중'
                                   ,'labels':labels}

        # construct JQLs to inquiry issue
        self.jql_model = settings.jql_model
        self.jql_spec = settings.jql_spec
        self.jql_test = settings.jql_test

        # get other jira configurations
        self.maxResultJira = settings.max_result_cnt

    def saveSession(self):
        ## check login success
        if self.jira is None:
            return
        session = Element('Session')

        server = Element('jira_url')
        server.text = self.url
        session.append(server)

        account_id = Element('id')
        account_id.text = self.jira_id
        session.append(account_id)

        account_pwd = Element('passwd')
        account_pwd.text = self.pwd
        session.append(account_pwd)

        ## create or save session file
        ElementTree(session).write(self.session_file)

    def clearSession(self):
        try:
            tree = ET.parse(self.session_file)
        except FileNotFoundError:
            # need to do nothing
            return
        session = Element('Session')
        ## create or save session file
        ## write empty session tag to xml
        ElementTree(session).write(self.session_file)

    # local session file을 이용한 Login
    # Main의 slotLogin 과 동일한 동작 수행
    def sessionLogin(self, main_ui, need_update_to_ui):
        try:
            tree = ET.parse(self.session_file)
        except FileNotFoundError:
            print(session_file_name)
            if need_update_to_ui is True:
                main_ui.setNeedLoginState(True)
            return

        root = tree.getroot()
        url = ''
        jira_id = ''
        pwd = ''
        try:
            url = root.find('jira_url').text
            jira_id = root.find('id').text
            pwd = root.find('passwd').text
            self.jira = JIRA(server=url, basic_auth=(jira_id, pwd))
        except:
            print("login failed")
            if need_update_to_ui is True:
                main_ui.setNeedLoginState(True)
            return
        else:
            ## login success
            print("jira login success")
            self.url = url
            if need_update_to_ui is True:
                main_ui.jira_tracker = self.jira
            users = self.jira.search_users(jira_id)
            if len(users)==1:   ## found user
                self.jira_id = jira_id
                self.pwd = pwd
                if need_update_to_ui is True:
                    main_ui.login_user = users[0]
                    main_ui.lblUserName.setText(users[0].displayName)
                    main_ui.setNeedLoginState(False)
            else:
                if need_update_to_ui is True:
                    # 가능한 상황은 아니라고 생각되지만 예외처리는 코딩해두도록 한다
                    main_ui.lblUserName.setText('')
                    main_ui.login_user = None
                    main_ui.setNeedLoginState(True)
                return
        return

    # text widget의  id와 passwd를 이용한 login
    def login(self, jira_id, pwd, isSaveAccount):
        self.jira_id = jira_id
        self.pwd = pwd
        try:
            self.jira = JIRA(server=self.url, basic_auth=(jira_id, pwd))
        except:
            return "failed"
        else:
            ## save session of login info to local file
            if isSaveAccount:
                self.saveSession()
            users = self.jira.search_users(jira_id)
            if len(users)==1:   ## found user
                return users[0]
            return None

    def concateModelNameForSummary(self, model_data):
        return (self.issue_model_template['summary']
                +"["+model_data[self.settings.col_mainsoc+1]+"]"
                +"["+model_data[self.settings.col_region]+"] "
                + model_data[self.settings.col_model_name])

    def getFieldsForModelIssue(self, dev_version, model_data):
        tracker = self.jira
        new_issue = self.issue_model_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data)
        # new_issue['labels']=["실물검증"]
        new_issue['description']= '''
        개발 Master Ver. : {ver}\n
        엑셀 행 번호: {row}\n
        Model Name : {model}\n
        UHD/FHD/HD : {panel_type}\n
        Main SoC : {main_soc}\n
        DV 시작 : {dv_start}\n
        DV 종료 : {dv_end}\n
        담당자 ===========\n
        SW : 이가영Y\n
        HW PL : {hwpl}\n
        기획 : {plan}
        '''.format(ver=dev_version, row=model_data[len(model_data)-1]
                    , model=model_data[self.settings.col_model_name]
                    , hwpl= model_data[self.settings.col_hw_pl]
                    , panel_type = model_data[self.settings.col_panel_type].upper()
                    , plan=model_data[self.settings.col_hw_pl+1]
                    , main_soc=model_data[self.settings.col_mainsoc]
                    , dv_start=model_data[self.settings.col_dv_start]
                    , dv_end=model_data[self.settings.col_dv_end])

        return new_issue

    def getFieldsForSpecCheckIssue(self, model_data, parent_issue):
        if parent_issue is None:
            # model issue (parent issue)가 생성 실패되었음
            return None

        tracker = self.jira
        new_issue = self.issue_spec_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data) \
                                + ' Spec. 확인 요청'
        model_name = model_data[self.settings.col_model_name]
        new_issue['description']= '''
        모델 : {color:red}'''+model_name+'{color}\n'

        new_issue['description']+= self.settings.spec_desc

        new_issue['issuetype'] = {'name' : 'Sub-task'}
        new_issue['parent'] = {'id' : parent_issue.key}
        return new_issue

    def getFieldsForTestIssue(self, model_data, parent_issue):
        if parent_issue is None:
            # model issue (parent issue)가 생성 실패되었음
            return None

        tracker = self.jira
        new_issue = self.issue_test_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data) \
                                + ' 실물 확인'
        model_name = model_data[self.settings.col_model_name]
        new_issue['description']= '''
        모델 : {color:red}'''+model_name+'{color}\n'

        new_issue['description']+= self.settings.spec_desc

        new_issue['issuetype'] = {'name' : 'Sub-task'}
        new_issue['parent'] = {'id' : parent_issue.key}
        return new_issue


    def inquiryModelIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_model+' AND summary~"' \
                                            +model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : " \
                    +len(result_list))
            return None
        return result_list[0]

    def inquiryTestIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_test \
                                            +' AND summary~"'+model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : "+len(result_list))
            return None
        return result_list[0]

    def inquirySpecConfirmIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_spec \
                                            +' AND summary~"'+model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : " \
                                            +len(result_list))
            return None
        return result_list[0]

    def resolveIssueForDroppedModel(self, ver, issue_key):
        tracker = self.jira
        try:
            issue = tracker.issue(issue_key)
            status_name = issue.fields.status.name
        except:
            return
        comment_body = '개발 Master '+ver+' 에서 본 모델 Drop되어 Resolve 합니다.'

        if  status_name != 'Resolved' and status_name != 'Closed':
            tracker.transition_issue(issue \
                                      , 'Resolve Issue' \
                                      , comment=comment_body)

    def createModelIssueAndSubTasks(self, dev_version, model):
        try:
            ## 1) create model issue
            print('start get fields of model issue')
            model_fields = self.getFieldsForModelIssue(dev_version, model)
            print('complete get fields of model issue')
            model_issue = self.jira.create_issue(fields=model_fields)
            print('complete create model issue')

            ## 2) create spec.확인 issue
            spec_fields = self.getFieldsForSpecCheckIssue(model, model_issue)
            spec_fields['labels'].append(model[self.settings.col_panel_type].lower())
            self.jira.create_issue(fields=spec_fields)

            ## 3) create 실물확인 issue
            test_fields = self.getFieldsForTestIssue(model, model_issue)
            self.jira.create_issue(fields=test_fields)
        except:
            print("failed to create model issues : " \
                    +model[self.settings.col_model_name])
            if model_issue is not None:
                model_issue.delete()
            return False
        else:
            return True










# issue = jira_usr.issue("ESTREAMER-127")
# project = jira_usr.project("ESTREAMER")
#
#
# rawdata = issue.raw
#
#
#
# print(rawdata)


# import re
# from jira import JIRA
#
# options = {'server': 'http://hlm.lge.com/qi/'}
# jira = JIRA(options)
#
# projects = jira.projects();
#
# print("projects type : "+type(projects))
#
# issue = jira.issue('ESTREAMER-127')
# print("issue type : "+type(issue))
