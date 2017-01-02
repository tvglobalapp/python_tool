from jira.client import *
import account

jira_server_url = "http://hlm.lge.com/issue"
# HLM Q. Tracker server url     : "http://hlm.lge.com/qi"

project_id      = "SSP"             # Global SW 개발실 Project id : GSWDIM
account_id      = "ybin.cho"        # jira login id
account_passwd  = account.passwd    # jira login password

# create instance as jira.client.JIRA class with given url, account
try:
    tracker = JIRA(server=jira_server_url, basic_auth=(account_id, account_passwd))
except:
    print("connect / login failed")
else:
    print("connect / login success")
