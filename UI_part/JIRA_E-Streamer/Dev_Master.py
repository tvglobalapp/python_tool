import xlrd
#import time

class Dev_Master:
    global meta_info

    def __init__(self, settings=None):
        self.table_data=[];

        # 개발  Master Version과 File명
        self.version = ''
        self.xls_file_name = None

        self.settings = settings

        # key : final model_name, value : list of previous model names
        # ex. A→B→C 인 모델의 경우 {'C': ['A', 'B']}
        self.prev_model_names = {}

    ## 지역 별 기획 담당자
    def getPlanOwnerName(self, region):
        # set 기획 담당
        planOwner=''
        if region.find('한국')>=0:
            planOwner = self.settings.owner_plan['KR']
        elif region.find('북미')>=0:
            planOwner = self.settings.owner_plan['US']
        elif region.find('유럽')>=0:
            planOwner = self.settings.owner_plan['EU']
        elif region.find('CIS')>=0:
            planOwner = self.settings.owner_plan['CIS']
        elif region.find('인도')>=0 or region.find('아주')>=0 \
            or region.find('필리핀')>=0:
            planOwner = self.settings.owner_plan['AJ']
        elif region.find('중아')>=0 or region.find('이스라엘')>=0 \
            or region.find('이란')>=0:
            planOwner = self.settings.owner_plan['JA']
        elif region.find('브라질')>=0 or region.find('칠레')>=0 \
            or region.find('에콰도르')>=0 or region.find('페루')>=0 \
            or region.find('아르헨티나')>=0:
            planOwner = self.settings.owner_plan['BR']
        elif region.find('콜롬비아')>=0 or region.find('파나마')>=0:
            planOwner = self.settings.owner_plan['CO']
        elif region.find('대만')>=0:
            planOwner = self.settings.owner_plan['TW']
        elif region.find('일본')>=0:
            planOwner = self.settings.owner_plan['JP']
        elif region.find('중국')>=0:
            planOwner = self.settings.owner_plan['CN']
        elif region.find('홍콩')>=0:
            planOwner = self.settings.owner_plan['HK']
        else:
            planOwner = 'N/A'
        return planOwner

    def convertFloatToDateString(cls, fDate):
        import datetime
        import xlrd.xldate as xdate
        date = xdate.xldate_as_datetime(fDate, 0) ## datemode - 0 : 1900-base, 1 : 1904-base
        return str(date.year)+"/"+str(date.month)+"/"+str(date.day)

    def getFilteredDateText(self, txt):
        ## Date Format -> String "MM/DD"
        if type(txt) in [float, int]:
            return self.convertFloatToDateString(txt)

        filteredTxt = self.getFilteredText(txt)
        list_date = filteredTxt.split("/")
        if len(list_date)==2:
            mm = list_date[0]
            if int(mm)>10:
                yy=str(int(self.settings.mp_year)-1)
            else:
                yy=str(self.settings.mp_year)
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
            self.version = file_name.split('_')[0].split('★')[1]
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

    def isValidModelToDisplay(self, rowdata, checkLowendOption=False):
        if len(rowdata)<14:
            return False

        chassis=rowdata[self.settings.col_chassis]
        grade = rowdata[self.settings.col_grade]

        if type(grade)!=str:
            grade=''

        is_valid = True
        history = rowdata[self.settings.col_history]
        for drop_keyword in self.settings.drop_model_keywords:
            if history.find(drop_keyword)>=0:
                is_valid=False
                break
        if is_valid:
            is_valid_main_soc = False
            main_soc = rowdata[self.settings.col_mainsoc]
            if checkLowendOption is False:
                for webos_mainsoc in self.settings.mainsocs_webos:
                    if main_soc.find(webos_mainsoc)>=0:
                        is_valid_main_soc = True
                        rowdata[self.settings.col_mainsoc+1] = 'webOS'
                        break
            if is_valid_main_soc is False:
                for lowend_mainsoc in self.settings.mainsocs_lowend:
                    if main_soc.find(lowend_mainsoc)>=0:
                        is_valid_main_soc = True
                        rowdata[self.settings.col_mainsoc+1] = 'Lowend'
                        break
            if is_valid_main_soc is False:
                is_valid = False
        if is_valid:
            if rowdata[self.settings.col_model_name]=='':
                is_valid = False
        if is_valid:
            if chassis=='' or chassis=='TBD' or grade.endswith('D_VA')==False:
                is_valid = False
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
                if model_name == model_data[self.settings.col_model_name]:
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
        print("chkedLowend:"+str(isCheckedLowend)+", ver : "+self.version)
        workbook = xlrd.open_workbook(self.xls_file_name)
        ws = workbook.sheet_by_index(1)

        # erase all privious data
        self.table_data.clear();
        total_row = 0;

        col_region      = self.settings.col_region
        col_model_name  = self.settings.col_model_name
        col_dev_pl      = self.settings.col_dev_pl
        col_hw_pl       = self.settings.col_hw_pl
        col_grade       = self.settings.col_grade
        col_mainsoc     = self.settings.col_mainsoc
        col_chassis     = self.settings.col_chassis
        col_dv_start    = self.settings.col_dv_start
        col_dv_end      = self.settings.col_dv_end

        for row in range(self.settings.row_header+1, ws.nrows):
            model_data = ws.row_values(row)

            if self.isValidModelToDisplay(model_data, isCheckedLowend):
                total_row+=1
                model_data.append(str(row+1))

                ## format excel data
                model_data[col_region] = self.getFilteredRegionText(model_data[col_region])
                model_data[col_model_name] = self.getFilteredText(model_data[col_model_name])
                self.prev_model_names[col_model_name] = self.getPrevModelNames(model_data[col_model_name])
                model_data[col_mainsoc] = self.getFilteredText(model_data[col_mainsoc])
                model_data[col_dv_start] = self.getFilteredDateText(model_data[col_dv_start])
                model_data[col_dv_end] = self.getFilteredDateText(model_data[col_dv_end])

                # 기획 담당자 설정
                model_data[col_hw_pl+1] = self.getPlanOwnerName(model_data[col_region])
                self.table_data.append(model_data)



        # sort by DV end date
        self.table_data = sorted(self.table_data
                                 , key=self.cmp_to_key(self.compareForSort
                                                       , col_dv_end))


        # delete same models except for one (earlist dv end date)
        for row in range(0, len(self.table_data)-2):
            if row>=len(self.table_data)-1:
                break;
            row_data = self.table_data[row]
            dv_end1 = row_data[col_dv_end]
            for compare_row in range(len(self.table_data)-1, row, -1):
                compare_data = self.table_data[compare_row]
                dv_end2 = compare_data[col_dv_end]
                compare_result = self.compareDateString(dv_end1, dv_end2)
                if row_data[col_model_name]==compare_data[col_model_name]:
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
