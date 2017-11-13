import shutil
import os, glob
import re
import copy
import xlrd
from PyQt5.QtWidgets import QMessageBox
import os, glob
import hashlib
import json
from xml.etree import ElementTree
import codecs
from define import *

ipkName = []

######################################################
######### 서버 Ordering DB 추가 부분
######### @param
######### 1. resPath : 서버 Ordering 문서 path
#########
######################################################
def add_DB(resPath):
    path = resPath
    retList = ['OK','* DB 저장 성공! *']

    #path를 기준으로 File path와 file Name을 구분해 내는 작업
    fileBuffer = path.split("/")
    fileName = fileBuffer[len(fileBuffer)-1]

    #안쓰면 삭제!!
    # filePath = ''
    # for value in fileBuffer:
    #     if value != fileName:
    #         filePath = filePath + value + "\\"
    # print(filePath)

    platformBuffer = fileName.split("_")
    platformCode = platformBuffer[0]

    key_dateBuffer = fileName.split("_")
    key_date = key_dateBuffer[DATE_INDEX]

    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)

    data = {}
    orderingDic = {}
    existDB = False

    with open("resources\country_code.txt", "r") as f:
        for value in f.readlines():
            value = value.replace('\n','')
            value = value.split('\t')
            data[value[0].upper()] = value[1]

    #resources폴더 search하여 db.json 있는지 확인
    for files in os.listdir("resources\\"):
        if files.find(platformCode+'db.json') != -1:
            existDB = True

    dbData = {}

    # resources폴더 내부에 db.json 파일이 존재할 경우
    # 기존에 DB 생성을 이미 한번 이상 한 경우
    jsonPath = 'resources\\'+platformCode+'db.json'
    if existDB == True:
        with codecs.open(jsonPath, "r",encoding="utf8") as jsonFile:
            dbData = json.load(jsonFile)

        if key_date in dbData.keys():
            retList = ['NG','* DATA가 DB에 이미 있습니다. *']
            return retList
        else:
            cnt = 0
            dbData[key_date] = {}
            for sheet in workbook.sheets():
                nrows = sheet.nrows
                for row_num in range(1,nrows):
                    countryName = sheet.row_values(row_num)[EXCEL_COUNTRY_NAME]
                    if(data[countryName.upper()] not in dbData[key_date].keys()):
                        if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                            dbData[key_date][data[countryName.upper()]] = []
                            #App Ordering 순서에 맞춰 sorting 해주기 위해 "ordering순서_AppID" 형식으로 만들어 준다.
                            dbData[key_date][data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])
                    else:
                        if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                            dbData[key_date][data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])


                cnt += 1;

            #"ordering순서_AppID" 형식으로 만들어 준 data를 sorting한다.
            #sorting 이후 ordering순서를 삭제하고 AppID만 data에 다시 넣어준다.
            for value in dbData[key_date].keys():
                dbData[key_date][value].sort()
                originList = []
                for appID in dbData[key_date][value]:
                    origin = appID.split('_')
                    originList.append(origin[1])
                dbData[key_date][value] = originList

            with codecs.open(jsonPath,'w',encoding="utf8") as jsonFile:
                jsonFile.write(json.dumps(dbData,indent=4, sort_keys=True,ensure_ascii=False))

    # resources폴더 내부에 db.json 파일이 없을 경우
    # DB 생성을 한번도 안한 경우
    else:
        cnt = 0
        dbData[key_date] = {}
        for sheet in workbook.sheets():
            nrows = sheet.nrows
            for row_num in range(1,nrows):
                countryName = sheet.row_values(row_num)[EXCEL_COUNTRY_NAME]
                if(data[countryName.upper()] not in dbData[key_date].keys()):
                    if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                        dbData[key_date][data[countryName.upper()]] = []
                        dbData[key_date][data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])
                else:
                    if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                        dbData[key_date][data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])
            cnt += 1;

        for value in dbData[key_date].keys():
            dbData[key_date][value].sort()
            originList = []
            for appID in dbData[key_date][value]:
                origin = appID.split('_')
                originList.append(origin[1])
            dbData[key_date][value] = originList

        with codecs.open(jsonPath,'w',encoding="utf8") as jsonFile:
            jsonFile.write(json.dumps(dbData,indent=4, sort_keys=True,ensure_ascii=False))
    return retList
######################################################
######### 필요 directory/default resource 추가 부분
######### @param
######### 1. resPath : cp stub git path
######### 2. dir_name : 추가할 directory name
######################################################
def add_directory(resPath, dir_name):
    #디렉토리 삭제 부분
    localPath = resPath
    localPath += "/"+dir_name

    serverPath = 'resources\default_resource'

    shutil.copytree(serverPath,localPath)

    jsonPath = localPath + '\\appinfo.json'
    with codecs.open(jsonPath, "r",encoding="utf8") as jsonFile:
        data = json.load(jsonFile)

    data['id'] = dir_name

    with codecs.open(jsonPath,'w',encoding="utf8") as jsonFile:
        jsonFile.write(json.dumps(data,indent=4, sort_keys=True,ensure_ascii=False))

######################################################
######### 불필요 directory 삭제 부분
######### @param
######### 1. resPath : cp stub git path
######### 2. dir_name : 삭제할 directory name
######################################################
def remove_directory(resPath, dir_name):
    #디렉토리 삭제 부분
    path = resPath
    path += "/"+dir_name

    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        shutil.remove(path)
    except OSError as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setText(e)
        retval = msg.exec_()

###############################################################
######### validation check 중 핵심 check Item이 있는지 확인하는 부분
######### @param
######### 1. excelPath : 검사할 excel file의 path
######### 2. excelFileName : 검사할 excel file의 이름
###############################################################
def critical_item_check(excelPath, excelFileName):
    path = excelPath
    path += "/"+excelFileName
    retList = ['OK','* Critical Item Value OK!!! *']
    critical_val = ['Country Name','Launcher','App Name','str app id','TV 노출가능여부','Ordering Use Flag']
    workbook = xlrd.open_workbook(path)
    cnt = 0
    for sheet in workbook.sheets():
        for value in critical_val:
            try:
                sheet.row_values(0).index(value)
            except ValueError:
                retList[0] = "Error"
                retList[1] = "* Critical Item Value Error!!! *"
                retList.append("- Error Sheet name : "+workbook.sheet_names()[cnt])
                retList.append("- Error item name : "+value)
        cnt += 1;
    return retList

###############################################################
######### validation check 중 비어있는 Cell이 있는지 확인하는 부분
######### @param
######### 1. excelPath : 검사할 excel file의 path
######### 2. excelFileName : 검사할 excel file의 이름
###############################################################
def blank_cell_check(excelPath, excelFileName):
    path = excelPath
    path += "/"+excelFileName
    retList = ['OK','* Blank Cell check OK!!! *']
    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)

    cnt = 0
    for sheet in workbook.sheets():
        row_val = []
        nrows = sheet.nrows
        for row_num in range(nrows):
            row_val.append(sheet.row_values(row_num))
            for value in range(len(row_val[row_num])):
                if(row_val[row_num][value] == ''):
                    retList[0] = "Error"
                    retList[1] = "* Blank Cell Error!!! *"
                    retList.append("---------------------------")
                    retList.append("- Error Sheet name : "+workbook.sheet_names()[cnt])
                    retList.append("- Error Country Name : "+row_val[row_num][EXCEL_COUNTRY_NAME])
                    retList.append("- Error row number : "+str(row_num+1))
                    retList.append("- Error colm number : "+str(chr(65+value)))
        cnt += 1;

    return retList

###############################################################
######### validation check 중 중복되는(Launcher 열) Cell이 있는지 확인하는 부분
######### @param
######### 1. excelPath : 검사할 excel file의 path
######### 2. excelFileName : 검사할 excel file의 이름
###############################################################
def duplication_cell_check(excelPath, excelFileName):
    path = excelPath
    path += "/"+excelFileName
    retList = ['OK','* Duplication Cell check OK!!! *']
    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)

    cnt = 0
    for sheet in workbook.sheets():
        countryList = []
        launcherList = []
        nrows = sheet.nrows
        for row_num in range(1,nrows):
            if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-'):
                launcherValue = str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))
            else:
                continue

            if(sheet.row_values(row_num)[EXCEL_COUNTRY_NAME] in countryList):
                if(launcherValue in launcherList):
                    retList[0] = "Error"
                    retList[1] = "* Duplication Cell Error!!! *"
                    retList.append("---------------------------")
                    retList.append("- Error Sheet name : "+workbook.sheet_names()[cnt])
                    retList.append("- Error Country Name : "+sheet.row_values(row_num)[EXCEL_COUNTRY_NAME])
                    retList.append("- Error row number : "+str(row_num+1))
                else:
                    if(launcherValue != '-'):
                        launcherList.append(launcherValue)
            else:
                launcherList = []
                if(launcherValue != '-'):
                    countryList.append(sheet.row_values(row_num)[EXCEL_COUNTRY_NAME])
                    launcherList.append(launcherValue)

        cnt += 1;
    return retList

###############################################################
######### validation check 중 local에 해당 country code가 있는지
######### 확인하는 부분
######### @param
######### 1. platform_dic : platform 구분 가능한 dictionary
######### 2. excelPath : 검사할 excel file의 path
######### 3. excelFileName : 검사할 excel file의 이름
###############################################################
def country_code_check(orderingPath, platform_dic, excelPath, excelFileName):
    path = excelPath
    path += "/"+excelFileName
    retList = ['OK','* Country Code check OK!!! *']

    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)

    data = {}
    countryCodeDic = {}
    with open("resources\country_code.txt", "r") as f:
        for value in f.readlines():
            value = value.replace('\n','')
            value = value.split('\t')
            data[value[0].upper()] = value[1]

    cnt = 0
    for sheet in workbook.sheets():
        countryCodeDic[workbook.sheet_names()[cnt]] = []
        nrows = sheet.nrows

        for row_num in range(1,nrows):
            countryName = sheet.row_values(row_num)[EXCEL_COUNTRY_NAME]
            if(data[countryName.upper()] not in countryCodeDic[workbook.sheet_names()[cnt]]):
                countryCodeDic[workbook.sheet_names()[cnt]].append(data[countryName.upper()])
        cnt += 1;

    dirName = ''
    for value in platform_dic.keys():
        if excelFileName.find(value) != -1:
            dirName = platform_dic[value]

    countryCodePath = orderingPath+'\\'+dirName +'\\launchpoints'
    try:
        for value in countryCodeDic.keys():
            for code in countryCodeDic[value]:
                if code not in os.listdir(countryCodePath):
                    retList[0] = "Error"
                    retList[1] = "* Country Code Check Error!!! *"
                    retList.append("---------------------------")
                    retList.append("- Error Sheet name : "+value)
                    for name in data.keys():
                        if data[name] == code:
                            retList.append("- Error Country Name : "+name)
                            break
                    retList.append("- Error Country Code : "+code)
    except:
        retList[0] = 'Warning'
        retList[1] = "* Country Code Check Error!!! *"
        retList.append("---------------------------")
        retList.append("Pleas Check <starfish-customization-consumer> Git branch!!!")
        retList.append("There is no "+dirName+" directory!!!")
    return retList

###############################################################
######### validation check 완료 후 변경점 적용 부분
######### @param
######### 1. platform_dic : platform 구분 가능한 dictionary
######### 2. excelPath : 검사할 excel file의 path
######### 3. excelFileName : 검사할 excel file의 이름
######### 4. orderingPath : excel과 비교할 ordering Git path
###############################################################
def ordering_apply(platform_dic, excelPath, excelFileName, orderingPath):
    retDic = {}
    retValue = None
    path = excelPath
    path += "/"+excelFileName

    workbook = xlrd.open_workbook(path)
    first_sheet = workbook.sheet_by_index(0)

    data = {}
    orderingDic = {}
    with open("resources\country_code.txt", "r") as f:
        for value in f.readlines():
            value = value.replace('\n','')
            value = value.split('\t')
            data[value[0].upper()] = value[1]

    cnt = 0
    for sheet in workbook.sheets():
        nrows = sheet.nrows
        for row_num in range(1,nrows):
            countryName = sheet.row_values(row_num)[EXCEL_COUNTRY_NAME]
            if(data[countryName.upper()] not in orderingDic.keys()):
                if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                    orderingDic[data[countryName.upper()]] = []
                    orderingDic[data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])
            else:
                if(sheet.row_values(row_num)[EXCEL_LAUNCHER] != '-' and sheet.row_values(row_num)[EXCEL_APP_DISPLAY] != '비노출(TV에 보이지 않음)'):
                    orderingDic[data[countryName.upper()]].append(str(int(sheet.row_values(row_num)[EXCEL_LAUNCHER]))+'_'+sheet.row_values(row_num)[EXCEL_APP_ID])

            if(data[countryName.upper()] in orderingDic.keys()):
                orderingDic[data[countryName.upper()]].sort()

        cnt += 1;

    dirName = ''
    for value in platform_dic.keys():
        if excelFileName.find(value) != -1:
            dirName = platform_dic[value]

    countryCodePath = orderingPath+'\\'+dirName +'\\launchpoints'

    errFlag = False
    for value in orderingDic.keys():
        local_f = open(countryCodePath+'\\'+value+'\\applist.json','r',encoding="utf8")
        local_appinfo_json = json.loads(local_f.read())
        local_f.close()
        originList = []
        for appid in orderingDic[value]:
            origin = appid.split('_')
            originList.append(origin[1])

        if len(local_appinfo_json['applications_dosci']) == len(orderingDic[value]):
            num = len(local_appinfo_json["applications_dosci"])
            for index in range(num):
                if local_appinfo_json['applications_dosci'][index] != originList[index]:
                    errFlag = True
                    break
            else:
                errFlag = False
        else:
            errFlag = True

        if(errFlag == True):
            country_name = None
            for country in data.keys():
                if(data[country] == value):
                    country_name = country
            retDic[value] = [country_name,local_appinfo_json["applications_dosci"],originList]
            retValue = ['Error',retDic]
    if retValue == None:
        retValue = ['Same']

    return retValue
###############################################################
######### 서버 리소스의 압축을 푸는 부분
######### @param
######### 1. zipPath : 7-zip install되어 있는 경로
######### 2. serverResPath : 압축된 서버 리소스들이 있는 경로
###############################################################
def decompression_server_resource(zipPath, serverResPath):
    folderPath = serverResPath
    ipkList = []

    for files in os.listdir(folderPath):
        if files.find('.ipk') != -1:
            ipkList.append(files)

    currPath = os.getcwd()
    os.chdir(zipPath)
    for ipk in ipkList:
        # try except 코드 추가하여 return하도록 필요... 압축 풀기 실패 시 알람 필요
        temp = ipk.split('.')
        ipkName.append(temp[0])
        for dir in os.listdir(folderPath):
            if dir == temp[0]:
                break;
        else:
            os.system('7z x ' + folderPath + '\\'+ipk + ' -o'+folderPath+'\\'+temp[0])
            os.system('7z x ' + folderPath + '\\'+temp[0] + '\\data.tar.gz' + ' -o'+folderPath+'\\'+temp[0]+'\\data.tar')
            os.system('7z x ' + folderPath + '\\'+temp[0] + '\\data.tar\\data.tar' + ' -o'+folderPath+'\\'+temp[0]+'\\data.tar\\data')

    os.chdir(currPath)

###############################################################
######### 서버 리소스들을 특정 folder로 copy하는 부분 __serverResource 폴더로 copy
######### @param
######### 1. serverResPath : 압축된 서버 리소스들이 있는 경로
###############################################################
def resource_copy(serverResPath):
    dstDir = serverResPath + '\\__serverResource'
    try:
        os.mkdir(dstDir)
    except:
        print('__serverResource is already exist!')

    for value in ipkName:
        path = serverResPath + '\\' + value + '\\data.tar\\data\\usr\\palm\\applications\\'
        try:
            shutil.copytree(path+'\\'+os.listdir(path)[0], dstDir+'\\'+os.listdir(path)[0])
        except:
            print('Already Exist App resource : '+os.listdir(path)[0])

###############################################################
######### Icon Color값이 존재하는지 확인하는 함수
######### @param
######### 1. local_appinfo_json : local json file data
######### 2. server_appinfo_json : server json file data
###############################################################
def check_icon_color_exist(local_appinfo_json, server_appinfo_json):
    returnValue = 0
    local_flag = True
    server_flag = True

    if 'iconColor' in local_appinfo_json.keys():
        if local_appinfo_json['iconColor'] == '':
            local_flag = False
        else:
            local_flag = True
    else:
        local_flag = False

    if 'iconColor' in server_appinfo_json.keys():
        if server_appinfo_json['iconColor'] == '':
            local_flag = False
        else:
            local_flag = True
    else:
        server_flag = False

    if ((local_flag == True) and (server_flag == True)):
        return 'ALL_EXIST'
    elif ((local_flag == True) and (server_flag is False)):
        return 'LOCAL_EXIST'
    elif ((local_flag == False) and (server_flag == True)):
        return 'SERVER_EXIST'
    else:
        return 'NOT_EXIST'

###############################################################
######### app resource간 차이점을 검사하는 부분
######### @param
######### 1. resPath : 로컬 resource path
######### 2. serverResPath : server resource path
###############################################################
allList = []
differList = []
matchList = []
def deffer_resource_error_check(resPath, serverResPath, localizationPath):
    serverAppIDList = []
    localAppIDList = []

    smallIcon_localPathDic = {}      #iconViewer로 전달하기 위한 local path dictionary 80x80
    smallIcon_serverPathDic = {}     #iconViewer로 전달하기 위한 server path dictionary 80x80
    largeIcon_localPathDic = {}      #iconViewer로 전달하기 위한 local path dictionary 130x130
    largeIcon_serverPathDic = {}     #iconViewer로 전달하기 위한 server path dictionary 130x130

    resource_err_list = []  #전체 error 정보를 담는 list  S_icon/L_icon/title/bgColor

    title_bgColor_err_dic = {}
    title_bgColor_err_list = [None,None,None,None,None]

    cnt = 0

    localDir = filter(os.path.isdir, glob.glob(resPath+'\\*'))

    for value in localDir:
        localAppIDList.append(os.path.basename(value))
    for dir in os.listdir(serverResPath + '\\__serverResource'):
        serverAppIDList.append(dir)

    for localAppID in localAppIDList:
        for serverAppID in serverAppIDList:
            if (serverAppID == localAppID):
                allList.append(serverAppID)
                # for num in range(len(title_bgColor_err_list)):
                #     title_bgColor_err_list.pop()
                title_bgColor_err_list = [None,None,None,None,None]
                cnt = cnt +1
                # print(serverAppID)
                #title / icon color 비교
                local_f = open(resPath+'\\'+serverAppID+'\\appinfo.json','r',encoding="utf8")
                local_appinfo_json = json.loads(local_f.read())
                local_f.close()

                server_f = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\appinfo.json','r',encoding="utf8")
                server_appinfo_json = json.loads(server_f.read())
                server_f.close()

                #icon color 비교
                iconColorExist = check_icon_color_exist(local_appinfo_json, server_appinfo_json)
                iconColorError = True

                if(iconColorExist == 'ALL_EXIST'):
                    localIconColor = local_appinfo_json['iconColor'].upper()
                    serverIconColor = server_appinfo_json['iconColor'].upper()

                    if(localIconColor != serverIconColor):
                        title_bgColor_err_list[0] = local_appinfo_json['iconColor']
                        title_bgColor_err_list[1] = server_appinfo_json['iconColor']
                    else:
                        iconColorError = False
                elif (iconColorExist == 'LOCAL_EXIST'):
                    title_bgColor_err_list[0] = local_appinfo_json['iconColor']
                    title_bgColor_err_list[1] = 'X'
                elif (iconColorExist == 'SERVER_EXIST'):
                    title_bgColor_err_list[0] = 'X'
                    title_bgColor_err_list[1] = server_appinfo_json['iconColor']
                else:
                    iconColorError = False
                    print('There is no iconColor.')

                if((iconColorExist != 'NOT_EXIST') and (iconColorError == True)):
                    if(title_bgColor_err_list[4] == None):
                        title_bgColor_err_list[4] = '<BackGround Color>'
                    else:
                        title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<BackGround Color>'

                #Title 비교
                if(local_appinfo_json['title'] != server_appinfo_json['title']):
                    #추가 필요 resource여서 default resource를 반영해 둔 경우
                    #title이 ''이기 때문에 바로 서버 title로 변경한다.
                    if(local_appinfo_json['title'] == ''):
                        title_bgColor_err_list[2] = local_appinfo_json['title']
                        title_bgColor_err_list[3] = server_appinfo_json['title']

                        if(title_bgColor_err_list[4] == None):
                            title_bgColor_err_list[4] = '<Title>'
                        else:
                            title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Title>'
                    else:
                        serverResAppPath = serverResPath+'\\__serverResource\\'+serverAppID
                        if('resources' in os.listdir(serverResAppPath)):
                            if('en' in os.listdir(serverResAppPath+'\\resources')):
                                try:
                                    server_en_f = open(serverResAppPath+'\\resources\\en\\appinfo.json','r',encoding="utf8")
                                except:
                                    server_en_f = open(serverResAppPath+'\\resources\\en\\GB\\appinfo.json','r',encoding="utf8")
                                server_en_json = json.loads(server_en_f.read())
                                server_en_f.close()
                                if(local_appinfo_json['title'] != server_en_json['title']):
                                    title_bgColor_err_list[2] = local_appinfo_json['title']
                                    title_bgColor_err_list[3] = server_en_json['title']

                                    if(title_bgColor_err_list[4] == None):
                                        title_bgColor_err_list[4] = '<Title>'
                                    else:
                                        title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Title>'
                                else:
                                    # localization git cpstub-apps data file parsing 이후
                                    # 다국어 번역 여부 확인 및 추가 변수에 내용 저장 필요!!
                                    localizationExcel = localizationPath + '\\cpstub-apps.xliff'
                                    localization_flag = localization_check(localizationExcel,local_appinfo_json['title'],server_appinfo_json['title'],serverAppID)

                                    if(localization_flag == False):
                                        title_bgColor_err_list[2] = local_appinfo_json['title'] + ' \n다국어 확인 필요'
                                        title_bgColor_err_list[3] = server_appinfo_json['title'] + ' \n다국어 확인 필요'

                                        if(title_bgColor_err_list[4] == None):
                                            title_bgColor_err_list[4] = '<Title>'
                                        else:
                                            title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Title>'
                            else:

                                title_bgColor_err_list[2] = local_appinfo_json['title']
                                title_bgColor_err_list[3] = server_appinfo_json['title']

                                if(title_bgColor_err_list[4] == None):
                                    title_bgColor_err_list[4] = '<Title>'
                                else:
                                    title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Title>'
                        else:

                            title_bgColor_err_list[2] = local_appinfo_json['title']
                            title_bgColor_err_list[3] = server_appinfo_json['title']

                            if(title_bgColor_err_list[4] == None):
                                title_bgColor_err_list[4] = '<Title>'
                            else:
                                title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Title>'

                if(title_bgColor_err_list[3] == None):
                    title_bgColor_err_list[3] = server_appinfo_json['title']
                #icon 비교
                local_image = open(resPath+'\\'+serverAppID+'\\icon.png','rb').read()
                localHash = hashlib.md5(local_image).hexdigest()

                local_large_image = open(resPath+'\\'+serverAppID+'\\largeIcon.png','rb').read()
                localLargeHash = hashlib.md5(local_large_image).hexdigest()

                for value in os.listdir(serverResPath+'\\__serverResource\\'+serverAppID):
                    iconSize = findIconSize(value)
                    if(iconSize == '80x80'):
                    # if(value.find('80x80') != -1 and value.find('130x130') == -1):
                        server_image = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value,'rb').read()
                        serverHash = hashlib.md5(server_image).hexdigest()
                        if(localHash != serverHash):
                            smallIcon_localPathDic[localAppID] = resPath+'\\'+localAppID+'\\icon.png'
                            smallIcon_serverPathDic[serverAppID] = serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value

                            if(title_bgColor_err_list[4] == None):
                                title_bgColor_err_list[4] = '<Small Icon>'
                            else:
                                title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Small Icon>'
                    if(iconSize == '130x130'):
                    # if(value.find('130x130') != -1 and value.find('80x80') == -1):
                        server_image = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value,'rb').read()
                        serverHash = hashlib.md5(server_image).hexdigest()
                        if (localLargeHash != serverHash):
                            largeIcon_localPathDic[localAppID] = resPath+'\\'+localAppID+'\\largeIcon.png'
                            largeIcon_serverPathDic[serverAppID] = serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value

                            if(title_bgColor_err_list[4] == None):
                                title_bgColor_err_list[4] = '<Large Icon>'
                            else:
                                title_bgColor_err_list[4] = title_bgColor_err_list[4]+'<Large Icon>'

                if (title_bgColor_err_list[4] != None):
                    title_bgColor_err_dic[serverAppID] = title_bgColor_err_list
                    differList.append(serverAppID)
                break

    print('check된 App Id 개수 : ' + str(cnt))
    iconList = [largeIcon_localPathDic,largeIcon_serverPathDic,smallIcon_localPathDic,smallIcon_serverPathDic]

    resource_err_list.append(iconList)
    resource_err_list.append(title_bgColor_err_dic)

    aaa = differList + matchList

    for value in allList:
        if(value not in aaa):
            print('no app ID : ' + value)

    return resource_err_list

def all_resource_error_check(resPath, serverResPath, localizationPath):
    serverAppIDList = []
    localAppIDList = []

    smallIcon_localPathDic = {}      #iconViewer로 전달하기 위한 local path dictionary 80x80
    smallIcon_serverPathDic = {}     #iconViewer로 전달하기 위한 server path dictionary 80x80
    largeIcon_localPathDic = {}      #iconViewer로 전달하기 위한 local path dictionary 130x130
    largeIcon_serverPathDic = {}     #iconViewer로 전달하기 위한 server path dictionary 130x130

    resource_err_list = []  #전체 error 정보를 담는 list  S_icon/L_icon/title/bgColor

    title_bgColor_err_dic = {}
    title_bgColor_err_list = [None,None,None,None,None]

    cnt = 0
    matchCount = 0
    localDir = filter(os.path.isdir, glob.glob(resPath+'\\*'))

    for value in localDir:
        localAppIDList.append(os.path.basename(value))
    for dir in os.listdir(serverResPath + '\\__serverResource'):
        serverAppIDList.append(dir)

    for localAppID in localAppIDList:
        for serverAppID in serverAppIDList:
            if (serverAppID == localAppID):
                smallFlag = False
                largeFlag = False
                smallLocalPath = ''
                smallServerPath = ''
                largeLocalPath = ''
                largeServerPath = ''
                # for num in range(len(title_bgColor_err_list)):
                #     title_bgColor_err_list.pop()
                title_bgColor_err_list = [None,None,None,None,None]
                cnt = cnt +1

                #title / icon color 비교
                local_f = open(resPath+'\\'+serverAppID+'\\appinfo.json','r',encoding="utf8")
                local_appinfo_json = json.loads(local_f.read())
                local_f.close()

                server_f = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\appinfo.json','r',encoding="utf8")
                server_appinfo_json = json.loads(server_f.read())
                server_f.close()

                #icon color 비교
                iconColorExist = check_icon_color_exist(local_appinfo_json, server_appinfo_json)
                iconColorError = True

                if(iconColorExist == 'ALL_EXIST' or iconColorError == 'NOT_EXIST'):
                    if(iconColorExist == 'ALL_EXIST'):
                        localIconColor = local_appinfo_json['iconColor'].upper()
                        serverIconColor = server_appinfo_json['iconColor'].upper()

                    if(localIconColor == serverIconColor):
                        #Title 비교
                        serverResAppPath = serverResPath+'\\__serverResource\\'+serverAppID
                        server_en_json = None
                        if(local_appinfo_json['title'] != server_appinfo_json['title']):
                            if('resources' in os.listdir(serverResAppPath)):
                                if('en' in os.listdir(serverResAppPath+'\\resources')):
                                    server_en_f = open(serverResAppPath+'\\resources\\en\\appinfo.json','r',encoding="utf8")
                                    server_en_json = json.loads(server_en_f.read())
                                    server_en_f.close()

                        localization_flag = None

                        if(server_en_json != None and local_appinfo_json['title'] == server_en_json['title']):
                            localizationExcel = localizationPath + '\\cpstub-apps.xliff'
                            localization_flag = localization_check(localizationExcel,local_appinfo_json['title'],server_appinfo_json['title'],serverAppID)

                        if((local_appinfo_json['title'] == server_appinfo_json['title'])
                            or (server_en_json != None and local_appinfo_json['title'] == server_en_json['title'] and localization_flag == True)):

                            #icon 비교
                            local_image = open(resPath+'\\'+serverAppID+'\\icon.png','rb').read()
                            localHash = hashlib.md5(local_image).hexdigest()

                            local_large_image = open(resPath+'\\'+serverAppID+'\\largeIcon.png','rb').read()
                            localLargeHash = hashlib.md5(local_large_image).hexdigest()

                            for value in os.listdir(serverResPath+'\\__serverResource\\'+serverAppID):
                                iconSize = findIconSize(value)
                                if(iconSize == '80x80'):
                                # if(value.find('80x80') != -1 and value.find('130x130') == -1):
                                    server_image = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value,'rb').read()
                                    serverHash = hashlib.md5(server_image).hexdigest()

                                    if(localHash == serverHash):
                                        smallLocalPath = resPath+'\\'+localAppID+'\\icon.png'
                                        smallServerpath = serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value
                                        smallFlag = True
                                if(iconSize == '130x130'):
                                # if(value.find('130x130') != -1):
                                    server_image = open(serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value,'rb').read()
                                    serverHash = hashlib.md5(server_image).hexdigest()

                                    if (localLargeHash == serverHash):
                                        largeLocalPath = resPath+'\\'+localAppID+'\\largeIcon.png'
                                        largeServerPath = serverResPath+'\\__serverResource\\'+serverAppID+'\\'+value
                                        largeFlag = True

                            if(smallFlag == True and largeFlag == True):
                                smallIcon_localPathDic[localAppID] = smallLocalPath
                                smallIcon_serverPathDic[serverAppID] = smallServerpath
                                largeIcon_localPathDic[localAppID] = largeLocalPath
                                largeIcon_serverPathDic[serverAppID] = largeServerPath

                                if(local_appinfo_json['title'] == server_appinfo_json['title']):
                                    title_bgColor_err_list[2] = local_appinfo_json['title']
                                    title_bgColor_err_list[3] = server_appinfo_json['title']
                                elif(local_appinfo_json['title'] == server_en_json['title']):
                                    title_bgColor_err_list[2] = local_appinfo_json['title']
                                    title_bgColor_err_list[3] = server_en_json['title']

                                if(iconColorExist == 'ALL_EXIST'):
                                    title_bgColor_err_list[0] = local_appinfo_json['iconColor']
                                    title_bgColor_err_list[1] = server_appinfo_json['iconColor']
                                else:
                                    title_bgColor_err_list[0] = 'X'
                                    title_bgColor_err_list[1] = 'X'

                                title_bgColor_err_list[4] = 'All Match!!'
                                title_bgColor_err_dic[serverAppID] = title_bgColor_err_list
                                matchCount = matchCount+1
                                matchList.append(serverAppID)
                break

    print('check된 App Id 개수 : ' + str(cnt))
    print('matchCount : '+str(matchCount))
    iconList = [largeIcon_localPathDic,largeIcon_serverPathDic,smallIcon_localPathDic,smallIcon_serverPathDic]
    resource_err_list.append(iconList)
    resource_err_list.append(title_bgColor_err_dic)

    return resource_err_list

def findIconSize(iconName):
    iconSplit = iconName.split('_')
    iconSize = iconSplit[len(iconSplit)-2]

    return iconSize

def localization_check(localizationExcel, localTitle, serverTitle, serverAppId):
    tree = ElementTree.parse(localizationExcel)
    root = tree.getroot()
    localization_flag = False

    for node_File in root.getchildren():
        body = node_File.find('.//body')
        for value in body.getchildren():
            if((value.find('.//source').text == localTitle)
                and (value.find('.//target').text == serverTitle)):
                    localization_flag = True
                    # print('---------------------')
                    # print(serverAppId)
                    # print('다국어 번역 완료')
                    break
        if(localization_flag == True):
            break
    else:
        # print('---------------------')
        # print(serverAppId)
        # print('다국어 번역 필요')
        return False

    return True
###############################################################
######### server resource를 local에 적용하는 함수
######### @param
######### 1. resPath : 로컬 resource path
######### 2. serverResPath : server resource path
######### 3. resourceErrorList : resource error data List
###############################################################
def applyServerResource(resPath, serverResourcePath,resourceErrorList):
    iconList = resourceErrorList[0]
    title_bgColor_err_dic = resourceErrorList[1]

    appIDList = title_bgColor_err_dic.keys()

    for appID in appIDList:
        errType = title_bgColor_err_dic[appID][ERR_TYPE]

        if(errType.find('<Large Icon>') != -1):
            localPath = iconList[LOCAL_LARGE_ICON][appID]
            serverPath = iconList[SERVER_LARGE_ICON][appID]
            shutil.copy(serverPath,localPath)

        if(errType.find('<Small Icon>') != -1):
            localPath = iconList[LOCAL_SMALL_ICON][appID]
            serverPath = iconList[SERVER_SMALL_ICON][appID]
            shutil.copy(serverPath,localPath)

        if(errType.find('<Title>') != -1):
            jsonPath = resPath + '\\' + appID + '\\appinfo.json'

            with codecs.open(jsonPath, "r",encoding="utf8") as jsonFile:
                data = json.load(jsonFile)

            #다국어 확인 필요 문구는 삭제하고 app Title만 적용하기 위한 string 가공
            if(title_bgColor_err_dic[appID][SERVER_TITLE].find('다국어') != -1):
                buf = title_bgColor_err_dic[appID][SERVER_TITLE].split(" ")
                title_bgColor_err_dic[appID][SERVER_TITLE] = buf[0]

            data['title'] = title_bgColor_err_dic[appID][SERVER_TITLE]

            with codecs.open(jsonPath,'w',encoding="utf8") as jsonFile:
                jsonFile.write(json.dumps(data,indent=4, sort_keys=True,ensure_ascii=False))

            url = resPath + '\\' + appID + '\\index.html'
            changeList = []
            with open(url, encoding="utf8") as f:
                for value in f.readlines():
                    if(value.find('var appName') != -1):
                        # print('\tvar appName = "'+title_bgColor_err_dic[appID][SERVER_TITLE]+'";\n')
                        changeList.append('\tvar appName = "'+title_bgColor_err_dic[appID][SERVER_TITLE]+'";\n')
                    else:
                        changeList.append(value)

            with open(url, 'wb') as f:
                for num in range(len(changeList)):
                    f.write(changeList[num].encode())

        if(errType.find('<BackGround Color>') != -1):
            jsonPath = resPath + '\\' + appID + '\\appinfo.json'
            data = []
            with codecs.open(jsonPath, 'r', encoding='utf8') as jsonFile:
                data = json.load(jsonFile)

            if('iconColor' in data.keys()):
                if(title_bgColor_err_dic[appID][SERVER_BG_COLOR] == 'X'):
                    data['iconColor'] = ''
                    data['bgColor'] = ''
                else:
                    data['iconColor'] = title_bgColor_err_dic[appID][SERVER_BG_COLOR]
                    data['bgColor'] = title_bgColor_err_dic[appID][SERVER_BG_COLOR]
            else:
                if(title_bgColor_err_dic[appID][SERVER_BG_COLOR] != 'X'):
                    data['iconColor'] = title_bgColor_err_dic[appID][SERVER_BG_COLOR]
                    data['bgColor'] = title_bgColor_err_dic[appID][SERVER_BG_COLOR]

            with codecs.open(jsonPath,'w', encoding='utf8') as jsonFile:
                jsonFile.write(json.dumps(data,indent=4, sort_keys=True,ensure_ascii=False))
