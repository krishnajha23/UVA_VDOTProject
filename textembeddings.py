import numpy as np
from numpy.linalg import norm
import pandas as pd
import openai
import tiktoken
openai.api_key = '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'
embedding_model = "text-embedding-3-large"
categorized_data = []
routine1 = "re-inspection"
routine2 = "routine annual inspection mow"
routine3 = "trim litter clean assessment"
routine4 = "brush cutting sign"
corrective1 = "Corrective action structural erosion repair"
corrective2 = "shrub tree debris sediment removal drop inlets"
corrective3 = "mulching pipe clogging invasive vegetation oil spill vacuum fence rip rap,"
significant = "restoration rehabilitation rebuilding BMP"
contextembeddings = []
for i in [routine1,routine2,routine3,routine4,corrective1,corrective2,corrective3,significant]:
  response = openai.Embedding.create(input=[i], model=embedding_model)
  contextembeddings.append(response['data'][0]['embedding'])
categorized_data = []
cosinesimilarities = []
sampleembeddings = []
ranges = []
highestcosines = []
sampledescriptions = pd.read_excel(r'TestCases.xlsx')['Description'].fillna('a').tolist()
for i in sampledescriptions:
  sampleembedding = openai.Embedding.create(input=[i], model=embedding_model)['data'][0]['embedding']
  sampleembeddings.append(sampleembedding)
for a in sampleembeddings:
  cosines = []
  highestcosine = -10
  highestcosineindex = -1
  for i in contextembeddings:
    cosine = np.dot(a,i)/(norm(a)*norm(i))
    cosines.append(cosine)
  for i in range(len(cosines)):
    if cosines[i] > highestcosine:
      highestcosine = cosines[i]
      highestcosineindex = i
  highestcosines.append(highestcosine)
  cosrange = np.ptp(cosines,axis=0)
  if highestcosine < 0.28:
    category = "Unknown"
  elif highestcosineindex == 0:
    category = "Routine"
  elif highestcosineindex == 1:
    category = "Routine"
  elif highestcosineindex == 2:
    category = "Routine"
  elif highestcosineindex == 3:
    category = "Routine"
  elif highestcosineindex == 4:
    category = "Corrective"
  elif highestcosineindex == 5:
    category = "Corrective"
  elif highestcosineindex == 6:
    category = "Corrective"
  elif highestcosineindex == 7:
    category = "Significant"
  categorized_data.append(category)
  ranges.append(cosrange)
  cosinesimilarities.append(cosines)
mydf = pd.read_excel(r'TestCases.xlsx')
mydf['cosine ranges'] = ranges
mydf['highest cosines'] = highestcosines
mydf['cosine similarity scores'] = cosinesimilarities
mydf['cosine categorized data'] = categorized_data
