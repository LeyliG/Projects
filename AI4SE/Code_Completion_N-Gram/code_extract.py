# this file is the first step in data pre-processing
# we load the json file and filter based on our needs
# we save the resulting smaller dataset for the next step in preprocessing

import os
import pandas as pd
from typing import List, Tuple
import json


file_path ='../seart_query.jsonl'

with open(file_path) as json_file:      
    full_data = json_file.readlines()
    # this line below may take at least 5 minutes. 
    # It converts all strings in list to actual json objects. 
    full_data = list(map(json.loads, full_data)) 

full_data= pd.DataFrame(full_data)
full_data= full_data.set_index('id')

# Filter the rows with less than 512 tokens and keep Apache projects
java_data = full_data[
    (full_data['total_tokens'] <= 512) &
    (full_data['repo'].apply(lambda repo: 'license' in repo and 
                                          ('Apache' in repo['license'] ))) &
    (full_data['repo'].apply(lambda repo: 'name' in repo and 
                                          ('apache' in repo['name'] )))
    ]


# save the updated and filtered DataFrame
java_data.to_csv('java_data.csv', index=False)

