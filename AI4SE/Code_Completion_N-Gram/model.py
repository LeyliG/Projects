#

import re
import random
import math
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set
import javalang as jl
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from main import tokenize_java, cleansing, train_ngram_model, evaluate_model, generate



java_data = pd.read_csv("java_class_data.csv")

# filter out instances where code tokens exceed 100
java_data = java_data[ java_data['code_tokens'] <= 100]
# create a dataframe containing only java code 
java_class = pd.DataFrame(java_data['clean_java_class'])

# tokenize the java code 
java_class['tokenized_code'] = java_class['clean_java_class'].apply(tokenize_java)

# split the data 
tokenized_data = pd.DataFrame(java_class['tokenized_code'])

## Obtain Train and Test Split : 641 test, 5760 training set
train, test = train_test_split(tokenized_data, test_size=0.1, random_state=42)

## Obtain Train and Validation Split : 1152 val, 4608 train set
train, val = train_test_split(train, test_size=0.2, random_state=42)

# create vocabulary, treat out-of-vocab instances, handle <UNK>
min_freq = 7  # Set minimum frequency threshold
final_train, final_val, final_test, vocabulary = cleansing(train, val, test, min_freq)

# Update the vocabulary in our main code
vocab = {word: idx for idx, word in enumerate(vocabulary)}

# Train and evaluate models for n = 1 to 5
for n in range(1, 6):
    n_gram_counts = train_ngram_model(final_train.iloc[:, 0].tolist(), n, vocab)
    
    # Evaluate on validation data
    val_perplexity = evaluate_model(n, final_val.iloc[:, 0].tolist(), n_gram_counts, vocab)
    print(f"{n}-gram model validation perplexity: {val_perplexity:.2f}")

    # Generate code completion
    start_tokens = random.choice(final_test.iloc[:, 0].tolist())[:3]  # Randomly select 3 tokens to start
    completed_code = generate(start_tokens, n, n_gram_counts, vocab)
    print(f"\n{n}-gram model code completion:")
    print(' '.join(completed_code))
    print("\n" + "="*50 + "\n")
    












