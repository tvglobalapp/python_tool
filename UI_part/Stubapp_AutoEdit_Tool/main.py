import sys
import os
import json
import time
import threading
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from workThread import *
from saveRawData import *
from ChangeCMListViewer import *
from fileDiffWindow import *

class MainForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("resources\ResourceChecker.ui", self)

        self.timeUpdate()
        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)

        #초기 사용자가 설정했던 Path 자동 설정 코드
        try:
            self.pathInfo = open('resources\pathInfo.json','r',encoding="utf8")
            self.pathInfoList = json.loads(self.pathInfo.read())
            self.pathInfo.close()
        except:
            self.pathInfoList = {'orderingPath':'',
                            'resourcePath':'',
                            '7zipPath':'',
                            'serverResourcePath':'',
                            'localizationPath':''}
        self.ui.orderingFolderNameLabel.setText(self.pathInfoList['orderingPath'])
        self.ui.resFolderNameLabel.setText(self.pathInfoList['resourcePath'])
        self.ui.zipPathEdit.setText(self.pathInfoList['7zipPath'])
        self.ui.serverResourceEdit.setText(self.pathInfoList['serverResourcePath'])
        self.ui.localizationEdit.setText(self.pathInfoList['localizationPath'])

        self.myLongTask.setOrderingPath(self.pathInfoList['orderingPath'])
        self.myLongTask.setResPath(self.pathInfoList['resourcePath'])
        self.myLongTask.set7ZipPath(self.pathInfoList['7zipPath'])
        self.myLongTask.setServerResourcePath(self.pathInfoList['serverResourcePath'])
        self.myLongTask.setLocalizationPath(self.pathInfoList['localizationPath'])

        self.pathDic = {'orderingPath':self.pathInfoList['orderingPath'],
                        'resourcePath':self.pathInfoList['resourcePath'],
                        '7zipPath':self.pathInfoList['7zipPath'],
                        'serverResourcePath':self.pathInfoList['serverResourcePath'],
                        'localizationPath':self.pathInfoList['localizationPath']}

    def timeUpdate(self):
        threading.Timer(1.0,self.timeUpdate).start()
        self.ui.dateLabel.setText(time.ctime())

#############################   Thread Code   ###############################

    def onStart(self,threadMode):
        self.ui.progressBar.setRange(0,0)
        self.myLongTask.threadMode = threadMode
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        self.ui.progressBar.setRange(0,1)
        self.ui.progressBar.setValue(1)
        self.ui.checkStartBtn.setEnabled(True)
        if self.myLongTask.threadMode == 'check':
            self.addResToListBox(self.myLongTask.delList,self.ui.delResBox)
            self.addResToListBox(self.myLongTask.addList,self.ui.necessaryResBox)

            if len(self.myLongTask.delList) > 0 or len(self.myLongTask.addList) > 0:
                if len(self.myLongTask.delList) > 0:
                    self.ui.delAllButton.setEnabled(True)
                if len(self.myLongTask.addList) > 0:
                    self.ui.addAllButton.setEnabled(True)
                self.ui.saveBtn.setEnabled(True)
                self.ui.changeCMListBtn.setEnabled(True)

            self.ui.totalResNumLabel.setText(str(len(self.myLongTask.dirList)))
            self.ui.totalAppIDNumLabel.setText(str(len(self.myLongTask.appList)))
            self.ui.delResNumLabel.setText('('+str(len(self.myLongTask.delList))+')')
            self.ui.needResNumLabel.setText('('+str(len(self.myLongTask.addList))+')')

        elif self.myLongTask.threadMode == 'del':
            self.showDialog('TYPE_INFORMATION','Success!! 선택한 Resource 삭제를 완료하였습니다..')
            num = self.ui.delResNumLabel.text().replace('(','')
            num = num.replace(')','')
            selectedNum = len(self.delResBox.selectedItems())
            self.ui.delResNumLabel.setText(str(int(num) - selectedNum))
            for selectedItem in self.delResBox.selectedItems():
                self.delResBox.takeItem(self.delResBox.row(selectedItem))

        elif self.myLongTask.threadMode == 'add':
            self.showDialog('TYPE_INFORMATION','Success!! 선택한 Resource 추가를 완료하였습니다.')
            num = self.ui.needResNumLabel.text().replace('(','')
            num = num.replace(')','')
            selectedNum = len(self.necessaryResBox.selectedItems())
            self.ui.needResNumLabel.setText(str(int(num) - selectedNum))
            for selectedItem in self.necessaryResBox.selectedItems():
                self.necessaryResBox.takeItem(self.necessaryResBox.row(selectedItem))

        elif self.myLongTask.threadMode == 'change':
            self.showDialog('TYPE_WARNING','Success!! CMakeLists file changed.')

        elif self.myLongTask.threadMode == 'AddDB':
            if(self.myLongTask.retList[0] == 'OK'):
                self.ui.compareErrorBox.setText(self.myLongTask.retList[1])
                self.exportDBBtn.setEnabled(True)
            elif(self.myLongTask.retList[0] == 'NG'):
                self.ui.compareErrorBox.setText(self.myLongTask.retList[1])

        elif self.myLongTask.threadMode == 'CriticalCheck':
            for value in range(1,len(self.myLongTask.retList)):
                self.resultTextEdit.append(self.myLongTask.retList[value])
            if(self.myLongTask.retList[0] == 'OK'):
                self.blankCheckBtn.setEnabled(True)
            else:
                self.resultTextEdit.append('\nPlease Check the Critical Items in selected Excel file.')

        elif self.myLongTask.threadMode == 'BlankCellCheck':
            for value in range(1,len(self.myLongTask.retList)):
                self.resultTextEdit.append(self.myLongTask.retList[value])
            if(self.myLongTask.retList[0] == 'OK'):
                self.dupCheckBtn.setEnabled(True)
            else:
                self.resultTextEdit.append('\nPlease Check the Blank cell in selected Excel file.')

        elif self.myLongTask.threadMode == 'DuplicationCellCheck':
            for value in range(1,len(self.myLongTask.retList)):
                self.resultTextEdit.append(self.myLongTask.retList[value])
            if(self.myLongTask.retList[0] == 'OK'):
                self.countryCheckBtn.setEnabled(True)
            else:
                self.resultTextEdit.append('\nPlease Check the Duplication cell in selected Excel file.')

        elif self.myLongTask.threadMode == 'CountryCodeCheck':
            for value in range(1,len(self.myLongTask.retList)):
                self.resultTextEdit.append(self.myLongTask.retList[value])
            if(self.myLongTask.retList[0] == 'OK'):
                self.OKBtn.setEnabled(True)
            elif(self.myLongTask.retList[0] == 'Error'):
                self.resultTextEdit.append('\nPlease Check the Country Code in selected Excel file.')
            else:
                pass

        elif self.myLongTask.threadMode == 'OrderingCheckOK':
            if self.myLongTask.orderingChangeList[0] == 'Same':
                self.showDialog('TYPE_INFORMATION','App Ordering이 일치합니다.\n 변경사항이 없습니다.')
            else:
                excelName = self.ui.excelFileComboBox.currentText()
                platformName = excelName.split('_')
                fileDiffWindow(self.myLongTask.orderingPath, self.myLongTask.orderingChangeList, platformName[0],self.myLongTask.platform_dic)

        elif self.myLongTask.threadMode == 'decompression':
            self.showDialog('TYPE_INFORMATION','모든 압축 풀기에 성공하였습니다.')
            self.iconTitleCheckBtn.setEnabled(True)

        elif self.myLongTask.threadMode == 'IconTitleCheck':
            if(len(self.myLongTask.resourceErrorList) == 0):
                self.showDialog('TYPE_INFORMATION','Icon / Title / Icon Color가 모두 일치합니다.')
            else:
                resourceErrorList = self.myLongTask.resourceErrorList
                errorAppIdList = resourceErrorList[1].keys()
                iconErrorAppIdList = []
                titleErrorAppIdList = []
                colorErrorAppIdList = []

                print('Error App 개수 : '+ str(len(errorAppIdList)))

                for appId in errorAppIdList:
                    if(resourceErrorList[1].get(appId)[4].find('<Large Icon>') != -1
                       or resourceErrorList[1].get(appId)[4].find('<Small Icon>') != -1):
                       iconErrorAppIdList.append(appId)

                    if(resourceErrorList[1].get(appId)[4].find('<Title>') != -1):
                        titleErrorAppIdList.append(appId)

                    if(resourceErrorList[1].get(appId)[4].find('<BackGround Color>') != -1):
                        colorErrorAppIdList.append(appId)

                self.ui.iconErrorNumLabel.setText(str(len(iconErrorAppIdList)))
                self.ui.titleErrorNumLabel.setText(str(len(titleErrorAppIdList)))
                self.ui.colorErrorNumLabel.setText(str(len(colorErrorAppIdList)))

                self.addResToListBox(iconErrorAppIdList,self.ui.iconBox)
                self.addResToListBox(titleErrorAppIdList,self.ui.titleBox)
                self.addResToListBox(colorErrorAppIdList,self.ui.colorBox)

                self.ui.iconTitleSaveBtn.setEnabled(True)
                self.ui.applyBtn.setEnabled(True)

        elif self.myLongTask.threadMode == 'ExportResourceData':
            self.showDialog('TYPE_WARNING','Success!! 변경점 Excel file이 생성완료 되었습니다.')
        elif self.myLongTask.threadMode == 'ExportResourceDataError':
            self.showDialog('TYPE_WARNING','Error!! Resource 필요여부 검사를 먼저 진행해 주세요!')
        elif self.myLongTask.threadMode == 'ApplyServerResource':
            self.showDialog('TYPE_WARNING','Success!! 변경점 적용이 완료 되었습니다.')
            self.ui.iconBox.clear()
            self.ui.titleBox.clear()
            self.ui.colorBox.clear()
            self.ui.iconErrorNumLabel.setText('')
            self.ui.titleErrorNumLabel.setText('')
            self.ui.colorErrorNumLabel.setText('')


#########################   Path Setting Code   ##########################

    #Excel folder open button을 click시 실행되는 slot
    @pyqtSlot()
    def slotOrderingFolderOpen(self):
        folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
        self.ui.orderingFolderNameLabel.setText(folderName)
        self.myLongTask.setOrderingPath(folderName)
        self.savePathJsonFile('orderingPath',folderName)

        if self.ui.resFolderNameLabel.text() != '':
            self.ui.checkStartBtn.setEnabled(True)

    #stub app folder open button을 click시 실행되는 slot
    @pyqtSlot()
    def slotResourceFolderOpen(self):
        folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
        self.ui.resFolderNameLabel.setText(folderName)
        # self.pathControl.saveFolderPath(folderName)
        self.myLongTask.setResPath(folderName)
        self.savePathJsonFile('resourcePath',folderName)

        if self.ui.orderingFolderNameLabel.text() != '':
            self.ui.checkStartBtn.setEnabled(True)

###################          서버 Ordering 비교        #################
    #서버 Ordering excel open button을 click시 실행되는 slot
    @pyqtSlot()
    def slotServerOrderingExcelFileOpen(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName (self,"Open Server Ordering File","")
        self.ui.serverOrderingExcelFileName.setText(filePath[0])
        self.myLongTask.setServerOrderingFilePath(filePath[0])

        if self.ui.serverOrderingExcelFileName.text() != '':
            self.ui.addDBBtn.setEnabled(True)

    #DB 추가 button을 click시 실행되는 slot
    @pyqtSlot()
    def slotAddDBBtnClicked(self):
        self.onStart('AddDB')

    #DB 추출 button을 click시 실행되는 slot
    @pyqtSlot()
    def slotExportDBBtnClicked(self):
        self.showDialog('TYPE_WARNING','구현중입니다!!')

    #DB 추출 button을 click시 실행되는 slot
    @pyqtSlot()
    def slotPastDataComboClicked(self):
        self.showDialog('TYPE_WARNING','구현중입니다!!')

    @pyqtSlot()
    def slotCurrentDataComboClicked(self):
        self.showDialog('TYPE_WARNING','구현중입니다!!')

    @pyqtSlot()
    def slotServerOrderingCompareBtnClicked(self):
        self.showDialog('TYPE_WARNING','구현중입니다!!')

    @pyqtSlot()
    def slotServerOrderingCompareResultBtnClicked(self):
        self.showDialog('TYPE_WARNING','구현중입니다!!')
###################   Ordering 문서 검사 / Json 적용   #################

    #Excel folder open button을 click시 실행되는 slot
    @pyqtSlot()
    def slotOrderingExcelFileOpen(self):
        excelFileList = []

        folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
        self.ui.excelFolderNameLabel.setText(folderName)
        self.myLongTask.setExcelFilePath(folderName)

        # 설정된 excel 경로의 excel file을 추출하여 list에 담고 combo box에 append하는 코드
        for (path, dir, files) in os.walk(folderName):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == '.xlsx' or ext == '.xls':
                    excelFileList.append(filename)

        if(len(self.ui.excelFileComboBox) > 0):
            self.ui.excelFileComboBox.clear()

        for fileName in excelFileList:
            self.ui.excelFileComboBox.addItem(fileName)

    #Validation check를 시작하는 부분
    @pyqtSlot()
    def slotValidationCheck(self):
        if(self.ui.excelFileComboBox.count() == 0):
            self.showDialog('TYPE_WARNING','Excel 파일을 선택하세요!!')
        else:
            platform_list = self.myLongTask.platform_dic.keys()
            for value in platform_list:
                if(self.ui.excelFileComboBox.currentText().find(value) != -1):
                    self.myLongTask.setPlatform(self.myLongTask.platform_dic[value])
                    self.myLongTask.setExcelFileName(self.ui.excelFileComboBox.currentText())

                    self.ui.resultTextEdit.clear()
                    self.ui.itemCheckBtn.setEnabled(True)
                    self.ui.blankCheckBtn.setEnabled(False)
                    self.ui.dupCheckBtn.setEnabled(False)
                    self.ui.countryCheckBtn.setEnabled(False)
                    self.ui.OKBtn.setEnabled(False)
                    break;
            else:
                self.showDialog('TYPE_WARNING','Platform Code가 없습니다. \n해당 파일의 platform code를 Git이나 resources/platform_code.txt에서 확인해 주세요')


    @pyqtSlot()
    def slotExcelFileChanged(self):
        self.ui.resultTextEdit.clear()
        self.ui.itemCheckBtn.setEnabled(False)
        self.ui.blankCheckBtn.setEnabled(False)
        self.ui.dupCheckBtn.setEnabled(False)
        self.ui.countryCheckBtn.setEnabled(False)
        self.ui.OKBtn.setEnabled(False)
    @pyqtSlot()
    def slotCriticalCheck(self):
        self.ui.resultTextEdit.clear()
        self.onStart('CriticalCheck')
    @pyqtSlot()
    def slotBlankCellCheck(self):
        self.ui.resultTextEdit.clear()
        self.onStart('BlankCellCheck')
    @pyqtSlot()
    def slotDupCheck(self):
        self.ui.resultTextEdit.clear()
        self.onStart('DuplicationCellCheck')
    @pyqtSlot()
    def slotCountryCheck(self):
        self.ui.resultTextEdit.clear()
        self.onStart('CountryCodeCheck')

    @pyqtSlot()
    def slotOKBtnClicked(self):
        self.onStart('OrderingCheckOK')
#########################   서버 Resource 비교 Code   ##########################

    #서버 Resource 경로 설정하는 button click시 실행되는 slot
    @pyqtSlot()
    def slotServerResourcePath(self):
        folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
        self.ui.serverResourceEdit.setText(folderName)
        self.myLongTask.setServerResourcePath(folderName)
        self.savePathJsonFile('serverResourcePath',folderName)

    #서버 Resource 경로 설정하는 button click시 실행되는 slot
    @pyqtSlot()
    def slot7ZipPath(self):
        folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
        self.ui.zipPathEdit.setText(folderName)
        self.myLongTask.set7ZipPath(folderName)
        self.savePathJsonFile('7zipPath',folderName)

    @pyqtSlot()
    def slotDecompressionBtnClicked(self):
        if(self.ui.serverResourceEdit.text() == ''):
            self.showDialog('TYPE_WARNING','Please, Set the Server Resource Path!!!')
        elif(self.ui.zipPathEdit.text() == ''):
            self.showDialog('TYPE_WARNING','Please, Set the 7-Zip Path!!!')
        elif(self.ui.serverResourceEdit.text().find(' ') != -1):
            self.showDialog('TYPE_WARNING','경로의 띄어쓰기를 없애주세요!')
        else:
            self.onStart('decompression')

    @pyqtSlot()
    def slotItemTitleBtnClicked(self):
        if(self.ui.iconErrorNumLabel.text() != ''):
            self.ui.iconErrorNumLabel.setText('')
            self.ui.titleErrorNumLabel.setText('')
            self.ui.colorErrorNumLabel.setText('')
            self.ui.iconBox.clear()
            self.ui.titleBox.clear()
            self.ui.colorBox.clear()
            self.ui.applyBtn.setEnabled(False)
            self.ui.iconTitleSaveBtn.setEnabled(False)

        if(self.ui.localizationEdit.text() == ''):
            self.showDialog('TYPE_WARNING','Please, Set the localization-data Path!!!')
        else:
            self.onStart('IconTitleCheck')

    @pyqtSlot()
    def slotExportAllClicked(self):
        if(self.myLongTask.exportAll != True):
            self.myLongTask.setExportAll(True)

    @pyqtSlot()
    def slotExportDifferenceClicked(self):
        if(self.myLongTask.exportAll != False):
            self.myLongTask.setExportAll(False)

    @pyqtSlot()
    def slotIconTitleSaveResult(self):
        self.onStart('ExportResourceData')

    @pyqtSlot()
    def slotApplyResourceBtnClicked(self):
        self.onStart('ApplyServerResource')

    @pyqtSlot()
    def slotLocalizationPathBtnClicked(self):
            folderName = QtWidgets.QFileDialog.getExistingDirectory(self,"Open Folder","")
            self.ui.localizationEdit.setText(folderName)
            self.myLongTask.setLocalizationPath(folderName)
            self.savePathJsonFile('localizationPath',folderName)

#########################   Resource 필요여부 / 적용 Code   ##########################

    #resource Check button clicked
    @pyqtSlot()
    def slotCheckStart(self):
        if self.ui.orderingFolderNameLabel.text() == '' or self.ui.resFolderNameLabel.text() == '':
            self.showDialog('TYPE_WARNING','Please, Set the Path!!!')
            return

        if self.ui.totalResNumLabel.text() != '':
            self.ui.totalResNumLabel.setText('')
            self.ui.totalAppIDNumLabel.setText('')
            self.ui.delResNumLabel.setText('')
            self.ui.needResNumLabel.setText('')
        #button enable 설정
        self.ui.progressBar.setEnabled(True)
        self.ui.checkStartBtn.setEnabled(False)
        self.ui.changeCMListBtn.setEnabled(False)
        self.ui.delAllButton.setEnabled(False)
        self.ui.addAllButton.setEnabled(False)
        self.ui.saveBtn.setEnabled(False)

        self.ui.delResBox.clear()
        self.ui.necessaryResBox.clear()
        self.onStart('check')

    def addResToListBox(self,resList,targetBox):
        for value in resList:
            targetBox.addItem(value)

    #saveRaw data button clicked
    @pyqtSlot()
    def slotSaveRawData(self):
        # print(self.myLongTask.pathDic)
        rawData = saveRawData(self.myLongTask.appList,self.myLongTask.dirList,self.myLongTask.pathDic)
        if rawData.saveData() == True:
            self.showDialog('TYPE_INFORMATION','[App추가_삭제필요Data.xls] was successfully saved.')
    # del all 버튼 선택 시
    @pyqtSlot()
    def slotDeleteAll(self):
        if(len(self.ui.delResBox.selectedItems()) == 0):
            self.showDialog('TYPE_INFORMATION','삭제할 resource를 선택하세요.')
            return
        else:
            self.myLongTask.selectedDelList = self.ui.delResBox.selectedItems()
            self.onStart('del')

    # Add all 버튼 선택 시
    @pyqtSlot()
    def slotAddAll(self):
        if(len(self.ui.necessaryResBox.selectedItems()) == 0):
            self.showDialog('TYPE_INFORMATION','추가할 resource를 선택하세요.')
            return
        else:
            self.myLongTask.selectedAddList = self.ui.necessaryResBox.selectedItems()
            self.onStart('add')

    # change CMakeLists 버튼 선택 시
    @pyqtSlot()
    def slotChangeCMList(self):
        # self.onStart('change')
        ChangeCMListViewer(self.myLongTask.resPath,self.myLongTask.countryCodeDic, self.myLongTask.addList, self.myLongTask.delList)

################################# popup dialog code ########################################

    def showDialog(self,msgType,message):
        msg = QMessageBox()
        if msgType == 'TYPE_WARNING':
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
        elif msgType == 'TYPE_INFORMATION':
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Information")
            msg.setStandardButtons(QMessageBox.Ok)
        elif msgType == 'TYPE_QUESTION':
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        else:
            msg.setIcon(QMessageBox.NoIcon)
        msg.setText(message)
        retval = msg.exec_()

    def savePathJsonFile(self,key,folderName):
        self.pathDic[key] = folderName
        with open('resources\\pathInfo.json', 'w') as outfile:
            json.dump(self.pathDic, outfile, indent=4, sort_keys=True)

app = QtWidgets.QApplication(sys.argv)

if __name__ == '__main__': # only execute when directly run this file
    W = MainForm()
    W.show()
    # sys.exit(app.exec_())
    app.exec_()
