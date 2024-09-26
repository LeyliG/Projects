# file with all the function definitions

import re
import random
import math
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set
import javalang as jl
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


# tokenize the data with javalang : string -> list[string]
def tokenize_java(code):
    tokens = []
    for token in jl.tokenizer.tokenize(code):
        if token.__class__.__name__ not in ['Separator', 'Operator']:
                tokens.append(token.value)
        else:
            tokens.append(token.__class__.__name__)
    
    return tokens

# create vocabulary (frequency dictionary)
def count_the_words(tokenized_data):
    # Creating a Dictionary of counts
    word_counts = Counter()
    
    # Iterating over tokenized code
    for tokens in tokenized_data.iloc[:, 0]:
        word_counts.update(tokens)
    
    return dict(word_counts)


def handling_oov(tokenized_data, count_threshold=1):
    # Empty list for closed vocabulary
    closed_vocabulary = ['<UNK>']
    
    # Obtain frequency dictionary using previously defined function
    words_count = count_the_words(tokenized_data)
    
    # Iterate over words and counts 
    for word, count in words_count.items():
        # Append if it's more (or equal) to the threshold 
        if count >= count_threshold:
            closed_vocabulary.append(word)
    
    return closed_vocabulary

# Create a function to replace out-of-vocabulary tokens
def handle_unk(tokens, vocab):
    return ['<UNK>' if token not in vocab else token for token in tokens]

def unk_tokenize(tokenized_data, vocabulary, unknown_token = "<UNK>"):
    # Convert Vocabulary into a set
    vocabulary_set = set(vocabulary)
    
    # Create a function to replace out-of-vocabulary tokens    
    def replace_oov(tokens):
        return [token if token in vocabulary_set else unknown_token for token in tokens]
    
    # Apply the function to each row of the DataFrame
    new_tokenized_data = tokenized_data.applymap(replace_oov)
    
    return new_tokenized_data


def cleansing(train_data, val_data, test_data, count_threshold=1):
    # Get closed vocabulary
    vocabulary = handling_oov(train_data, count_threshold)
    
    # Updated training and validation Datasets
    new_train_data = unk_tokenize(train_data, vocabulary)
    new_val_data = unk_tokenize(val_data, vocabulary)
    
    # Updated Test Dataset
    new_test_data = unk_tokenize(test_data, vocabulary)
    
    return new_train_data, new_val_data, new_test_data, vocabulary


# define function to train the model

def create_ngrams(tokens, n):
    return list(zip(*[tokens[i:] for i in range(n)]))

def train_ngram_model(tokenized_code, n, vocab):
    cfdist = defaultdict(lambda: defaultdict(float))
    for tokens in tokenized_code:
        padded_tokens = ['<s>'] * (n-1) + tokens + ['</s>']
        ngrams = create_ngrams(padded_tokens, n)
        for ngram in ngrams:
            context, token = ngram[:-1], ngram[-1]
            cfdist[context][token] += 1
    
    # Convert frequencies to probabilities
    for context in cfdist:
        total_count = float(sum(cfdist[context].values()))
        for token in cfdist[context]:
            cfdist[context][token] /= total_count
    
    return cfdist

def predict_next_token(context, model, vocab):
    context = tuple(context)
    if context in model:
        probabilities = model[context]
        return max(probabilities, key=probabilities.get)
    return random.choice(list(vocab))

def generate(context, n, model, vocab, max_length=100):
    generated = list(context)
    while len(generated) < max_length:
        next_token = predict_next_token(generated[-(n-1):], model, vocab)
        if next_token == '</s>':
            break
        generated.append(next_token)
    return generated

# calculate perplexity
def evaluate_model(n, eval_data, model, vocab):
    log_likelihood = 0
    token_count = 0
    for tokens in eval_data:
        padded_tokens = ['<s>'] * (n-1) + tokens + ['</s>']
        ngrams = create_ngrams(padded_tokens, n)
        for ngram in ngrams:
            context, token = ngram[:-1], ngram[-1]
            probability = model[context][token] if context in model and token in model[context] else 1e-10
            log_likelihood += np.log(probability)
            token_count += 1
    return np.exp(-log_likelihood / token_count)














