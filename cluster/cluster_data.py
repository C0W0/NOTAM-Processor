import csv
import json
import random
import numpy as np


def k_means_cluster_data(k: int):
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    dataSetRaw = csv.DictReader(historyData)
    
    pointsStr = []
    points = []
    pointsData = []
    
    for entry in dataSetRaw:
        ls = entry['Launch Site']
        r = entry['Rocket']
        
        for i in range(1,6):
            notam = entry[f'NOTAM {i}'].strip()
            
            if(notam == ''):
                continue
            
            pointsStr.append(notam)
            points.append(np.array([float(num) for num in notam.split(',')]))
            
            posData = {}
            posData['Rocket'] = r
            posData['Launch Site'] = ls
            
            pointsData.append(posData)
    
    historyData.close()
    
    points = np.array(points)
    pointsData = np.array(pointsData)
    
    choices = np.random.choice(points.shape[0], k, replace=False)
    centersStr = []
    centers = []
    for c in choices:
        ptStr = pointsStr[c]
        
        while ptStr in centersStr:
            c = int(random.random()*len(pointsStr))
            ptStr = pointsStr[c]
            
        centersStr.append(ptStr)
        centers.append(points[c])
    
    centers = np.array(centers)
    
    shouldLoop = True
    while shouldLoop:
        distances = []
        
        for c in centers:
            distance = np.linalg.norm((points-c)**2, axis=1)
            distances.append(distance)
        
        distances = np.array(distances)
        labels: np.ndarray = np.argmin(distances, axis=0)
        
        newCenters = np.array([points[labels == i].mean(axis=0) for i in range(k)])
        
        shouldLoop = not np.allclose(centers, newCenters)
        centers = newCenters
        
    clusters = {}    
    clusterJson = open('cluster/clusters.json', mode='w+')
    rocketsJson = open(file='cluster/rockets.json', mode='r')
    launchSitesJson = open(file='cluster/launch_sites.json', mode='r')
    
    rocketsCategorized = json.load(rocketsJson)
    lsCategorized = json.load(launchSitesJson)
    
    for i in range(k):
        allPoints: np.ndarray = points[labels == i]
        centre:np.ndarray = allPoints.mean(axis=0)
        allData: np.ndarray = pointsData[labels == i]
        
        data = {}
        data['Centre'] = centre.tolist()
        
        allInfo: list[dict[str, str]] = allData.tolist()
        rocketArr = np.zeros(len(rocketsCategorized[allInfo[0]['Rocket']]))
        lsArr = np.zeros(5)
        
        for info in allInfo:
            rocketArr += np.array(rocketsCategorized[info['Rocket']])
            lsArr += np.array(lsCategorized[info['Launch Site']])
        
        rocketArr = (rocketArr/len(allInfo)).tolist()
        lsArr = (lsArr/len(allInfo)).tolist()
        
        data['Rocket'] = rocketArr
        data['Launch Site'] = lsArr
        
        data['Raw Data'] = allInfo
        
        clusters[f'Cluster {i}'] = data
    
    json.dump(clusters, clusterJson)
    clusterJson.close()
    rocketsJson.close()
    launchSitesJson.close()
    

def get_categories():
    historyData = open(file='data_set/Historical NOTAMs - data.csv', mode='r')
    rocketsJson = open(file='cluster/rockets.json', mode='w+')
    launchSitesJson = open(file='cluster/launch_sites.json', mode='w+')

    dataSet = csv.DictReader(historyData)

    categorized = {}
    rockets = []
    
    for entry in dataSet:
        rocket = entry['Rocket']

        if(not rocket in rockets):
            rockets.append(rocket)

    rockets = sorted(rockets)

    rCount = len(rockets)

    for i in range(rCount):
        r = rockets[i]
        cateVector = [0]*rCount
        cateVector[i] = 1
        categorized[r] = cateVector
    
    lsCate = {'JSLC': 0, 'TSLC': 1, 'XSLC': 2, 'WSLS': 3, 'Yellow Sea': 4}
    lsCategorized = {}
    for (ls, i) in lsCate.items():
        cateVector = [0]*5
        cateVector[i] = 1
        lsCategorized[ls] = cateVector

    json.dump(categorized, rocketsJson)
    json.dump(lsCategorized, launchSitesJson)

    historyData.close()
    rocketsJson.close()
    launchSitesJson.close()