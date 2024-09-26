# second file for pre-processing

import os
import re
import pandas as pd
from typing import List, Tuple
from collections import defaultdict
import random
import math
import json
#from pydriller import Repository
from javalang import parse, tree


# remove comments from the code: multiline /* */ & single-line //
## multiline and singleline comments
# https://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, string)


# v2 for extracting and cleaning up java class code

def extract_java_class(code):
    # Remove comments
    code = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.MULTILINE | re.DOTALL)
    
    # Remove empty lines and leading/trailing whitespace
    code = '\n'.join(line.strip() for line in code.split('\n') if line.strip())
    
    # Find all class definitions
    class_matches = re.finditer(r'(?:public\s+|protected\s+|private\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{', code)
    
    classes = []
    for match in class_matches:
        class_name = match.group(1)
        start_index = match.start()
        
        # Find the matching closing brace
        brace_count = 0
        end_index = start_index
        for i, char in enumerate(code[start_index:], start=start_index):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1
                    break
        
        # Extract the full class code
        class_code = code[start_index:end_index].strip()
        classes.append(class_code)
    
    # Return the first class found, or an empty string if no class was found
    return classes[0] if classes else ''

def is_public_class(class_code):
    # Check if the class definition starts with 'public'
    return bool(re.match(r'^\s*public\s+', class_code))

# Function to apply the extraction to a DataFrame
def java_class_column(df, input_column='java_code', output_column='java_class'):

    #df[output_column] = df[input_column].apply(extract_java_class)
    # Filter out rows where java_class is empty
    #df_filtered = df[df[output_column].str.strip() != '']
    
    df_copy = df.copy()
    # Apply the extraction function
    df_copy[output_column] = df_copy[input_column].apply(extract_java_class)
    
    # Filter out rows where java_class is empty or doesn't start with 'public'
    df_filtered = df_copy[
        (df_copy[output_column].str.strip() != '') &
        (df_copy[output_column].apply(is_public_class))
        ].copy()

    return df_filtered

# replece \n with empty space
def clean_string(string):
    # Remove newline characters
    cleaned_string = string.replace('\n', ' ')
    # Replace occurrences of 'id' with a space
    cleaned_string = cleaned_string.replace('id', ' ')
    return cleaned_string

# Function to identify rows with unbalanced quotes
def has_unbalanced_quotes(string):
    # Count the number of opening and closing quotes
    double_quotes = string.count('"')
    single_quotes = string.count("'")
    return (double_quotes % 2 != 0) or (single_quotes % 2 != 0)


# 
java_data = pd.read_csv("java_data.csv")
# Apply the extraction
java_data['java_code'] = java_data['content'].apply(remove_comments)
java_class_data = java_class_column(java_data)

# remove rows with URLs
java_class_data = java_class_data[~java_class_data.java_class.str.contains("https:", "http:")]
java_class_data = java_class_data[~java_class_data.java_class.str.contains("http:")]

# Applying the clean_string function to the 'content' column
java_class_data['clean_java_class'] = java_class_data['java_class'].apply(clean_string)

# remove lines with unbalalnced quotes
java_class_data = java_class_data[~java_class_data['clean_java_class'].apply(has_unbalanced_quotes)]

# save the updated and filtered DataFrame
java_class_data.to_csv('java_class_data.csv', index=False)







