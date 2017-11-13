import sys
import time
import threading
from copy import copy
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from makeCountryCode import *

class ChangeCMListViewer(QtWidgets.QDialog):
    def __init__(self,path,countryCodedic,addList,delList):
        super(ChangeCMListViewer, self).__init__()

        # QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("resources\cmakeListViewer.ui", self)
        self.ui.show()
        self.countryCodeList = makeCountryCodeList()
        self.delList = delList
        self.delList.sort()
        self.countryCodedic = countryCodedic
        self.path = path
        self.necessaryList = addList #list(countryCodedic.keys())

        self.necessaryList.sort()
        for item in delList:
            self.ui.delBox.addItem(item)

        for item in self.necessaryList:
            self.ui.addBox.addItem(item)

    # select All del list radio button
    @pyqtSlot()
    def slotDelListSelectAll(self):
        if self.ui.delRadio.isChecked():
            for num in range(self.ui.delBox.count()):
                self.ui.delBox.item(num).setSelected(True)
        else:
            for num in range(self.ui.delBox.count()):
                self.ui.delBox.item(num).setSelected(False)

    # select All add list radio button
    @pyqtSlot()
    def slotAddListSelectAll(self):
        if self.ui.addRadio.isChecked():
            for num in range(self.ui.addBox.count()):
                self.ui.addBox.item(num).setSelected(True)
        else:
            for num in range(self.ui.addBox.count()):
                self.ui.addBox.item(num).setSelected(False)

    #country Code가 ATSC/DVB/ARIB 인지를 return한다.
    def getGroup(self,code):
        for country in self.countryCodeList.atscList:
            if country == code:
                return 'ATSC'
        for country in self.countryCodeList.dvbList:
            if country == code:
                return 'DVB'
        for country in self.countryCodeList.aribList:
            if country == code:
                return 'ARIB'

    # change start 버튼 선택 시
    @pyqtSlot()
    def slotChangeStartBtn(self):
        ######################################################
        ######### CMakeLists 변경 부분
        ######### textListAfterDel    :  불필요 resource 삭제 후 list
        ######### textListAfterAdd    :  필요 resource 추가 후 list
        ######################################################
        textListAfterDel = []
        textListAfterAdd = []

        #필요 AppID를 추가하기 위한 group 별 list
        atscList = []
        dvbList = []
        aribList = []

        #추가 필요한 AppID를 group별로 분류하기 위한 버퍼 dictionary
        groupBuf = {'ATSC':[],'DVB':[],'ARIB':[]}

        #Group별로 dictionary value 추가를 위한 flag
        groupFlag = "__NONE__"

        delList = self.ui.delBox.selectedItems()
        addList = self.ui.addBox.selectedItems()

        countryDic = self.countryCodedic.copy()

        for app in self.countryCodedic.keys():
            for addItem in addList:
                if app == addItem.data(0):
                    break
            else:
                del countryDic[app]

        cmListPath = self.path + '\CMakeLists.txt'

        for appId in countryDic.keys():
            for code in countryDic[appId]:
                groupCode = self.getGroup(code)
                if groupCode == 'ATSC':
                    groupBuf['ATSC'].append(appId)
                elif groupCode == 'DVB':
                    groupBuf['DVB'].append(appId)
                elif groupCode == 'ARIB':
                    groupBuf['ARIB'].append(appId)
                else:
                    print(appId)
                    pass

        groupBuf['ATSC'] = list(set(groupBuf['ATSC']))
        groupBuf['DVB'] = list(set(groupBuf['DVB']))
        groupBuf['ARIB'] = list(set(groupBuf['ARIB']))

        ### 불필요 AppID 삭제 부분
        with open(cmListPath, 'r') as f:
            savelist = f.readlines()

            for num in range(len(savelist)):
                appID = savelist[num].replace("    ","")
                appID = appID.replace("\n","")

                if appID.find(")") != -1:
                    appID = appID.replace(")","")

                for delID in delList:
                    if appID == delID.data(0):
                        break;
                else:
                    textListAfterDel.append(savelist[num])

            for num in range(len(textListAfterDel)):
                if textListAfterDel[num] == "\n":
                    if textListAfterDel[num-1].find(")") == -1:
                        textListAfterDel[num-1] = textListAfterDel[num-1].replace("\n", "") + ')\n'

        ### 필요 AppID 추가 부분
        ### 불필요 AppID가 삭제된 List인 textListAfterDel를 기준으로
        ### 각 국가 코드별로 ATSC/DVB/ARIB 구분하여 각각의 list를 만드는 부분
        for num in range(len(textListAfterDel)):
            appID = textListAfterDel[num].replace("    ","")
            appID = appID.replace("\n","")
            if appID.find(")") != -1:
                appID = appID.replace(")","")

            if groupFlag == "__ATSC__":
                if appID == "":
                    groupFlag = "__NONE__"
                    continue
                atscList.append(appID)
            elif groupFlag == "__DVB__":
                if appID == "":
                    groupFlag = "__NONE__"
                    continue
                dvbList.append(appID)
            elif groupFlag == "__ARIB__":
                if appID == "":
                    groupFlag = "__NONE__"
                    continue
                aribList.append(appID)
            else:
                pass

            if appID == 'set(ATSC_CP_LISTS':
                groupFlag = "__ATSC__"
            elif appID == 'set(DVB_CP_LISTS':
                groupFlag = "__DVB__"
            elif appID == 'set(ARIB_CP_LISTS':
                groupFlag = "__ARIB__"
            else:
                pass

        ### ATSC/DVB/ARIB list에 추가할 App ID list 합치고 정렬하는 부분
        atscList.extend(groupBuf['ATSC'])
        atscList = list(set(atscList))
        atscList.sort()
        # print('======================\n')
        # print(atscList)
        dvbList.extend(groupBuf['DVB'])
        dvbList = list(set(dvbList))
        dvbList.sort()
        # print('======================\n')
        # print(dvbList)
        aribList.extend(groupBuf['ARIB'])
        aribList = list(set(aribList))
        aribList.sort()
        # print('======================\n')
        # print(aribList)
        ### CMakeLists.txt에 저장할 textListAfterAdd data 추가 부분
        ###App ID 이전 부분 추가
        for line in textListAfterDel:
            textListAfterAdd.append(line)
            if line == '# ATSC CP lists\n':
                break
        # print('======================\n')
        # print(textListAfterAdd)
        ### App ID 부분 추가
        textListAfterAdd.append('set(ATSC_CP_LISTS\n')
        for atscAppID in atscList:
            textListAfterAdd.append('    '+atscAppID+'\n')
        textListAfterAdd[-1] = textListAfterAdd[-1].replace("\n","")+')'+'\n'
        textListAfterAdd.append('\n')

        textListAfterAdd.append('# DVB CP lists\n')
        textListAfterAdd.append('set(DVB_CP_LISTS\n')
        for dvbAppID in dvbList:
            textListAfterAdd.append('    '+dvbAppID+'\n')
        textListAfterAdd[-1] = textListAfterAdd[-1].replace("\n","")+')'+'\n'
        textListAfterAdd.append('\n')

        textListAfterAdd.append('# ARIB CP lists\n')
        textListAfterAdd.append('set(ARIB_CP_LISTS\n')
        for aribAppID in aribList:
            textListAfterAdd.append('    '+aribAppID+'\n')
        textListAfterAdd[-1] = textListAfterAdd[-1].replace("\n","")+')'+'\n'
        textListAfterAdd.append('\n')

        ### App ID 이후 부분 추가
        addFlag = False;
        for line in textListAfterDel:
            if line == '# set the applist variable for each region\n':
                addFlag = True
            if addFlag == True:
                textListAfterAdd.append(line)

        ### 변경된 CMakeLists 저장 부분
        with open(cmListPath, 'wb') as f:
            for num in range(len(textListAfterAdd)):
                f.write(textListAfterAdd[num].encode())
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText("CMakeLists.txt change success.")
            retval = msg.exec_()
            self.close()
    @pyqtSlot()
    def slotCloseBtnClicked(self):
        self.close()
