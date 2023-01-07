import sys
sys.path.append(f'{sys.path[0]}\\data_set')

from data_set.Process_Data import NotamDataSet, Decoder
from torch.utils.data import DataLoader
from torch import float32
import torch

GPU = torch.device(0)

decoder = Decoder()
dataset = NotamDataSet()

print(len(dataset))

inputSize = dataset.n_features
hiddenSize = 16
outputSize = dataset.n_categories

# linear layer 1
w1 = torch.rand((hiddenSize*2, inputSize), dtype=float32, requires_grad=True, device=GPU)
b1 = torch.rand((hiddenSize*2, 1), dtype=float32, requires_grad=True, device=GPU)
# linear layer 2
w2 = torch.rand((hiddenSize, hiddenSize*2), dtype=float32, requires_grad=True, device=GPU)
b2 = torch.rand((hiddenSize, 1), dtype=float32, requires_grad=True, device=GPU)
# linear layer 3
# w3 = torch.rand((hiddenSize, hiddenSize), dtype=float32, requires_grad=True, device=GPU)
# b3 = torch.rand((hiddenSize, 1), dtype=float32, requires_grad=True, device=GPU)
# output layer
w4 = torch.rand((outputSize, hiddenSize), dtype=float32, requires_grad=True, device=GPU)
b4 = torch.rand((outputSize, 1), dtype=float32, requires_grad=True, device=GPU)

lr = torch.tensor([0.1], dtype=float32, device=GPU)

def forward(X: torch.Tensor) -> torch.Tensor:
    a1 = (w1.mm(X)+b1).relu()
    a2 = (w2.mm(a1)+b2).relu()
    # a3 = (w3.mm(a2)+b3).relu()
    n = (w4.mm(a2)+b4)
    n1 = n-n.min()
    z = n1/n1.max()
    a4 = z
    return a4
    
dataLoader = DataLoader(dataset=dataset, batch_size=16, shuffle=True)

for epoch in range(5000):
    x: torch.Tensor
    y: torch.Tensor
    for x, y in dataLoader:
        X = x.transpose(0, 1)
        Y = y.transpose(0, 1)
        
        Y_Pre = forward(X)
        
        loss = torch.nn.CrossEntropyLoss()
        l = loss.forward(Y_Pre, Y)
        # loss = ((Y_Pre-Y)**2).mean()
        l.backward()
        
        with torch.no_grad():
            w1 -= w1.grad*lr
            w2 -= w2.grad*lr
            # w3 -= w3.grad*lr
            w4 -= w4.grad*lr
            b1 -= b1.grad*lr
            b2 -= b2.grad*lr
            # b3 -= b3.grad*lr
            b4 -= b4.grad*lr
        
        w1.grad.zero_()
        w2.grad.zero_()
        # w3.grad.zero_()
        w4.grad.zero_()
        b1.grad.zero_()
        b2.grad.zero_()
        # b3.grad.zero_()
        b4.grad.zero_()
    
    if(not epoch%100 == 0):
        continue
    
    with torch.no_grad():
        correctCount = 0
        for x, y in dataLoader:
            X = x.transpose(0, 1)
            
            Y_Pre = forward(X).transpose(0, 1)
            types = {}
            
            for preResult, dataResult in zip(Y_Pre, y):
                resultStr = decoder(preResult)
                types[resultStr] = 0
                if(decoder.match(preResult, dataResult)):
                    correctCount += 1
                # else:
                    # print(preResult, resultStr, decoder(dataResult), len(types))
            
    print(f'epoch: {epoch}; accuracy: {correctCount}/{len(dataset)}')
        

strInput = input('enter coordinate: ')
while strInput != 's':
    inputList = [float(num) for num in strInput.split(',')]
    inputX = torch.tensor(inputList, dtype=float32, device=GPU).reshape(inputSize, 1)
    inputCorrected = dataset.normalize(inputX)
    
    with torch.no_grad():
        prediction = forward(inputX).reshape(outputSize)
        print(prediction)
        print(decoder(prediction))
        
    strInput = input('enter coordinate: ')
    
