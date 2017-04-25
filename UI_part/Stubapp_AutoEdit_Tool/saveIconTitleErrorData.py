import xlrd
import xlsxwriter
from PIL import Image
import io
import datetime
from define import *

class saveIconTitleErrorData:
    def __init__(self,resPath,errResList,matchResList,countryDic):
        self.matchIconList = None
        self.matchInfoDic = None
        self.resPath = resPath

        if(matchResList != None):
            self.matchIconList = matchResList[0]
            self.matchInfoDic = matchResList[1]
        self.errIconList = errResList[0]
        self.errInfoDic = errResList[1]
        self.countryDic = countryDic

        d = datetime.date.today()
        self.date = d.isoformat()

    def saveData(self):
        filename = '['+str(self.date) +']'+'Icon_Title_Compare_Result.xlsx'
        workbook = xlsxwriter.Workbook(filename)
        self.saveErrorData(workbook)
        if(self.matchIconList != None):
            self.saveMatchData(workbook)

        print("close workbook")
        try:
            workbook.close()
        except:
            print("exception occurs")
        else:
            print("not exception")

    def saveMatchData(self,workbook):
        worksheet = workbook.add_worksheet('Icon Title Match Data')

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

        text_style = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter'})

        sameCell = workbook.add_format({'bold': True,
                                        'border': 1,
                                        'align': 'center',
                                        'valign': 'vcenter'})

        worksheet.set_column('A:B', 15)
        worksheet.set_column('C:C', 50)
        worksheet.set_column('D:G', 15)
        worksheet.set_column('H:I', 15)
        worksheet.set_column('J:K', 20)

        #title default 값 추가
        worksheet.merge_range('A1:A3', 'App ID', title_style)
        worksheet.merge_range('B1:B3', 'Server Title', title_style)
        worksheet.merge_range('C1:C3', 'Error Type', title_style)
        worksheet.merge_range('D1:G1', 'Icon', title_style)
        worksheet.merge_range('D2:E2', 'Large', title_style)
        worksheet.merge_range('F2:G2', 'Small', title_style)
        worksheet.merge_range('J1:J3', 'Group', title_style)
        worksheet.merge_range('K1:K3', 'Service Country', title_style)
        worksheet.write('D3','Local',subtitle_style)
        worksheet.write('E3','Server',subtitle_style)
        worksheet.write('F3','Local',subtitle_style)
        worksheet.write('G3','Server',subtitle_style)
        worksheet.merge_range('H1:I2', 'Title', title_style)
        worksheet.write('H3','Local',subtitle_style)
        worksheet.write('I3','Server',subtitle_style)

        groupList = self.getCountryGroupListForAppID()
        # filename = 'D:\8. 자체 개발\CP_App_resource_자동화\(W17H)_Ordering(WEBOS)_20161114_004917_김종석K.xls'
        # countryBook = xlrd.open_workbook(filename)

        matchAppIdList = self.matchInfoDic.keys()

        row_num = 4
        for appId in matchAppIdList:
            group = ''
            for value in groupList[0]:
                if(appId == value):
                    group = group + '<ATSC> '
                    break
            for value in groupList[1]:
                if(appId == value):
                    group = group + '<DVB> '
                    break
            for value in groupList[2]:
                if(appId == value):
                    group = group + '<ARIB> '
                    break

            worksheet.write('J'+str(row_num), group,text_style)

            countryName = self.countryDic[appId]
            worksheet.write('K'+str(row_num), str(countryName),text_style)
            row_num = row_num + 1

        for value in range(3,len(self.matchInfoDic.keys())+3):
            worksheet.set_row(value,90)

        row_num = 4
        for appId in matchAppIdList:
            errType = self.matchInfoDic[appId][ERR_TYPE]

            worksheet.write('A'+str(row_num), appId,text_style)
            worksheet.write('B'+str(row_num), self.matchInfoDic[appId][SERVER_TITLE],text_style)
            worksheet.write('C'+str(row_num), errType,text_style)

            LocalbgColor = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vbottom'})
            serverbgColor = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vbottom'})

            if(self.matchInfoDic[appId][LOCAL_BG_COLOR] == 'X'):
                LocalbgColor.set_bg_color('#ffffff')
                LocalbgColor.set_font_color('red')
            else:
                LocalbgColor.set_bg_color(self.matchInfoDic[appId][LOCAL_BG_COLOR])
                fontColor = self.convertBGColor(self.matchInfoDic[appId][LOCAL_BG_COLOR])
                LocalbgColor.set_font_color(fontColor)

            if(self.matchInfoDic[appId][SERVER_BG_COLOR] == 'X'):
                serverbgColor.set_bg_color('#ffffff')
                serverbgColor.set_font_color('red')
            else:
                serverbgColor.set_bg_color(self.matchInfoDic[appId][SERVER_BG_COLOR])
                fontColor = self.convertBGColor(self.matchInfoDic[appId][SERVER_BG_COLOR])
                serverbgColor.set_font_color(fontColor)

            worksheet.write('D'+str(row_num), self.matchInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
            worksheet.write('E'+str(row_num), self.matchInfoDic[appId][SERVER_BG_COLOR],serverbgColor)
            worksheet.write('F'+str(row_num), self.matchInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
            worksheet.write('G'+str(row_num), self.matchInfoDic[appId][SERVER_BG_COLOR],serverbgColor)

            worksheet.write('H'+str(row_num), self.matchInfoDic[appId][LOCAL_TITLE],text_style)
            worksheet.write('I'+str(row_num), self.matchInfoDic[appId][SERVER_TITLE],text_style)

            local_image_data = None
            server_image_data = None
            local_image_data = self.get_resized_image_data(self.matchIconList[LOCAL_LARGE_ICON][appId])
            worksheet.insert_image('D'+str(row_num),
                                    self.matchIconList[LOCAL_LARGE_ICON][appId],
                                    {'x_offset': 30, 'y_offset': 20,
                                    'image_data': local_image_data})

            server_image_data = self.get_resized_image_data(self.matchIconList[SERVER_LARGE_ICON][appId])
            worksheet.insert_image('E'+str(row_num),
                                    self.matchIconList[SERVER_LARGE_ICON][appId],
                                    {'x_offset': 30, 'y_offset': 20,
                                    'image_data': server_image_data})

            local_image_data = None
            server_image_data = None

            local_image_data = self.get_resized_image_data(self.matchIconList[LOCAL_SMALL_ICON][appId])
            worksheet.insert_image('F'+str(row_num),
                                    self.matchIconList[LOCAL_SMALL_ICON][appId],
                                    {'x_offset': 30, 'y_offset': 20,
                                    'image_data': local_image_data})

            server_image_data = self.get_resized_image_data(self.matchIconList[SERVER_SMALL_ICON][appId])
            worksheet.insert_image('G'+str(row_num),
                                    self.matchIconList[SERVER_SMALL_ICON][appId],
                                    {'x_offset': 30, 'y_offset': 20,
                                    'image_data': server_image_data})
            row_num = row_num + 1

    def saveErrorData(self,workbook):

        worksheet = workbook.add_worksheet('Icon Title Error Data')

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

        appid_style = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter'})

        text_style = workbook.add_format({'bold': True,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'font_color': 'red'})

        sameCell = workbook.add_format({'bold': True,
                                        'border': 1,
                                        'align': 'center',
                                        'valign': 'vcenter'})

        worksheet.set_column('A:B', 15)
        worksheet.set_column('C:C', 50)
        worksheet.set_column('D:G', 15)
        worksheet.set_column('H:I', 15)
        worksheet.set_column('J:K', 20)

        #title default 값 추가
        worksheet.merge_range('A1:A3', 'App ID', title_style)
        worksheet.merge_range('B1:B3', 'Server Title', title_style)
        worksheet.merge_range('C1:C3', 'Error Type', title_style)
        worksheet.merge_range('D1:G1', 'Icon', title_style)
        worksheet.merge_range('D2:E2', 'Large', title_style)
        worksheet.merge_range('F2:G2', 'Small', title_style)
        worksheet.merge_range('J1:J3', 'Group', title_style)
        worksheet.merge_range('K1:K3', 'Service Country', title_style)
        worksheet.write('D3','Local',subtitle_style)
        worksheet.write('E3','Server',subtitle_style)
        worksheet.write('F3','Local',subtitle_style)
        worksheet.write('G3','Server',subtitle_style)
        worksheet.merge_range('H1:I2', 'Title', title_style)
        worksheet.write('H3','Local',subtitle_style)
        worksheet.write('I3','Server',subtitle_style)

        errAppIdList = self.errInfoDic.keys()
        groupList = self.getCountryGroupListForAppID()

        row_num = 4
        for appId in errAppIdList:
            group = ''
            for value in groupList[0]:
                if(appId == value):
                    group = group + '<ATSC> '
                    break;
            for value in groupList[1]:
                if(appId == value):
                    group = group + '<DVB> '
                    break;
            for value in groupList[2]:
                if(appId == value):
                    group = group + '<ARIB> '
                    break;

            worksheet.write('J'+str(row_num), group,text_style)

            countryName = self.countryDic[appId]
            worksheet.write('K'+str(row_num), str(countryName),text_style)
            row_num = row_num + 1

        for value in range(3,len(self.errInfoDic.keys())+3):
            worksheet.set_row(value,90)

        row_num = 4
        for appId in errAppIdList:
            errType = self.errInfoDic[appId][ERR_TYPE]

            worksheet.write('A'+str(row_num), appId,appid_style)
            worksheet.write('B'+str(row_num), self.errInfoDic[appId][SERVER_TITLE],appid_style)
            worksheet.write('C'+str(row_num), errType,appid_style)

            if(errType.find('<BackGround Color>') != -1):
                LocalbgColor = workbook.add_format({'bold': True,
                                                'border': 1,
                                                'align': 'center',
                                                'valign': 'vbottom'})
                serverbgColor = workbook.add_format({'bold': True,
                                                'border': 1,
                                                'align': 'center',
                                                'valign': 'vbottom'})

                if(self.errInfoDic[appId][LOCAL_BG_COLOR] == 'X'
                    or self.errInfoDic[appId][LOCAL_BG_COLOR] == ''):
                    LocalbgColor.set_bg_color('#ffffff')
                else:
                    LocalbgColor.set_bg_color(self.errInfoDic[appId][LOCAL_BG_COLOR])
                    fontColor = self.convertBGColor(self.errInfoDic[appId][LOCAL_BG_COLOR])
                    LocalbgColor.set_font_color(fontColor)

                if(self.errInfoDic[appId][SERVER_BG_COLOR] == 'X'
                    or self.errInfoDic[appId][SERVER_BG_COLOR] == ''):
                    serverbgColor.set_bg_color('#ffffff')
                else:
                    serverbgColor.set_bg_color(self.errInfoDic[appId][SERVER_BG_COLOR])
                    fontColor = self.convertBGColor(self.errInfoDic[appId][SERVER_BG_COLOR])
                    serverbgColor.set_font_color(fontColor)

                worksheet.write('D'+str(row_num), self.errInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
                worksheet.write('E'+str(row_num), self.errInfoDic[appId][SERVER_BG_COLOR],serverbgColor)
                worksheet.write('F'+str(row_num), self.errInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
                worksheet.write('G'+str(row_num), self.errInfoDic[appId][SERVER_BG_COLOR],serverbgColor)

            if(errType.find('<Title>') != -1):
                worksheet.write('H'+str(row_num), self.errInfoDic[appId][LOCAL_TITLE],text_style)
                worksheet.write('I'+str(row_num), self.errInfoDic[appId][SERVER_TITLE],text_style)
            else:
                worksheet.write('H'+str(row_num), 'Same',sameCell)
                worksheet.write('I'+str(row_num), 'Same',sameCell)

            if(errType.find('<Large Icon>') != -1):
                local_image_data = None
                server_image_data = None

                local_image_data = self.get_resized_image_data(self.errIconList[LOCAL_LARGE_ICON][appId])
                worksheet.insert_image('D'+str(row_num),
                                        self.errIconList[LOCAL_LARGE_ICON][appId],
                                        {'x_offset': 30, 'y_offset': 20,
                                        'image_data': local_image_data})

                server_image_data = self.get_resized_image_data(self.errIconList[SERVER_LARGE_ICON][appId])
                worksheet.insert_image('E'+str(row_num),
                                        self.errIconList[SERVER_LARGE_ICON][appId],
                                        {'x_offset': 30, 'y_offset': 20,
                                        'image_data': server_image_data})

                # worksheet.insert_image('C'+str(row_num), self.errIconList[LOCAL_LARGE_ICON][appId])#,{'x_scale': x_scale, 'y_scale': y_scale,'x_offset': 10, 'y_offset': 10})
                # worksheet.insert_image('D'+str(row_num), self.errIconList[SERVER_LARGE_ICON][appId])#,{'x_scale': x_scale, 'y_scale': y_scale,'x_offset': 10, 'y_offset': 10})
            else:
                if(errType.find('<BackGround Color>') != -1):
                    worksheet.write('D'+str(row_num), 'Same\n\n'+self.errInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
                    worksheet.write('E'+str(row_num), 'Same\n\n'+self.errInfoDic[appId][SERVER_BG_COLOR],serverbgColor)
                else:
                    worksheet.write('D'+str(row_num), 'Same',sameCell)
                    worksheet.write('E'+str(row_num), 'Same',sameCell)

            if(errType.find('<Small Icon>') != -1):
                local_image_data = None
                server_image_data = None

                local_image_data = self.get_resized_image_data(self.errIconList[LOCAL_SMALL_ICON][appId])
                worksheet.insert_image('F'+str(row_num),
                                        self.errIconList[LOCAL_SMALL_ICON][appId],
                                        {'x_offset': 30, 'y_offset': 20,
                                        'image_data': local_image_data})

                server_image_data = self.get_resized_image_data(self.errIconList[SERVER_SMALL_ICON][appId])
                worksheet.insert_image('G'+str(row_num),
                                        self.errIconList[SERVER_SMALL_ICON][appId],
                                        {'x_offset': 30, 'y_offset': 20,
                                        'image_data': server_image_data})
            else:
                if(errType.find('<BackGround Color>') != -1):
                    worksheet.write('F'+str(row_num), 'Same\n\n'+self.errInfoDic[appId][LOCAL_BG_COLOR],LocalbgColor)
                    worksheet.write('G'+str(row_num), 'Same\n\n'+self.errInfoDic[appId][SERVER_BG_COLOR],serverbgColor)
                else:
                    worksheet.write('F'+str(row_num), 'Same',sameCell)
                    worksheet.write('G'+str(row_num), 'Same',sameCell)

            row_num = row_num + 1

    def convertBGColor(self,bgColor):
        newColor = bgColor.replace('#','')
        if(ord(newColor[0]) > 47 and ord(newColor[0])<58):
            newColor = '#FFFFFF'
        else:
            newColor = '#000000'
        return newColor

    def get_resized_image_data(self,file_path):
        bound_width_height = (70, 70)
        # get the image and resize it
        im = Image.open(file_path)
        im.thumbnail(bound_width_height, Image.ANTIALIAS)  # ANTIALIAS is important if shrinking

        # stuff the image data into a bytestream that excel can read
        im_bytes = io.BytesIO()
        im.save(im_bytes, format='PNG')
        return im_bytes

    def getCountryName(self,workbook,appID):
        country = ''
        for sheet in workbook.sheets():
            for num in range(len(sheet.col_values(9))):
                if(sheet.col_values(9)[num] == appID and sheet.col_values(5)[num] != '-'):
                    country += str(sheet.col_values(3)[num])+'/'

        return country

    def getCountryGroupListForAppID(self):
        atscList = []
        dvbList = []
        aribList = []
        allList = []

        atscFlag = False
        dvbFlag = False
        aribFlag = False
        with open(self.resPath+'\\CMakeLists.txt', 'r') as f:
            cmList = f.readlines()

            for num in range(len(cmList)):
                if(cmList[num] == '\n'):
                    atscFlag = False
                    dvbFlag = False
                    aribFlag = False

                if(atscFlag == True):
                    appID = cmList[num].replace("    ","")
                    appID = appID.replace("\n","")
                    if(appID.find(')') != -1):
                        appID = appID.replace(")","")

                    atscList.append(appID)
                elif(dvbFlag == True):
                    appID = cmList[num].replace("    ","")
                    appID = appID.replace("\n","")
                    if(appID.find(')') != -1):
                        appID = appID.replace(")","")

                    dvbList.append(appID)
                elif(aribFlag == True):
                    appID = cmList[num].replace("    ","")
                    appID = appID.replace("\n","")
                    if(appID.find(')') != -1):
                        appID = appID.replace(")","")

                    aribList.append(appID)
                else:
                    pass


                if(cmList[num] == 'set(ATSC_CP_LISTS\n'):
                    atscFlag = True
                elif(cmList[num] == 'set(DVB_CP_LISTS\n'):
                    dvbFlag = True
                elif(cmList[num] == 'set(ARIB_CP_LISTS\n'):
                    aribFlag = True
                else:
                    pass
        allList.append(atscList)
        allList.append(dvbList)
        allList.append(aribList)

        return allList
