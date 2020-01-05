import json
from pprint import pprint
import numpy as np
import pandas as pd
import pinyin
import shapefile

# Data from https://data.gov.tw/dataset/8120
# Source: Council of Agriculture
with open("cropdata.json", "r") as file:
    cropdata = json.load(file)

# Fruit list edited by Yanping
with open("fruits.txt", "r") as file:
    fruitset = set(line.replace('\n','') for line in file)

# Shapefile from some source.
# TODO look up where this came from
with shapefile.Reader("villageLevelShapefile/TOWN_MOI_1080617.shp") as shape:
    mapctytwn = ["".join(r[1:3]) for r in shape.records()]
with open("shapefile_entries.txt", "w") as file:
    file.write("\n".join(mapctytwn))

# reducing everything to ASCII pinyin will help us export these things much more easily.
# Because you #can't #trust #Unicode.
def PYnoTone(string):
    return pinyin.get(string, format='strip')

# Saves a pinyin version of the fruit names for future use
with open("fruitpinyin.csv", "w") as pinyinfile:
    pinyinfile.write("pinyin, guoyu\n")
    pinyindefs = [",".join([PYnoTone(f), f])+"\n" for f in fruitset]
    pinyinfile.writelines(pinyindefs)

# Some manual replacements to clean errors in the original data
replacementpairs = (
    ('台',"臺"),
    ('臺東縣成功鄉',"臺東縣成功鎮"),
    ('桃園縣大溪鎮','桃園市大溪區'),
    ('桃園縣復興鄉','桃園市復興區'),
    ('彰化縣員林鎮','彰化縣員林市'),
    ('雲林縣竹塘鄉','彰化縣竹塘鄉'),
    ('屏東縣燕巢區','高雄市燕巢區')
    )

# Keeps everything encapsulated
def openfruit(dictentry):
    crop = dictentry.pop('crop')
    countytown = dictentry.pop('county') + dictentry.pop('town')
    for c in replacementpairs:
        countytown = countytown.replace(c[0], c[1])
    month = dictentry.pop('month')
    return crop, countytown, month
    
# creates a dictionary separated by fruits
fruitdict = {fruit:{} for fruit in fruitset}
townset = []
for entry in cropdata:
    crop, countytown, month = openfruit(entry)
    townset.append(countytown)
    if crop in fruitset:
        fruitdict[crop][countytown] = month

# This is a set of county-town pairs, for debugging 臺／台 style problems
# \u3000 is the full-width space in Chinese.
townset = [n.replace("\u3000", "") for n in townset]
townset = set(townset)

# for t in townset:
#     # Some data have no town info attached. These will be discarded.
#     if t not in mapctytwn and len(t) >= 3:
#         # This ensures that everything matches up.
#         print(f"Error! {t} does not appear in shapefile")

# Saves the original Unicode as json for future use
with open("fruitdata_parsed.json", 'w') as file:
    json.dump(fruitdict, file, ensure_ascii=False, indent=2)

#Saves a dataset of town pinyin names for future use.
with open("townpinyin.csv", "w") as pinyinfile:
    pinyinfile.write("pinyin, guoyu\n")
    pinyindefs = [",".join([PYnoTone(t), t])+"\n" for t in townset]
    pinyinfile.writelines(pinyindefs)

# Creates a pure pinyin dataframe with all fruits.
# This can be sliced later if we need to.
combinedfruitdf = pd.DataFrame(columns=['COUNTYTOWN'] + [PYnoTone(f) for f in fruitset])
combinedfruitdf['COUNTYTOWN'] = [PYnoTone(t) for t in townset]
combinedfruitdf = combinedfruitdf.set_index('COUNTYTOWN')

for fruit in fruitdict:
    for town in fruitdict[fruit]:
        combinedfruitdf[PYnoTone(fruit)][PYnoTone(town)] = 1
combinedfruitdf = combinedfruitdf.fillna(0)

with open("allfruits.csv", 'w') as file:
    combinedfruitdf.to_csv(file)

unicodefruitdf = pd.DataFrame(columns=["COUNTYTOWN"]+list(fruitset))
unicodefruitdf['COUNTYTOWN'] = list(townset)
print(unicodefruitdf.columns)


for fruit in fruitdict:
    for town in fruitdict[fruit]:
        unicodefruitdf[fruit][town] = 1
unicodefruitdf = unicodefruitdf.fillna(0)
with open("allfruitsutf8.csv", 'w') as file:
    unicodefruitdf.to_csv(file, index=False)

print(fruitdict)
print(unicodefruitdf)