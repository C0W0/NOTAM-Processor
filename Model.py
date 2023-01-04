import sys
sys.path.append(f'{sys.path[0]}\\data_set')

from data_set.Process_Data import NotamDataSet, Decoder
from torch.utils.data import DataLoader
from torch import float32
import torch
import random

GPU = torch.device(0)

decoder = Decoder()
dataset = NotamDataSet()

inputSize = dataset.n_features
outputSize = dataset.n_categories

dataLoader = DataLoader(dataset=dataset, batch_size=8, shuffle=True)

for x, y in dataLoader:
    print(x,y)
