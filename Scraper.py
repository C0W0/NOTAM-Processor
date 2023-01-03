import math
from sqlite3 import Date
import mechanize
import mechanize._http
import http.cookiejar
import html.parser
import re

#constants
READFILE = False
WRITEFILE = False
CONCISE_MODE = True
keyWords = ['A TEMPORARY RESTRICTED AREA', 'A TEMPORARY DANGER AREA', 'TEMPO DANGER AREA', 'AERO SPACE FLT', 'AEROSPACE', 'SFC-UNL']
months = {1:'JAN', 2:'FEB', 3:'MAR', 4:'APR', 5:'MAY', 6:'JUN', 7:'JUL', 8:'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}
firDomestic = {'Lanzhou': 'ZLHW', 'Kunming': 'ZPKM', 'Wuhan': 'ZHWH', 'GuangZhou': 'ZGZU', 'Shanghai': 'ZSHA', 'Beijing': 'ZBPE', 'Shanghai': 'ZSHA', 'Sanya': 'ZJSA', 'Hongkong': 'VHHK'}
firInt = {'Yangon': 'VYYF', 'Chennai': 'VOMF', 'Melbourne': 'YMMM', 'Fukuoka': 'RJJJ', 'Ho-Chi-Minh': 'VVHM', 'Hanoi': 'VVHN', 'Colombo': 'VCCF', 'Manila': 'RPHI', 
            'Oakland': 'KZAK', 'Brisbane': 'YBBB', 'InCheon': 'RKRR', 'Nadi': 'NFFF'}
launchZones = {
    'JSLC': [firDomestic['Lanzhou'], firDomestic['Wuhan'], firDomestic['Shanghai'], firDomestic['Kunming'], firInt['Yangon'], firInt['Chennai'], firInt['Colombo'], firInt['Melbourne'], firInt['Brisbane'], firInt['Manila'], firDomestic['Hongkong']],
    'XSLC': [firDomestic['Kunming'], firDomestic['GuangZhou'], firDomestic['Sanya'], firInt['Fukuoka'], firInt['Nadi']],
    'TSLC': [firDomestic['Beijing'], firDomestic['Lanzhou'], firDomestic['Wuhan'], firDomestic['Kunming'], firInt['Ho-Chi-Minh'], firInt['Hanoi'], firInt['Melbourne']],
    'WSLS': [firDomestic['Sanya'], firInt['Manila'], firInt['Oakland'], firInt['Ho-Chi-Minh']],
    'Yellow Sea': [firDomestic['Shanghai'], firInt['InCheon'], firInt['Manila'], firInt['Nadi'], firInt['Fukuoka'], firInt['Brisbane']]
}

class NotamRetriever:
    def __init__(self):
        #Browser
        self.br = mechanize.Browser()

        #Cookie Jar
        cj = http.cookiejar.LWPCookieJar()
        self.br.set_cookiejar(cj)

        #setting
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.set_handle_refresh(mechanize._http.HTTPRefererProcessor(), max_time=1)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    def get_notam_raw(self, fir):
        #open site
        self.br.open('https://www.notams.faa.gov/dinsQueryWeb/')

        #input fir
        self.br.select_form(nr=0)
        self.br.form['retrieveLocId']=fir
        self.br.submit()

        #read website
        info = str(self.br.response().read())
        info = info.replace('\\t', ' ')
        info = info.replace('\\n', ' ')
        return info

#html parser
class MyHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.dataSet = []
    
    # def is_matched(self, string):
    #     return bool(re.match('A[0-9]+', string))
    
    def handle_data(self, data):
        self.append_data(data)
    
    def append_data(self, data):
        dataStr = (str(data)).strip()
        if(dataStr.startswith("- ")):
            self.dataSet.append(dataStr)
        # else:
        #     print("invalid: '"+dataStr+"'")

    def clear_data(self):
        self.dataSet = []

#process NOTAM into airclosure
class AirClosure:
    def __init__(self, notamCorrected):
        self.source = notamCorrected
        closure = notamCorrected.split("CREATED")[0]

        dates = re.findall('\d{2}\s[A-Z]{3}\s\d{2}:\d{2}\s\d{4}', closure)
        self.startDate = self.parse_date(dates[0].split(" "))
        self.endDate = self.parse_date(dates[1].split(" "))

        percisionL: int = 0
        # format 1 (e.g. N165049E0933636)
        poses = re.findall('[NS]\d{6}[EW]\d{7}', closure)
        percisionL = 6

        # format 2 (e.g. N3754E09916)
        if(len(poses) == 0):
            poses = re.findall('[NS]\d{4}[EW]\d{5}', closure)
            percisionL = 4

        # format 3 (e.g. S303437 E0843459 / S22 53 00 E163 20 00)
        if(len(poses) == 0):
            poses = re.findall('[NS]\d{6} [EW]\d{7}', closure)
            if(len(poses) == 0):
                poses = re.findall('[NS]\d{2} \d{2} \d{2} [EW]\d{3} \d{2} \d{2}', closure)
            for i in range(0, len(poses)):
                poses[i] = poses[i].replace(' ', '')
            percisionL = 6

        # format 4 (e.g. 191727N1071251E / 184400N 1240300E)
        if(len(poses) == 0):
            poses = re.findall('\d{6}[NS]\d{7}[EW]', closure)
            if(len(poses) == 0):
                poses = re.findall('\d{6}[NS] \d{7}[EW]', closure)
                
            for i in range(0, len(poses)):
                pos: str = poses[i].replace(' ', '')
                poses[i] = pos[6] + pos[0:6] + pos[14] + pos[7:14]
            percisionL = 6

        # format 5 (e.g. 0244N09052E / 3910S 09508E)
        if(len(poses) == 0):
            poses = re.findall('\d{4}[NS]\d{5}[EW]', closure)
            if(len(poses) == 0):
                poses = re.findall('\d{4}[NS] \d{5}[EW]', closure)

            for i in range(0, len(poses)):
                pos: str = poses[i].replace(' ', '')
                poses[i] = pos[4] + pos[0:4] + pos[10] + pos[5:10]
            percisionL = 4
        
        # format 7 (e.g. 16 56 00N 118 58 00E)
        if(len(poses) == 0):
            poses = re.findall('\d{2} \d{2} \d{2}[NS] \d{3} \d{2} \d{2}[EW]', closure)
            for i in range(0, len(poses)):
                pos: str = poses[i].replace(' ', '')
                poses[i] = pos[6] + pos[0:6] + pos[14] + pos[7:14]
            percisionL = 6

        # format 8 (e.g. S0818 E09017)
        if(len(poses) == 0):
            poses = re.findall('[NS]\d{4} [EW]\d{5}', closure)
            for i in range(0, len(poses)):
                poses[i] = poses[i].replace(' ', '')
            percisionL = 4
        
        xPos = 0.0
        yPos = 0.0

        for p in poses:
            yCoord = int(p[1:1+percisionL])
            if(p[0] == 'S'): yCoord = -yCoord
            yPos += yCoord
            xCoord = int(p[2+percisionL:])
            if(p[1+percisionL] == 'W'): xCoord = -xCoord
            xPos += xCoord


        if(len(poses) > 0):
            xPos /= len(poses)
            yPos /= len(poses)
        # else:
        #     raise ValueError('FormatNotSupportError: '+self.source)

        corrFactor: float = math.pow(10, percisionL-2)
        self.position = (yPos/corrFactor, xPos/corrFactor)

    def parse_date(self, tokens):
        month = 0
        for i in range (1,13):
            if(months[i] == tokens[1]):
                month = i
                break
        return Date(int(tokens[3]), month, int(tokens[0]))

    def __eq__(self, other):
        return (self.position == other.position) and (self.endDate == other.endDate) and (self.startDate == other.startDate)

def get_notam_single_site():
    notamTool = NotamRetriever()
    myParser = MyHTMLParser()

    selections = ['', 'JSLC', 'XSLC', 'TSLC', 'WSLS', 'Yellow Sea']
    for i in range(1, len(selections)):
        print(str(i)+': ' + selections[i], end=' ')
    print()
    launchComplex = selections[int(input())]
    print('loading NOTAM...')
    print()

    #get and parse info
    notamList = []
    for e in launchZones[launchComplex]:
        info = ''

        if(READFILE):
            f = open(e+'.txt', 'r')
            info = f.read()
            f.close()
        else:
            info = notamTool.get_notam_raw(e)
            if(WRITEFILE):
                f = open(e+'.txt', 'w')
                f.write(info)
                f.close

        myParser.clear_data()
        myParser.feed(info)
        notamList.append((e, myParser.dataSet))
    
    return notamList

def get_all_notams():
    notamTool = NotamRetriever()
    myParser = MyHTMLParser()

    allFir = []
    allFir.extend(firDomestic.values())
    allFir.extend(firInt.values())
    
    notamList = []

    print('Fetching info...')
    print(f'[{" "*50}]', end='\r')

    count = len(allFir)
    for i in range(count):
        fir = allFir[i]
        info = notamTool.get_notam_raw(fir)

        myParser.clear_data()
        myParser.feed(info)

        notamList.append((fir, myParser.dataSet))
        
        progress = int(50*i/count)
        print(f'[{"="*progress}>{" "*(49-progress)}]', end='\r')
    print()

    return notamList

def main():
    notamList: list[tuple] = get_all_notams()

    #find air closure
    matchList = []
    for pair in notamList:
        for info in pair[1]:
            for w in keyWords:
                if(w in info): matchList.append((pair[0], info))

    #pre-process the NOTAM to retrieve date
    for i in range(0, len(matchList)):
        for m in months.values():
            matchList[i] = (matchList[i][0], matchList[i][1].replace(m, " "+m+" ", -1).replace("  ", " ", -1))
        matchList[i] = (matchList[i][0], matchList[i][1].replace("UNTIL", " UNTIL ", -1).replace("  ", " ", -1))
        # print(matchList[i])

    #process the NOTAM
    closures: list[AirClosure] = []
    regions = []
    for n in matchList:
        closure = AirClosure(n[1])
        if(not closure in closures): 
            closures.append(closure)
            regions.append(n[0])

    for i in range(len(closures)):
        c = closures[i]

        if(CONCISE_MODE):
            print(regions[i])
        else:
            print(f"{regions[i]} {c.source}")
        
        print(f"Date: {c.startDate}~{c.endDate}")
        print(f"Position: {c.position}")
        print()

if(__name__ == '__main__' ):
    main()