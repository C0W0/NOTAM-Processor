from Scraper import AirClosure

# from Scraper import AirClosure

months = {1:'JAN', 2:'FEB', 3:'MAR', 4:'APR', 5:'MAY', 6:'JUN', 7:'JUL', 8:'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}

def import_notam():
    f = open('Import_NOTAM.txt', 'r')
    infosRaw = f.read().split('>-*-<')
    f.close()

    infosProcessed: list[str] = []
    for s in infosRaw:
        info: str = s.replace('\\t', ' ')
        info = info.replace('\\n', ' ')
        if(info):
            infosProcessed.append(info)

    for info in infosProcessed:
        closure = AirClosure(info)
        # print("From the source NOTAM: "+closure.source)
        print("Date: "+str(closure.startDate)+"~"+str(closure.endDate))
        print("Position: "+str(closure.position))
        print()

def test():
    k = 345635
    for i in range(k):
        progress = int(50*i/k)
        bar = f'[{"="*progress}>{" "*(49-progress)}]'
        print(bar, end='\r')
    print()

if(__name__ == '__main__' ):
    import_notam()

