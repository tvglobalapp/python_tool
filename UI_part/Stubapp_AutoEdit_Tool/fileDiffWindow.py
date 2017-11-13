import sys
import time
import threading
import xlsxwriter
import json
import codecs
import collections
from copy import copy
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox

class fileDiffWindow(QtWidgets.QDialog):
    def __init__(self,path,orderingChangeList,platformName, platform_dic):
        super(fileDiffWindow, self).__init__()

        self.ui = uic.loadUi("resources\FileDiffWindow.ui", self)
        self.ui.show()

        self.orderingPath = path
        orderingBuffer = collections.OrderedDict()

        for value in sorted(orderingChangeList[1].items()):
            orderingBuffer[value[0]] = orderingChangeList[1][value[0]]
        fullBuffer = orderingChangeList
        fullBuffer[1] = orderingBuffer

        self.orderingChangeList = fullBuffer
        self.platformName = platformName
        self.platform_dic = platform_dic

        self.infoTextEdit.append('Total Changed Area Num : '+ str(len(self.orderingChangeList[1].keys())))
        self.infoTextEdit.append('\n< Area Code >     < Changed Area Name >')
        self.infoTextEdit.append('--------------      -----------------------')

        for value in self.orderingChangeList[1].keys():
            newLine = len(self.orderingChangeList[1][value][1]) - len(self.orderingChangeList[1][value][2])

            self.beforeTextEdit.append(value + ' - '+ self.orderingChangeList[1][value][0]+'('+str(len(self.orderingChangeList[1][value][1]))+')\n')
            for data in self.orderingChangeList[1][value][1]:
                self.beforeTextEdit.append('- '+data)
            self.afterTextEdit.append(value + ' - '+ self.orderingChangeList[1][value][0]+'('+str(len(self.orderingChangeList[1][value][2]))+')\n')
            for data in self.orderingChangeList[1][value][2]:
                self.afterTextEdit.append('- '+data)
            if newLine > 0:
                for num in range(newLine):
                    self.afterTextEdit.append('')
            elif newLine < 0:
                for num in range(abs(newLine)):
                    self.beforeTextEdit.append('')
            else:
                pass
            self.beforeTextEdit.append('-----------------------------------------\n')
            self.afterTextEdit.append('-----------------------------------------\n')
            self.infoTextEdit.append('    ['+value+']\t      - '+self.orderingChangeList[1][value][0])

    @pyqtSlot()
    def slotCloseBtnClicked(self):
        self.close()

    @pyqtSlot()
    def slotApplyToJsonBtnClicked(self):
        platform_code = ''
        for value in self.platform_dic.keys():
            if self.platformName.find(value) != -1:
                platform_code = self.platform_dic[value]
        print(platform_code)

        for value in self.orderingChangeList[1].keys():
            new_applist_json = collections.OrderedDict()
            path = self.orderingPath+'\\'+platform_code+'\\launchpoints\\'+ value + '\\applist.json'
            f = codecs.open(path,'r',encoding="utf8")
            applist_json = json.loads(f.read())
            f.close()

            if 'applications_common' in applist_json.keys():
                new_applist_json['applications_common'] = applist_json['applications_common']

            new_applist_json['applications_dosci'] = applist_json['applications_dosci']
            new_applist_json['applications_dobci'] = applist_json['applications_dobci']
            new_applist_json['applications_dobci_oled'] = applist_json['applications_dobci_oled']

            new_applist_json['applications_dosci'] = self.orderingChangeList[1][value][2]

            with codecs.open(path,'w', encoding='utf8') as jsonFile:
                jsonFile.write(json.dumps(new_applist_json, indent=2, ensure_ascii=False))
        self.showDialog('TYPE_INFORMATION','변경점을 모두 반영하였습니다.')
    @pyqtSlot()
    def slotExportToExcelBtnClicked(self):
        filename = self.platformName + 'AppOrdering_Changes_Data.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        self.saveOrderingData(workbook)
        print("close workbook")
        try:
            workbook.close()
        except:
            self.showDialog('TYPE_WARNING','오류가 발생하여 저장에 실패하였습니다.')
        else:
            self.showDialog('TYPE_INFORMATION','저장에 성공하였습니다.')

    def saveOrderingData(self,workbook):
        sheetName = self.platformName.replace('(','')
        sheetName = sheetName.replace(')','')
        worksheet = workbook.add_worksheet(sheetName)

        title_style = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'fg_color': '#cccccc'})
        subtitle_style = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'fg_color': '#eeeeee'})

        text_style = workbook.add_format({'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter'})

        worksheet.set_column('A:B', 30)
        worksheet.set_column('D:G', 30)

        #title default 값 추가
        worksheet.write('A1','Total Changed Country Num',title_style)
        worksheet.write('B1','Changed Country Name',title_style)
        worksheet.merge_range('D1:D2', 'Country', title_style)
        worksheet.merge_range('E1:F1', 'App ID', title_style)
        worksheet.write('E2','AS-IS',subtitle_style)
        worksheet.write('F2','TO-BE',subtitle_style)

        worksheet.write('A2',len(self.orderingChangeList[1].keys()),text_style)
        cnt = 2
        mergeStartNum = 3
        appIDLineNum = 3
        mergeSize = 0

        for value in self.orderingChangeList[1].keys():
            worksheet.write('B'+str(cnt),self.orderingChangeList[1][value][0],text_style)

            if(len(self.orderingChangeList[1][value][1]) >= len(self.orderingChangeList[1][value][2])):
                mergeSize = len(self.orderingChangeList[1][value][1])
            else:
                mergeSize = len(self.orderingChangeList[1][value][2])

            countryData = '['+value+']'+self.orderingChangeList[1][value][0]
            worksheet.merge_range('D'+str(mergeStartNum)+':D'+str(mergeStartNum + mergeSize -1), countryData, text_style)
            mergeStartNum += mergeSize
            for num in range(mergeSize):
                try:
                    worksheet.write('E'+str(appIDLineNum),self.orderingChangeList[1][value][1][num],text_style)
                except:
                    worksheet.write('E'+str(appIDLineNum),'',text_style)

                try:
                    worksheet.write('F'+str(appIDLineNum),self.orderingChangeList[1][value][2][num],text_style)
                except:
                    worksheet.write('F'+str(appIDLineNum),'',text_style)

                appIDLineNum += 1

            cnt += 1

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
