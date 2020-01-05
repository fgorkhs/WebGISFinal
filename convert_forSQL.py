import json
import numpy as np
import pandas as pd
import pinyin

with open("fruitdata_parsed.json" , 'r') as file:
    datadict = json.load(file)

def PYnoTone(string):
    return pinyin.get(string, format='strip')

fruits = list(datadict.keys())

towns = []
for f in datadict:
    [towns.append(t) for t in datadict[f].keys()]

towns = list((set(towns)))

dfpinyin = pd.DataFrame(columns=['countytown', 'ctytwnhanzi']+[PYnoTone(f) for f in fruits])
dfpinyin['ctytwnhanzi'] = towns
dfpinyin['countytown'] = [PYnoTone(t) for t in towns]
dfpinyin = dfpinyin.set_index("countytown")
dfpinyin = dfpinyin.fillna(0)

for fruit in datadict:
    for town in datadict[fruit]:
        dfpinyin[PYnoTone(fruit)][[PYnoTone(town)]] = datadict[fruit][town]

print(dfpinyin)

with open('fruitbymonth_pinyin.csv', 'w') as file:
    dfpinyin.to_csv(file)