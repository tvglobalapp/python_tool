import xlrd
#import time

# weekdaystr=["(월)", "(화)", "(수)", "(목)", "(금)", "(토)", "(일)"]
class Dev_Meta:
    ''' 개발 Master 장표의 Meta 정보들에 대한 constant 관리 class
    '''
    ##개발 Master의 row index
    idxHeader             = 2
    idxStartModelInfo     = 3

    ##개발 Master의 column index
    idxComment         = 0
    idxRegion          = 2
    idxModelName       = 6
    idxDevPL           = 7
    idxHwPL            = 8
    idxGrade           = 11
    idxChassis         = 13
    idxDvStart         = 34
    idxDvEnd           = 37

class Dev_Master:
    global meta_info

    def __init__(self, xls=None):
        self.table_data=[];

        # 개발  Master Version과 File명
        self.version = ''
        self.xls_file_name = xls

    ## 지역 별 기획 담당자
    def getPlanOwnerName(cls, region):
        # set 기획 담당
        planOwner=''
        if region.find('한국')>=0:
            planOwner = '이동현J'
        elif region.find('북미')>=0:
            planOwner = '박정용J'
        elif region.find('북미')>=0:
            planOwner = '박정용J'
        elif region.find('유럽')>=0 or region.find('CIS')>=0:
            planOwner = '안태규Y'
        elif region.find('인도')>=0 or region.find('아주')>=0 \
            or region.find('중아')>=0 or region.find('이스라엘')>=0 \
            or region.find('이란')>=0:
            planOwner = '이현석Y'
        elif region.find('브라질')>=0 or region.find('칠레')>=0 \
            or region.find('에콰도르')>=0 or region.find('콜롬비아')>=0 \
            or region.find('파나마')>=0:
            planOwner = '김보미Y'
        else:
            planOwner = 'N/A'
        return planOwner

    def convertFloatToDateString(cls, fDate):
        import datetime
        import xlrd.xldate as xdate
        date = xdate.xldate_as_datetime(fDate, 0) ## datemode - 0 : 1900-base, 1 : 1904-base
        return str(date.month)+"/"+str(date.day)

    def getFilteredText(cls, txt):
        ## Date Format -> String "MM/DD"
        if type(txt) in [float, int]:
            return cls.convertFloatToDateString(txt)

        list1 = txt.split("→")
        list2 = list1[len(list1)-1]
        return list2.split("(")[0].split("\n")[0]

    def setDevMasterExcel(self, excel):
        self.xls_file_name = excel

    def parseMasterVersion(self):
        if self.xls_file_name==None:
            self.version = ''
            return
        try:
            tokens = self.xls_file_name.split('/')
            file_name = tokens[len(tokens)-1]
            self.version = file_name.split('_')[0]
        except:
            pass

    def isLowendModel(cls, chassis):
        if len(chassis)<4:
            return False
        ## chassis[3] : Main SoC. 6=='M1A/M1Ap', 7=='M1Lp/M1LCp', 8=='M8RR'
        if chassis[3]=='6' or chassis[3]=='7' or chassis[3]=='8':
            return True
        else:
            return False

    def isValidLowendModel(self, rowdata, checkOption=False):
        if len(rowdata)<14:
            return False

        chassis=rowdata[Dev_Meta.idxChassis]
        grade = rowdata[Dev_Meta.idxGrade]

        if type(grade)!=str:
            grade=''
        if rowdata[Dev_Meta.idxComment]=='Drop':     ## 1) 'Drop' model
            is_valid = False
        elif rowdata[Dev_Meta.idxModelName]=='':     ## 2) Model Name empty
            is_valid = False
        elif chassis=='' or chassis=='TBD' or \
           (checkOption==True and \
           (self.isLowendModel(chassis)==False or grade.endswith('D_VA')==False)):
            is_valid = False
        else:
            is_valid = True
        return is_valid

    def updateDevMaster(self, isCheckedLowend):
        self.parseMasterVersion()
        print("ver : "+self.version)
        workbook = xlrd.open_workbook(self.xls_file_name)
        ws = workbook.sheet_by_index(1)

        # erase all privious data
        self.table_data.clear();
        total_row = 0;

        for row in range(Dev_Meta.idxStartModelInfo, ws.nrows):
            model_data = ws.row_values(row)
            if self.isValidLowendModel(model_data, isCheckedLowend):
                total_row+=1
                model_data.append(str(row+1))

                ## format excel data
                model_data[Dev_Meta.idxRegion] = self.getFilteredText(model_data[Dev_Meta.idxRegion])
                model_data[Dev_Meta.idxModelName] = self.getFilteredText(model_data[Dev_Meta.idxModelName])
                model_data[Dev_Meta.idxDvStart] = self.getFilteredText(model_data[Dev_Meta.idxDvStart])
                model_data[Dev_Meta.idxDvEnd] = self.getFilteredText(model_data[Dev_Meta.idxDvEnd])
                # 기획 담당자 설정
                model_data[Dev_Meta.idxHwPL+1] = self.getPlanOwnerName(model_data[Dev_Meta.idxRegion])
                self.table_data.append(model_data)


        # remove duplicated rows
        modelName = Dev_Meta.idxModelName
        for row in range(0, len(self.table_data)-2):
            for compare_row in range(len(self.table_data)-1, row, -1):
                row_data = self.table_data[row]
                compare_data = self.table_data[compare_row]
                if row_data[modelName]==compare_data[modelName]:
                    del(self.table_data[compare_row])
