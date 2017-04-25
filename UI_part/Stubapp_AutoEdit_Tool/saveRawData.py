import shutil
import os, glob
import xlrd, xlwt
import re
from PyQt5.QtWidgets import QMessageBox

class saveRawData:
    def __init__(self,appList,dirList,pathDic):
        self.applist = appList
        self.dirlist = dirList
        self.pathDic = pathDic

    def saveData(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet_del = workbook.add_sheet('삭제 필요 resource')
        worksheet_add = workbook.add_sheet('추가 필요 resource')

        title_style = xlwt.easyxf('font: name Arial, bold on, color white; pattern: pattern solid, fore_colour gray25; align: horiz center;borders: top thin,bottom thin,right thin,left thin')
        res_text_style = xlwt.easyxf('font: name Arial, color blue;borders: top thin,bottom thin,right thin,left thin')
        text_style = xlwt.easyxf('font: name Arial, color blue;borders: top thin,bottom thin,right thin,left thin')
        subTitle_style = xlwt.easyxf('font: name Arial, bold on, color-index white;pattern: pattern solid, fore_colour gray25;borders: top thin,bottom thin,right thin,left thin')

        worksheet_del.col(0).width = 256 * 30
        worksheet_del.col(1).width = 256 * 30
        worksheet_del.col(2).width = 256 * 90

        worksheet_add.col(0).width = 256 * 30
        worksheet_add.col(1).width = 256 * 90

        worksheet_del.write_merge(0,0,0,2,'삭제 필요 resource',title_style)
        worksheet_del.write(1,0,'cpstub-apps Git',subTitle_style)
        worksheet_del.write(1,1,'starfish-customization-consumer Git',subTitle_style)
        worksheet_del.write(1,2,'starfish-customization-consumer Git path',subTitle_style)

        worksheet_add.write_merge(0,0,0,1,'추가 필요 resource',title_style)
        worksheet_add.write(1,0,'starfish-customization-consumer Git',subTitle_style)
        worksheet_add.write(1,1,'starfish-customization-consumer Git path',subTitle_style)

        for resNum in range(len(self.dirlist)):
            for appIdNum in range(len(self.applist)):
                if self.dirlist[resNum] == self.applist[appIdNum]:
                    res_text_style = xlwt.easyxf('font: name Arial, color blue;borders: top thin,bottom thin,right thin,left thin')
                    worksheet_del.write(resNum+2,1,self.dirlist[resNum],text_style)
                    value = '\n'.join(self.pathDic.get(self.applist[appIdNum]))
                    worksheet_del.write(resNum+2,2,value,text_style)
                    break;
            else:
                res_text_style = xlwt.easyxf('font: name Arial, color red;borders: top thin,bottom thin,right thin,left thin')

            worksheet_del.write(resNum+2,0,self.dirlist[resNum],res_text_style)

        lineCnt = 0
        for appIdNum in range(len(self.applist)):
            for resNum in range(len(self.dirlist)):
                if self.dirlist[resNum] == self.applist[appIdNum]:
                    break;
            else:
                res_text_style = xlwt.easyxf('font: name Arial, color red;borders: top thin,bottom thin,right thin,left thin')
                worksheet_add.write(lineCnt+2,0,self.applist[appIdNum],res_text_style)
                value = '\n'.join(self.pathDic.get(self.applist[appIdNum]))
                worksheet_add.write(lineCnt+2,1,value,text_style)
                lineCnt += 1

        try:
            workbook.save('App추가_삭제필요Data.xls')
            return True
        except PermissionError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText("[App추가_삭제필요Data.xls] file is opened. Please close the [App추가_삭제필요Data.xls] file and try again.")
            retval = msg.exec_()
            return False
