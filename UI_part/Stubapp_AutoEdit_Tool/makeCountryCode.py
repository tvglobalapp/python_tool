import shutil
import os, glob
import re
import copy
from xml.etree import ElementTree

class makeCountryCodeList():
    def __init__(self):
        self.tree = ElementTree.parse("resources\country_codes_v5.xml")
        self.root = self.tree.getroot()
        self.atscList = []
        self.dvbList = []
        self.aribList = []

        for group in self.root.getchildren():
            code = group.get('code')
            # print("country group : ",code)
            for country in group.getchildren():
                code3 = country.get('code3')
                if code == 'EU' or code == 'AJ' or code == 'JA' \
                    or code == 'CS' or code == 'TW' or code == 'CO' \
                    or code == 'CN' or code == 'HK' or code == 'IL' \
                    or code == 'PA' or code == 'IR':
                    self.dvbList.append(code3)
                    # if 'DVB' in self.countryList:
                    #     self.countryList['DVB'].append(code3)
                    # else:
                    #     self.countryList['DVB'] = [code3]
                elif code == 'JP':
                    self.aribList.append(code3)
                    # if 'ARIB' in self.countryList:
                    #     self.countryList['ARIB'].append(code3)
                    # else:
                    #     self.countryList['ARIB'] = [code3]
                else:
                    self.atscList.append(code3)
                    # if 'ATSC' in self.countryList:
                    #     self.countryList['ATSC'].append(code3)
                    # else:
                    #     self.countryList['ATSC'] = [code3]


        self.dvbList = list(set(self.dvbList))
        self.aribList = list(set(self.aribList))
        self.atscList = list(set(self.atscList))
        # self.countryList['DVB'] = list(set(countryList['DVB']))
        # self.countryList['ARIB'] = list(set(countryList['ARIB']))
        # self.countryList['ATSC'] = list(set(countryList['ATSC']))
