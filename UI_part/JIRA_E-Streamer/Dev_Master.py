import xlrd
#import time

# weekdaystr=["(월)", "(화)", "(수)", "(목)", "(금)", "(토)", "(일)"]
class Dev_Meta:
    ''' 개발 Master 장표의 Meta 정보들에 대한 constant 관리 class
    '''
    ## 개발 Master의 개발/모델 년도
    devYear             = 2016
    modelYear           = devYear+1

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

        # key : final model_name, value : list of previous model names
        # ex. A→B→C 인 모델의 경우 {'C': ['A', 'B']}
        self.prev_model_names = {}

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
        return str(date.year)+"/"+str(date.month)+"/"+str(date.day)

    def getFilteredDateText(cls, txt):
        ## Date Format -> String "MM/DD"
        if type(txt) in [float, int]:
            return cls.convertFloatToDateString(txt)

        filteredTxt = cls.getFilteredText(txt)
        list_date = filteredTxt.split("/")
        if len(list_date)==2:
            mm = list_date[0]
            if int(mm)>10:
                yy=str(Dev_Meta.devYear)
            else:
                yy=str(Dev_Meta.modelYear)
        else:
            #print("list_date : "+filteredTxt)
            return filteredTxt
        #print("return date : "+yy+"/"+filteredTxt)
        return yy+"/"+filteredTxt

    def getFilteredText(cls, txt):
        list1 = txt.split("→")
        list2 = list1[len(list1)-1]
        return list2.split("(")[0].split("\n")[0]

    # Model Name은 변경사항에 대해 변경 전 모델명들을 return한다
    # ex. A->B->C->D로 3번 변경되었으면 ['A', 'B', 'C'] 을 return
    def getPrevModelNames(cls, txt):
        model_list = txt.split("→")
        prev_model_names = []
        if len(model_list)>1:
            print("exist prev model : "+str(model_list))
            for prev_model in range(0, len(model_list)-1):
                prev_model_name = model_list[prev_model].strip()
                prev_model_name = prev_model_name.split("(")[0].split("\n")[0]
                prev_model_names.append(prev_model_name)

        # for debug print : 나중에 지우자
        if len(prev_model_names)>0:
            last_model_name = cls.getFilteredText(txt)
            print("prev model names of "
                  +last_model_name
                  +" : "+str(prev_model_names))
        return prev_model_names

    def getFilteredRegionText(cls, region):
        ## Region에는 줄바꿈만 공백으로 치환하고 그대로
        region = region.replace('\n', ' ')
        return region


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
        if chassis[3]=='6' or chassis[3]=='8':
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

    def isValidDateString(cls, date):
        if type(date)!=str:
            return False
        tokens = date.split("/")
        if len(tokens)!=3:
            return False

        if int(tokens[0])<2016 or int(tokens[1])<1 or int(tokens[1])>12 or \
        int(tokens[2])<0 or int(tokens[2])>31:
            return False

        return True

    # compare two date String
    # assume two args are both string as format "yyyy/mm/dd"
    # ref. convertFloatToDateString()
    # return None if invalid params
    # return 0 if date1 == date2
    # return date1 - date2
    def compareDateString(cls, date1, date2):
        # assume args are only string
        if cls.isValidDateString(date1)==False:
            return 1
        if cls.isValidDateString(date2)==False:
            return -1

        tokens1 = date1.split("/")  ## array : yyyy, mm, dd
        tokens2 = date2.split("/")
        year1 = int(tokens1[0])
        year2 = int(tokens2[0])
        if year1!=year2:
            return year1-year2
        month1 = int(tokens1[1])
        month2 = int(tokens2[1])
        if month1!=month2:
            return month1-month2
        day1 = int(tokens1[2])
        day2 = int(tokens2[2])
        return day1-day2

    def getModelDataFromModelName(self, model_name):
        for model_data in self.table_data:
            try:
                if model_name == model_data[Dev_Meta.idxModelName]:
                    return model_data
            except:
                continue
        return None


    def compareForSort(self, model1, model2, index, second):
        dv_end1 = model1[index]
        dv_end2 = model2[index]
        result = self.compareDateString(dv_end1, dv_end2)
        if result == 0 and second is not None:
            second1 = int(model1[second])
            second2 = int(model2[second])
            return (second1 - second2)
        else:
            return result

    def cmp_to_key(self, mycmp, index_col, second=None):
        'Convert a cmp= function into a key= function'
        class K(object):
            def __init__(self, obj, *args):
                self.obj = obj
                self.index_col = index_col
                self.index_second = second
            def __lt__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) < 0
            def __gt__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) > 0
            def __eq__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) == 0
            def __le__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) <= 0
            def __ge__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) >= 0
            def __ne__(self, other):
                return mycmp(self.obj
                             , other.obj
                             , self.index_col
                             , self.index_second) != 0
        return K

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
                model_data[Dev_Meta.idxRegion] = self.getFilteredRegionText(model_data[Dev_Meta.idxRegion])
                model_data[Dev_Meta.idxModelName] = self.getFilteredText(model_data[Dev_Meta.idxModelName])
                self.prev_model_names[Dev_Meta.idxModelName] = self.getPrevModelNames(model_data[Dev_Meta.idxModelName])
                model_data[Dev_Meta.idxDvStart] = self.getFilteredDateText(model_data[Dev_Meta.idxDvStart])
                model_data[Dev_Meta.idxDvEnd] = self.getFilteredDateText(model_data[Dev_Meta.idxDvEnd])
                # 기획 담당자 설정
                model_data[Dev_Meta.idxHwPL+1] = self.getPlanOwnerName(model_data[Dev_Meta.idxRegion])
                self.table_data.append(model_data)


        # remove duplicated rows
        idxModelName = Dev_Meta.idxModelName
        idxDvEndDate = Dev_Meta.idxDvEnd

        # sort by DV end date
        self.table_data = sorted(self.table_data
                                 , key=self.cmp_to_key(self.compareForSort
                                                       , idxDvEndDate))


        # delete same models except for one (earlist dv end date)
        for row in range(0, len(self.table_data)-2):
            if row>=len(self.table_data)-1:
                break;
            row_data = self.table_data[row]
            dv_end1 = row_data[idxDvEndDate]
            for compare_row in range(len(self.table_data)-1, row, -1):
                compare_data = self.table_data[compare_row]
                dv_end2 = compare_data[idxDvEndDate]
                compare_result = self.compareDateString(dv_end1, dv_end2)
                if row_data[idxModelName]==compare_data[idxModelName]:
                    # print("compare "+dv_end1+", "+dv_end2)
                    if compare_result==None:
                        print("compare result is invalid")
                        if self.isValidDateString(dv_end1)==False:
                            print("del row_data: "+str(row_data))
                            print("dv_end1 : "+dv_end1)
                            del(self.table_data[row])
                            row=row-1
                            break;
                        else:    # dv_end2 is invalid date String
                            print("del compare_data: "+str(compare_data))
                            print("dv_end1 : "+dv_end2)
                            del(self.table_data[compare_row])
                    elif compare_result<=0:
                        # print("del compare_row : "+dv_end2)
                        del(self.table_data[compare_row])
                    else:       # dv_end of row_data > dv_end of compare_Data
                        # print("del row : "+dv_end1)
                        del(self.table_data[row])
                        row=row-1
                        break;
