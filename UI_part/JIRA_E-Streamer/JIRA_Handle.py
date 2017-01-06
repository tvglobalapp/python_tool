from jira.client import JIRA
import jira.config
from Dev_Master import Dev_Meta
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree

event = 'dev'     ## dev / release
dev_local_path = 'd://project//python//JIRA_Estreamer//'

def GetPath():
    global event, dev_local_path
    if event == 'dev':
        return dev_local_path
    else:
        return ''


jira_usr = jira.config.get_jira('hlm')

# HLM Dev. Tracker
hlm_dev_url = "http://hlm.lge.com/issue"
# HLM Q Tracker
hlm_q_url = "http://hlm.lge.com/qi"

# Project Id
project_id = 'ESTREAMER'

# jira issue query
jql_default = 'project='+project_id+' and '
jql_model_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물검증)'
jql_test_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_실물확인)'
jql_spec_issue = jql_default+'filter in (L17_ESTREAMER_D_VA_SPEC확인)'

# E-Streamer S/W 담당자 : JIRA reporter & default assignee
estreamer_sw = 'gayoung.lee'

# Jira Login을 위한 session file name
session_file_name = 'jira_session.xml'

# Jira 에서 issue 조회 시 maxResult개수를 지정해야 한다
# @ jira_tracker.search_issues [default:50]
maxResult = 200

# Fileter : 실물검증TEST -> 실물검증
# filter name : L17_ESTREAMER_D_VA_XXXX_TEST -> L17_ESTREAMER_D_VA_XXXX

class JIRA_Handler:
    main_issue_watchers = ['ybin.cho', 'gayoung.lee']
    def __init__(self, tracker):
        # jira server url
        global hlm_dev_url, hlm_q_url

        global project_id
        global jql_model_issue, jql_test_issue, jql_spec_issue
        global estreamer_sw
        global session_file_name
        global GetPath
        global maxResult

        self.maxResultJira = maxResult

        self.jira_id=''
        self.pwd=''

        #exception : default DEV tracker
        if tracker.lower()=="q":
            self.url = hlm_q_url
        elif tracker.lower()=="dev":
            self.url = hlm_dev_url
        else:   #default dev tracker
            self.url = hlm_dev_url

        self.issue_template = {'project':{"key":project_id}
                               ,"assignee":{"name":estreamer_sw}
                               ,'summary': '[Estreamer검증]'
                               ,'description':'Test 중'
                               ,'issuetype':{'name':'Request'}}
        self.jira=None
        self.jira_project_id = project_id
        self.jql_model = jql_model_issue
        self.jql_test = jql_test_issue
        self.jql_spec = jql_spec_issue

        self.session_file = GetPath()+session_file_name

        print("JIRA handler init.")

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
    def sessionLogin(self, main_ui):
        try:
            tree = ET.parse(self.session_file)
        except FileNotFoundError:
            print(session_file)
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
            main_ui.setNeedLoginState(True)
            return
        else:
            ## login success
            self.url = url
            main_ui.jira_tracker = self.jira
            users = self.jira.search_users(jira_id)
            if len(users)==1:   ## found user
                main_ui.login_user = users[0]
                main_ui.lblUserName.setText(users[0].displayName)
                self.jira_id = jira_id
                self.pwd = pwd
                main_ui.setNeedLoginState(False)
            else:
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
        return (self.issue_template['summary']
                +"["+model_data[Dev_Meta.idxRegion]+"] "
                + model_data[Dev_Meta.idxModelName])

    def getFieldsForModelIssue(self, dev_version, model_data):
        tracker = self.jira
        new_issue = self.issue_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data)
        #new_issue['labels'].append(dev_version)
        new_issue['labels']=["실물검증"]
        new_issue['description']= '''
        개발 Master Ver. : {ver}\n
        엑셀 행 번호: {row}\n
        Model Name : {model}\n
        DV 시작 : {dv_start}\n
        DV 종료 : {dv_end}\n
        담당자 ===========\n
        SW : 이가영Y\n
        HW PL : {hwpl}\n
        기획 : {plan}
        '''.format(ver=dev_version, row=model_data[len(model_data)-1], model=model_data[Dev_Meta.idxModelName], \
                   hwpl= model_data[Dev_Meta.idxHwPL], plan=model_data[Dev_Meta.idxHwPL+1], \
                   dv_start=model_data[Dev_Meta.idxDvStart], dv_end=model_data[Dev_Meta.idxDvEnd])
        return new_issue

    def getFieldsForSpecCheckIssue(self, model_data, parent_issue):
        if parent_issue is None:
            # model issue (parent issue)가 생성 실패되었음
            return None

        tracker = self.jira
        new_issue = self.issue_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data)+ ' Spec. 확인 요청'
        model_name = model_data[Dev_Meta.idxModelName]
        new_issue['labels']=["실물검증"]
        new_issue['description']= '''
        모델 : {color:red}'''+model_name+'{color}\n'

        new_issue['description']+= '''
        상기 모델에 대해 E-Streamer 적용되어야 할 Spec. 모델명 확인 요청 드립니다.\n
        Spec. 모델명이란 E-Streamer Spec. Sheet 상에 지역 탭에 정의된 'Model Name' 항목을 의미합니다.\n
        모델에 대한 정보는 본 이슈의 상위 이슈를 참조하세요.\n
        E-Streamer Spec. Sheet 기준 적용 모델명을 comment에 기입 후 Resolve 부탁 드립니다.'''

        new_issue['issuetype'] = {'name' : 'Sub-task'}
        new_issue['parent'] = {'id' : parent_issue.key}
        return new_issue

    def getFieldsForTestIssue(self, model_data, parent_issue):
        if parent_issue is None:
            # model issue (parent issue)가 생성 실패되었음
            return None

        tracker = self.jira
        new_issue = self.issue_template.copy()
        new_issue['summary'] = self.concateModelNameForSummary(model_data)+ ' 실물 확인'
        model_name = model_data[Dev_Meta.idxModelName]
        new_issue['description']= '''
        모델 : {color:red}'''+model_name+'{color}\n'

        new_issue['description']+= '''
        유첨 E-Streamer 적용 결과 이미지 참조하시어 실물 점검 부탁 드립니다.\n
        모델 정보는 상위 이슈 참조하세요.\n
        Comment 확인하시어 지역(Area) 내 전 국가 실물 확인 후 Resolve 부탁 드립니다.\n

        PPM 포맷 이미지 뷰어는 알씨 등이 지원하고 있으며 아래 사이트에서도 쉽게 다운로드 가능합니다.\n
        : http://free-ppm-viewer.en.informer.com/\n
        : 캡쳐 파일 바로 열기에 문제가 있을 경우 이미지 파일을 로컬에 저장 후 열어주세요.\n'''

        new_issue['issuetype'] = {'name' : 'Sub-task'}
        new_issue['parent'] = {'id' : parent_issue.key}
        return new_issue


    def inquiryModelIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_model+' AND summary~"'+model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : "+len(result_list))
            return None
        return result_list[0]

    def inquiryTestIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_test+' AND summary~"'+model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : "+len(result_list))
            return None
        return result_list[0]

    def inquirySpecConfirmIssue(self, model_name):
        tracker = self.jira
        result_list = tracker.search_issues(self.jql_spec+' AND summary~"'+model_name+'"')
        if len(result_list)!=1:
            print("search failed !. number of result length : "+len(result_list))
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
            tracker.transition_issue(issue, 'Resolve Issue', comment=comment_body)

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
            self.jira.create_issue(fields=spec_fields)

            ## 3) create 실물확인 issue
            test_fields = self.getFieldsForTestIssue(model, model_issue)
            self.jira.create_issue(fields=test_fields)
        except:
            print("failed to create model issues : "+model[Dev_Meta.idxModelName])
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
