from jira.client import *

jira_server_url = "https://ybincho.atlassian.net/"
# HLM Dev. Tracker serevr url   : "hlm.lge.com/issue"
# HLM Q. Tracker server url     : "hlm.lge.com/qi"

project_id      = "PR1-1"       # Global SW 개발실 Project id : GSWDIM
account_id      = "ybin"        # jira login id
account_passwd  = "passwd"   # jira login password

# create instance as jira.client.JIRA class with given url, account
tracker = JIRA(server=jira_server_url, basic_auth=(account_id, account_passwd))

## 1. Get Issue with various method
## 1-1. with issue-key (ex. 'GSWDIM-XXXX')
issue = tracker.issue("PR1-1")
print(str(issue))

## 1-2. with jql (jql is jira-sql)
## ex1. 'project=GSWDIM and assignee=ybin.cho'
## ex2. 'filter in ('L17_global_UI_part')'
jql = "project=PR1 AND assignee=ybin"
issues = tracker.search_issues(jql)
len(issues) # 검색 결과 이슈 개수, 첫번째 이슈 : issues[0], 두번째:issue[1], ...
issue = issues[0]   # 첫번째 이슈 가져오기

## 2. issue 의 fields 정보 가져오기
## 2-1. raw data를 통한 fields 정보 가져오기
issue.key       # issue key 값 (ex. GSWIDM-XXXX)
issue.raw       # issue 내 모든 정보 dictionary 객체
fields = issue.raw['fields']    ## 모든 field들에 대한 dictionary 객체
fields['summary']               ## get issue summary [str]
fields['description']           ## get issue description [str]
assignee = fields['assignee']   ## get assignee [dict]
reporter = fields['reporter']   ## get reporter [dict]
assignee['name']                ## assignee name [str]
assignee['emailAddress']        ## e-mail address [str] ex. 'ybin.cho@lge.com'

# label
labels = fields['labels']       ## get issue labels [list]
labels[0]                       ## first label [str]

# status
status = fields['status']       ## get status [dict]
status['name']                  ## status name [str] ex. Open, In-progress, ..
tracker.transitions(issue)      ## get list of status[dict]
tracker.transition_issue(issue, 'Resolved') ## status의 string
tracker.transition_issue(issue, 10)         ## status의 id값

## 2-2. fields 멤버를 통해 가져오기
fs = issue.fields                   ## type : jira.resoucrs.PropertyHolder
dir(issue.fields)                   ## fields 멤버 목록 확인

fs.labels               ## labels 가져오기
fs.status               ## status
fs.assignee
fs.summary
fs.description
fs.comment

## issue의 field 변경 (update)
description = fields['description']           ## get issue description [str]
issue.update(fields={'description':'hahaha'})  ## change description : 'hahaha'
issue.update(fields={'description':description+'\n추가된 내용'})
issue.update(fields={'summary':'바뀐 이슈 제목'}) ## change summary
issue.add_field_value('labels', '근태')

# watcher add/get
watchers = tracker.watchers(issue)      ## get watchers of issue given [Watchers]
users_of_watchers = watchers.watchers   ## list of jira.resources.Users
user_1 = users_of_watchers[0]           ## get first watcher
user_1.key                              ## jira id
user_1.name                             ## jira display name
user_1.emailAddress                     ## email address of first watcher
tracker.add_watcher(issue, 'ybin.cho')  ## issue의 watcher에 ybin.cho 계정 추가

# attachment
files = fields['attachment']        ## get attachment [list] file1, file2, ...
file_1 = fields['attachment'][0]    ## get first file_1 [dict]
file_1['content']                   ## file url [str]
tracker.add_attachment(issue, file_name)

# comments
tracker.add_comment(issue, 'comment blurblur')  ## issue에 comment 추가
issue.fields.comment.comments[0].body   # get first comment
