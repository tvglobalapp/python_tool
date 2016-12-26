from jira.client import JIRA
import jira.config

jira_usr = jira.config.get_jira('hlm')

#HLM Dev. Tracker
hlm_dev_url ="http://hlm.lge.com/issue"
#HLM Q Tracker
hlm_q_url ="http://hlm.lge.com/qi"

class JIRA_Handler:
    main_issue_watchers = [{'name':'seungyong.jun'}, {'name':'gayoung.lee'}]
    def __init__(self, tracker):
        global hlm_dev_url
        global hlm_q_url
        self.id=''
        self.pwd=''

        #exception : default DEV tracker
        if tracker.lower()=="q":
            self.url = hlm_q_url
        elif tracker.lower()=="dev":
            self.url = hlm_dev_url
        else:   #default dev tracker
            self.url = hlm_dev_url

        self.issue_template = {'project':{"key":"ESTREAMER"},"assignee":{"name":"ybin.cho"},"labels":["실물검증"],'summary': '[Estreamer검증]','description':'Test 중', 'issuetype':{'name':'Request'}}
        self.jira_handle=''
        print("JIRA handler init")

    def login(self, jira_id, pwd):
        try:
            self.jira = JIRA(server=self.url, basic_auth=(jira_id, pwd))
        except:
            return "failed"
        else:
            return "success"












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
