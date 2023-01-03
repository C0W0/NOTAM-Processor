import requests
import json
import math
from Scraper import firDomestic, firInt, launchZones, keyWords, months, AirClosure

URL = 'https://notams.aim.faa.gov/notamSearch/search'
ARCHIVE_DATE = '2020-12-05'
LAUNCH_SITE = 'XSLC'

def main():
    jsonFile = open(file='payloads.json', mode='r')
    jsonParsed = json.load(jsonFile)['params']
    jsonFile.close()

    params = {}

    for entry in jsonParsed:
        params[entry['name']] = entry['value']

    params['archiveDate'] = ARCHIVE_DATE
    notamsParsed = []

    firList = launchZones[LAUNCH_SITE]
    count = len(firList)

    print('Fetching info...')
    print(f'[{" "*50}]', end='\r')
    for i in range(count):
        fir = firList[i]
        params['archiveDesignator'] = fir

        response = requests.post(url=URL, params=params)

        notamsRaw: list[dict[str, str]] = response.json()['notamList']
        for entry in notamsRaw:
            message = entry['icaoMessage'].replace('\n', ' ')

            isInfoRelevant = False
            for keyword in keyWords:
                if(keyword in message):
                    isInfoRelevant = True
                    break

            if(not isInfoRelevant):
                continue

            dateStart = reformatDate(entry['startDate'])
            dateEnd = reformatDate(entry['endDate'])

            notamFull = f'{message} {dateStart} UNTIL {dateEnd}'
            notamsParsed.append(notamFull)
    
        progress = math.ceil(50*i/count)
        print(f'[{"="*progress}>{" "*(49-progress)}]', end='\r')

    print()
    resultFile = open('Historical_Data_P.txt', mode='w')

    for info in notamsParsed:
        closure = AirClosure(info)
        resultFile.write(f'{closure.source}\n')
        resultFile.write(f'Date: {closure.startDate}~{closure.endDate}\n')
        resultFile.write(f'Location: {closure.position}\n')
        resultFile.write('\n')
        print("From the source NOTAM: "+closure.source)
        print("Date: "+str(closure.startDate)+"~"+str(closure.endDate))
        print("Position: "+str(closure.position))
        print()
    
# MM/dd/yyyy hhmm -> dd MMM hh:mm yyyy
def reformatDate(dateRaw: str) -> str:
    tokens = dateRaw.split(' ')
    daysRaw = tokens[0]
    daysToken = daysRaw.split('/')
    month = daysToken[0]
    day = daysToken[1]
    year = daysToken[2]

    timeRaw = tokens[1]
    time = timeRaw[:2]+':'+timeRaw[2:]

    return f'{day} {months[int(month)]} {time} {year}'

if(__name__ == '__main__' ):
    main()
    

