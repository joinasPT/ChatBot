import pandas as pd
import numpy as np
import nltk
import re
import json 
from scripts_processing import utils
import seaborn as sns
import matplotlib.pyplot as plt

#loading the scripts
episode_script = np.load('scripts_processing/processed_scripts.npy').item()

#loading the characters dataset to a dictionary
with open("story_locations/locations.json") as f:
    data = json.load(f)

#selecting only the name fo characters
regions = []
for region in data['regions']:
    for subregion in region['subLocation']:
        if subregion != '':
            regions.append([region['location'].lower().replace("'",''), subregion.lower().replace("'",'')])

#function to extract location from description
def find_regions(sentence, regions):
    for region in regions:
        if region[0] in sentence.lower().replace("'",''):
            return region[0]
        elif region[1] in sentence.lower().replace("'",''):
            if region[1]=='inn':
                return region[0]
            else:
                return region[1]
    return 'somewhere'

#finding locations
last_location = 'unknown'
counter = []
for episode, script in episode_script.items():
    for line in script:
        if line[1]=='Scene Change' or line[1]=='Description':
            if find_regions(line[0].lower(), regions) != 'somewhere':
                last_location = find_regions(line[0].lower(), regions)
        else:
            counter.append([episode,last_location, 1])
                

counter = pd.DataFrame(counter, columns = ['season','location','count'])

counter['season'] = counter['season'].str[0:2]
counter['season'] = 'Season '+counter['season'].str[-1]
counter['location'] = counter['location'].str.title()

top10 = counter[['location','count']].groupby(['location']).sum().reset_index().sort_values(by=['count'], ascending=False).head(5)

counter = counter[counter['location'].isin(top10['location'].values)]
counter = counter.groupby(['season','location']).sum().reset_index()  

for season in counter['season'].unique():
    counter.loc[counter['season']==season,'count'] = counter.loc[counter['season']==season,'count'] / np.sum(counter.loc[counter['season']==season,'count'])



matrix=[]
for i in range(len(counter['season'].unique())):
    line = []
    for c in range(len(counter['location'].unique())):
        try:
            line.append(counter.loc[(counter['season']==counter['season'].unique()[i]) & (counter['location']==counter['location'].unique()[c]) , 'count'].values[0])
        except:
            line.append(0)
    matrix.append(line)

matrix = pd.DataFrame(matrix, columns = counter['location'].unique(), index = counter['season'].unique())

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.set_facecolor('xkcd:salmon')
ax.set_facecolor((1.0, 0.47, 0.42))




plt.style.use('dark_background')
ax = matrix.plot(kind='barh', stacked=True)
ax.set_facecolor((0,0,0))
ax.get_xaxis().set_visible(False)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0),
          ncol=3, fancybox=True, shadow=True)
ax.set_title('Location Distribution by Season')



colors = ['gray','green','green','orange','white','yellow']


plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)



N = 5
menMeans = (20, 35, 30, 35, 27)
womenMeans = (25, 32, 34, 20, 25)
menStd = (2, 3, 4, 1, 2)
womenStd = (3, 5, 2, 3, 3)
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, menMeans, width, yerr=menStd)
p2 = plt.bar(ind, womenMeans, width,
             bottom=menMeans, yerr=womenStd)

plt.ylabel('Scores')
plt.title('Scores by group and gender')
plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0]), ('Men', 'Women'))

plt.show()

