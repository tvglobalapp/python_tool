import shutil
import os, glob
import xlrd, xlwt
import re
import threading
import json
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
from threadFunction import *
from saveIconTitleErrorData import *

class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.orderingPath = ''
        self.resPath = ''   #cpstub resource path
        self.delList = []
        self.addList = []
        self.appList = []
        self.dirList = []
        self.retList = []
        self.pathDic = {}
        self.countryCodeDic = {}
        self.threadMode = ''
        self.validationCheckPlatform = ''
        self.excelFilePath = ''
        self.excelFileName = ''
        self.serverResourcePath = ''
        self.resourceErrorList = None  #icon 비교를 위한 path,appID list모음
        self.resourceMatchList = None
        self.zipPath = '' #7zip Path저장용
        self.localizationPath = '' #localization path 저장용
        self.exportAll = False #excel 추출 시 전체 ? 변경점만 ? 설정하는 flag
        self.selectedAddList = []
        self.selectedDelList = []
        self.orderingChangeList = []
        self.platform_dic = {}
        with open("resources\platform_code.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                lineBuffer = line.replace("\n","")
                lineBuffer = lineBuffer.split('\t')
                self.platform_dic[lineBuffer[0]] = lineBuffer[1]

        self.serverOrderingFilePath = ''

    def setOrderingPath(self,path):
        # self.orderingPath = 'Y:\starfish-customization-consumer'
        self.orderingPath = path

    def setResPath(self,path):
        # self.resPath = 'Y:\cpstub-apps'
        self.resPath = path

    def setExcelFilePath(self,path):
        self.excelFilePath = path

    def setServerResourcePath(self,path):
        self.serverResourcePath = path

    def setPlatform(self,platform):
        # self.orderingPath = 'Y:\starfish-customization-consumer'
        self.validationCheckPlatform = platform

    def setExcelFileName(self,filename):
        self.excelFileName = filename

    def set7ZipPath(self,zipPath):
        self.zipPath = zipPath

    def setLocalizationPath(self,localizationPath):
        self.localizationPath = localizationPath

    def setServerOrderingFilePath(self,serverOrderingFilePath):
        self.serverOrderingFilePath = serverOrderingFilePath

    #flag가 true이면 전체 추출, false이면 변경점만 추출
    def setExportAll(self,flag):
        self.exportAll = flag
    #특정 경로의 폴더 명을 list로 만들어 return함.
    def getAppResourceDirName(self):
        dirList = []
        print(self.resPath)
        for a in os.listdir(self.resPath):
            if os.path.isdir(os.path.join(self.resPath,a)):
                if a != '.git':
                    dirList.append(a)
        return dirList

    def run(self):
######################################################
######### 필요/불필요 App resource checking하는 부분 ###
######### thread mode : check                #########
######################################################
        if self.threadMode == 'check':
            appList=[]
            dirList=[]
            self.delList = []
            self.addList = []
            self.pathDic.clear()
            self.countryCodeDic.clear()

            for (path, dir, files) in os.walk(self.orderingPath):
                for number in range(len(files)):
                    if files[number] == 'applist.json':
                        fullPath = os.path.join(path,files[number])
                        if(fullPath.find('qemux86') != -1):
                            continue
                        with open(fullPath) as f:
                            data = json.load(f)
                            if len(data["applications_dosci"]) > 0:
                                for appId in data["applications_dosci"]:
                                    appId = re.sub("\"", "", appId)
                                    appId = re.sub(",", "", appId)
                                    appList.append(appId)

                                    #path가 너무 길어 platform과 국가만 표기
                                    tempPath = path.split('\\')
                                    index = tempPath.index('launchpoints')
                                    try:
                                        savePath = '['+tempPath[index-1]+'/'+tempPath[index+1]+']'
                                    except IndexError:
                                        #예외처리 필요!!
                                        print("Path setting error!! need to set the right directory.")
                                    if appId in self.pathDic:
                                        self.pathDic[appId].append(savePath)
                                    else:
                                        self.pathDic[appId] = [savePath]

                                    if appId in self.countryCodeDic:
                                        for code in self.countryCodeDic[appId]:
                                            if code == tempPath[3]:
                                                break;
                                        else:
                                            self.countryCodeDic[appId].append(tempPath[3])
                                    else:
                                        self.countryCodeDic[appId] = [tempPath[3]]

            appList = list(set(appList))
            dirList = self.getAppResourceDirName()

            for res in dirList:
                for appId in appList:
                    if res == appId:
                        break;
                else:
                    self.delList.append(res)

            for appId in appList :
                for res in dirList:
                    if res == appId:
                        break;
                else:
                    self.addList.append(appId)

            self.appList = appList
            self.dirList = dirList

            self.taskFinished.emit()
######################################################
#########불필요한 App resource Delete하는 부분 #########
######### thread mode : del                  #########
######################################################
        elif self.threadMode == 'del':
            for delResName in self.selectedDelList:
                remove_directory(self.resPath,delResName.data(0))
            self.selectedDelList = []
            self.taskFinished.emit()
######################################################
#########필요한 App resource Add하는 부분 #########
######### thread mode : add                  #########
######################################################
        elif self.threadMode == 'add':
            print(self.selectedAddList)
            for addResName in self.selectedAddList:
                print(addResName.data(0))
                add_directory(self.resPath,addResName.data(0))
            self.selectedAddList = []
            self.taskFinished.emit()
####################################################
######### 서버 Ordering 비교 DB 추가하는 부분 ##################
######### thread mode : AddDB      #########
####################################################
        elif self.threadMode == 'AddDB':
            self.retList = []
            self.retList = add_DB(self.serverOrderingFilePath)
            print(self.retList)
            self.taskFinished.emit()
####################################################
######### Validation Check하는 부분 ##################
######### thread mode : CriticalCheck      #########
####################################################
        elif self.threadMode == 'CriticalCheck':
            self.retList = []
            self.retList = critical_item_check(self.excelFilePath,self.excelFileName)
            self.taskFinished.emit()
####################################################
######### Validation Check하는 부분 ##################
######### thread mode : BlankCellCheck      #########
####################################################
        elif self.threadMode == 'BlankCellCheck':
            self.retList = []
            self.retList = blank_cell_check(self.excelFilePath,self.excelFileName)
            self.taskFinished.emit()
####################################################
######### Validation Check하는 부분 ##################
######### thread mode : DuplicationCellCheck  #########
####################################################
        elif self.threadMode == 'DuplicationCellCheck':
            self.retList = []
            self.retList = duplication_cell_check(self.excelFilePath,self.excelFileName)
            self.taskFinished.emit()
####################################################
######### Validation Check하는 부분 ##################
######### thread mode : CountryCodeCheck  #########
####################################################
        elif self.threadMode == 'CountryCodeCheck':
            self.retList = []
            self.retList = country_code_check(self.orderingPath,self.platform_dic,self.excelFilePath,self.excelFileName)
            self.taskFinished.emit()
####################################################
######### Validation Check완료 후 적용 ##################
######### thread mode : OrderingCheckOK  #########
####################################################
        elif self.threadMode == 'OrderingCheckOK':
            self.orderingChangeList = ordering_apply(self.platform_dic,self.excelFilePath,self.excelFileName, self.orderingPath)
            self.taskFinished.emit()
####################################################
######### 서버 리소스 압축 푸는 부분 ##################
######### thread mode : decompression     #########
####################################################
        elif self.threadMode == 'decompression':
            decompression_server_resource(self.zipPath, self.serverResourcePath)
            self.taskFinished.emit()
####################################################
######### 서버 리소스 Item Title check 부분 ##########
######### thread mode : ItemTitleCheck     #########
####################################################
        elif self.threadMode == 'IconTitleCheck':
            resource_copy(self.serverResourcePath)
            if(self.exportAll == True):
                print('export All')
                self.resourceMatchList = all_resource_error_check(self.resPath, self.serverResourcePath, self.localizationPath)
                self.resourceErrorList = deffer_resource_error_check(self.resPath, self.serverResourcePath, self.localizationPath)
            else:
                print('export differ')
                self.resourceErrorList = deffer_resource_error_check(self.resPath, self.serverResourcePath, self.localizationPath)
            self.taskFinished.emit()
####################################################
######### 리소스 변경점을 Excel로 export 함 ##########
######### thread mode : ExportResourceData  #########
####################################################
        elif self.threadMode == 'ExportResourceData':
            if(self.pathDic != {}):
                errResource = saveIconTitleErrorData(self.resPath,self.resourceErrorList,self.resourceMatchList,self.pathDic)
                errResource.saveData()
            else:
                self.threadMode = 'ExportResourceDataError'
            self.taskFinished.emit()
###############################################################
######### 불일치 하는 server resource를 local에 적용함 ##########
######### thread mode : ApplyServerResource  ##################
################################################################
        elif self.threadMode == 'ApplyServerResource':
            applyServerResource(self.resPath, self.serverResourcePath,self.resourceErrorList)
            self.taskFinished.emit()
