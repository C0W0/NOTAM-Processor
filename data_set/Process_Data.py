import csv
import torch
from torch.utils.data import Dataset
import json
from Merge_Sort import MergeSort
import numpy as np
import random

class Decoder:
    def __init__(self) -> None:
        categoricalJson = open(file='data_set/category.json', mode='r')
        categories:dict[str, list[int]] = json.load(categoricalJson)

        typeCount = len(categories)
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
        maxVal, maxI = 0.0, 0
        
        for i in range(len(vec)):
            val = vec[i]
            if(val > maxVal):
                maxVal = val
                maxI = i
                
        return self.decodeArr[maxI]

    def match(self, vec1: torch.Tensor, vec2: torch.Tensor) -> bool:
        maxVal = 0.0
        maxI1 = 0
        for i in range(len(vec1)):
            val = vec1[i]
            if(val > maxVal):
                maxVal = val
                maxI1 = i
        
        maxVal = 0.0
        maxI2 = 0
        for i in range(len(vec2)):
            val = vec2[i]
            if(val > maxVal):
                maxVal = val
                maxI2 = i
        
        return maxI1 == maxI2
        

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
            if(not info['Include']):
                continue
            
            X = [float(num) for num in pos.split(',')]

            rockets:list = info['Rocket']
            rocketsCount = len(rockets)
            Y:np.ndarray = np.zeros(len(categories[rockets[0]]))
            
            for r in rockets:
                Y += np.array(categories[r])
            
            Y /= rocketsCount

            for _ in range(rocketsCount):
                xSet.append(X)
                ySet.append(Y.tolist())
            
        dataSetJson.close()
        categoricalJson.close()
        
        device = torch.device(0)
        
        self.x = torch.tensor(xSet, dtype=torch.float32, device=device)
        self.xMin = self.x.min()
        self.x -= self.xMin
        self.xMax = self.x.max()
        self.x /= self.xMax
        
        self.y = torch.tensor(ySet, dtype=torch.float32, device=device)
        self.n_sample = len(xSet)
        
        self.n_features = len(xSet[0])
        self.n_categories = len(ySet[0])
        
    def __getitem__(self, index) -> tuple[torch.Tensor, torch.Tensor]:
        return self.x[index], self.y[index]
    
    def __len__(self):
        return self.n_sample
    
    def normalize(self, x: torch.Tensor) -> torch.Tensor:
        x -= self.xMin
        x /= self.xMax
        return x
        

def get_categories():
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    categoricalJson = open(file='data_set/category.json', mode='w+')

    dataSet = csv.DictReader(historyData)

    rocketCount = {}
    for entry in dataSet:
        rocket = entry['Rocket']

        if(not rocket in rocketCount):
            rocketCount[rocket] = 1
        else:
            rocketCount[rocket] += 1
    
    rockets = []
    for r, count in rocketCount.items():
        if(count > 3):
            rockets.append(r)

    rockets = MergeSort(rockets)

    categorized = {}
    rCount = len(rockets)

    for i in range(rCount):
        r = rockets[i]
        cateVector = [0]*rCount
        cateVector[i] = 1
        categorized[r] = cateVector
    
    # lsCate = {'JSLC': 0, 'TSLC': 1, 'XSLC': 2, 'WSLS': 3, 'Yellow Sea': 4}
    # for (ls, i) in lsCate.items():
    #     cateVector = [0]*5
    #     cateVector[i] = 1
    #     categorized[ls] = cateVector

    json.dump(categorized, categoricalJson)

    historyData.close()
    categoricalJson.close()


def clean_data():
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    dataJson = open(file='data_set/dataset.json', mode='w+')
    categoryJson = open(file='data_set/category.json', mode='r')

    dataSetRaw = csv.DictReader(historyData)
    categories = json.load(categoryJson)
    locations = {}
    posByRocket: dict[str, list[str]] = {}
    
    for entry in dataSetRaw:
        ls = entry['Launch Site']
        r = entry['Rocket']
        
        for i in range(1,6):
            notam = entry[f'NOTAM {i}'].strip()
            
            if(notam == ''):
                continue

            isDataUsed = r in categories

            if(notam in locations):
                if(locations[notam]['Include'] and isDataUsed):
                    locations[notam]['Rocket'].append(r)
                    posByRocket[r].append(notam)
                    continue
                else:
                    notam += ' '
            
            posData = {}
            posData['Launch Site'] = ls
            posData['Rocket'] = [r]
            
            posData['Include'] = isDataUsed
            
            locations[notam] = posData
            
            if(isDataUsed):
                if(not r in posByRocket): posByRocket[r] = []
                posByRocket[r].append(notam)
        
    maxLen = 0
    for _, notamList in posByRocket.items():
        maxLen = max(maxLen, len(notamList))
    
    for r, notamList in posByRocket.items():
        duplicateNum = maxLen - len(notamList)
        duplicateSet = get_random_subset(notamList, duplicateNum, locations)
        
        for pos in duplicateSet:
            locations[pos]['Rocket'].append(r)
    
    json.dump(locations, dataJson)
    dataJson.close()
    historyData.close()


def get_random_subset(sourceSet: list, subsetSize: int, mainDataSet: dict = {}) -> list:
    subset = []
    setSize = len(sourceSet)
    for _ in range(subsetSize):
        duplicate = sourceSet[int(random.random()*setSize)]
            
        subset.append(duplicate)
    
    return subset
