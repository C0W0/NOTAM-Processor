import csv
import torch
from torch.utils.data import Dataset
import json
from Merge_Sort import MergeSort

class Decoder:
    def __init__(self) -> None:
        categoricalJson = open(file='data_set/category.json', mode='r')
        categories:dict[str, list[int]] = json.load(categoricalJson)

        typeCount = len(categories)-5 # ignore launch sites
        self.decodeArr = ['']*typeCount

        for rocket, vec in categories.items():
            # ignore launch sites
            vecSize = len(vec)
            if(vecSize <= 5):
                break

            for i in range(vecSize):
                if(vec[i] == 1):
                    self.decodeArr[i] = rocket
                    break

        categoricalJson.close()
    
    def __call__(self, vec: list[float]) -> str:
        for i in range(len(vec)):
            if(vec[i] == 1):
                return self.decodeArr[i]
        return ''

class NotamDataSet(Dataset):
    def __init__(self) -> None:
        super().__init__()
        
        dataSetJson = open(file='data_set/dataset.json', mode='r')
        categoricalJson = open(file='data_set/category.json', mode='r')

        dataSet:dict = json.load(dataSetJson)
        categories:dict = json.load(categoricalJson)

        xSet = []
        ySet = []

        for pos, info in dataSet.items():
            X = [float(num) for num in pos.split(',')]

            r = info['Rocket']
            Y = categories[r]

            xSet.append(X)
            ySet.append(Y)
            
        dataSetJson.close()
        categoricalJson.close()
        
        device = torch.device(0)
        
        self.x = torch.tensor(xSet, dtype=torch.float32, device=device)
        self.y = torch.tensor(ySet, dtype=torch.float32, device=device)
        self.n_sample = len(xSet)
        
        self.n_features = len(xSet[0])
        self.n_categories = len(ySet[0])
        
    def __getitem__(self, index) -> tuple[torch.Tensor, torch.Tensor]:
        return self.x[index], self.y[index]
    
    def __len__(self):
        return self.n_sample
        

def get_categories():
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    categoricalJson = open(file='data_set/category.json', mode='w+')

    dataSet = csv.DictReader(historyData)

    rockets = []
    for entry in dataSet:
        rocket = entry['Rocket']

        if(not rocket in rockets):
            rockets.append(rocket)

    rockets = MergeSort(rockets)

    categorized = {}
    rCount = len(rockets)

    for i in range(rCount):
        r = rockets[i]
        cateVector = [0]*rCount
        cateVector[i] = 1
        categorized[r] = cateVector
    
    lsCate = {'JSLC': 0, 'TSLC': 1, 'XSLC': 2, 'WSLS': 3, 'Yellow Sea': 4}
    for (ls, i) in lsCate.items():
        cateVector = [0]*5
        cateVector[i] = 1
        categorized[ls] = cateVector

    json.dump(categorized, categoricalJson)

    historyData.close()
    categoricalJson.close()


def clean_data():
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    dataJson = open(file='data_set/dataset.json', mode='w+')

    dataSetRaw = csv.DictReader(historyData)
    locations = {}

    for entry in dataSetRaw:
        ls = entry['Launch Site']
        r = entry['Rocket']
        
        for i in range(1,6):
            notam = entry[f'NOTAM {i}']

            if(not notam.strip() == ''):
                posData = {}
                posData['Launch Site'] = ls
                posData['Rocket'] = r
                locations[notam] = posData
    
    json.dump(locations, dataJson)
    dataJson.close()
    historyData.close()