from  jira_connect import *

issue_template = {'project':{"key":"SSP"}
                  ,"assignee":{"name":"ybin.cho"}
                  ,"labels":["실물검증"]
                  ,'summary': '[Estreamer검증]'
                  ,'description':'Test 중'
                  ,'issuetype':{'name':'Request'}}

for i in range(0,5):
    new_issue = issue_template.copy()
    new_issue['summary'] += str(i)
    issue = tracker.create_issue(fields=new_issue)

# new_issue['summary'] = new_issue['summary']+"["+model_data[Dev_Meta.idxRegion]+"] "+ model_data[Dev_Meta.idxModelName]
# new_issue['labels'].append(self.dev_master.version)
# new_issue['description']= '''
# 개발 Master Ver. : {ver}\n
# 엑셀 행 번호: {row}\n
# Model Name : {model}\n
# DV 시작 : {dv_start}\n
# DV 종료 : {dv_end}\n
# 담당자 ===========\n
# SW : 조용빈\n
# HW PL : {hwpl}\n
# 기획 : {plan}
# '''.format(ver=dev_version, row=model_data[len(model_data)-1], model=model_data[Dev_Meta.idxModelName], \
#            hwpl= model_data[Dev_Meta.idxHwPL], plan=model_data[Dev_Meta.idxHwPL+1], \
#            dv_start=model_data[Dev_Meta.idxDvStart], dv_end=model_data[Dev_Meta.idxDvEnd])
