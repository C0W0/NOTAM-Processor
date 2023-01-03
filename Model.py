import sys
sys.path.append(f'{sys.path[0]}\\data_set')
from data_set.Process_Data import get_data, get_decoder

decoder = get_decoder()
X, Y = get_data()
print(f'{X[6]}: {Y[6]}')
print(decoder(Y[6]))
