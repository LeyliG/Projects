'''
Author Mostafa Ahmed

This script is used to split a CSV file into two 
separate files based on the presence of Chinese 
characters in a specific column. The script reads 
the input CSV file, checks each row for Chinese 
characters in the specified column, and writes 
the rows with Chinese characters to one output 
file and the rows without Chinese characters to 
another output file.
'''
import pandas as pd
import re
import argparse
import sys

def contains_chinese(text):
    if not isinstance(text, str):
        return False
    chinese_pattern = re.compile('[\u4e00-\u9fff]')                       #Simplified pattern to match only common Chinese characters
    return bool(chinese_pattern.search(str(text)))

def split_csv_by_chinese(input_file, non_chinese_output, chinese_output, debug=True):
    try:
        df = pd.read_csv(input_file)
        
        def row_contains_chinese(row):
            has_chinese = contains_chinese(str(row['Commit Message']))
            if debug and has_chinese:
                print(f"\nFound Chinese in commit message:")
                print(f"Message: {row['Commit Message'][:200]}...")
            return has_chinese
        
        chinese_rows = df[df.apply(row_contains_chinese, axis=1)]
        non_chinese_rows = df[~df.apply(row_contains_chinese, axis=1)]
        
        chinese_rows.to_csv(chinese_output, index=False, encoding='utf-8')
        non_chinese_rows.to_csv(non_chinese_output, index=False, encoding='utf-8')
        
        print(f"\nSummary:")
        print(f"Total rows: {len(df)}")
        print(f"Rows with Chinese characters in commit message: {len(chinese_rows)}")
        print(f"Rows without Chinese characters in commit message: {len(non_chinese_rows)}")
        print(f"\nFiles created:")
        print(f"- With Chinese characters: {chinese_output}")
        print(f"- Without Chinese characters: {non_chinese_output}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: Input file '{input_file}' is empty", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Split CSV file based on presence of Chinese characters in commit messages'
    )
    parser.add_argument(
        'input_file',
        help='Input CSV file to process'
    )
    parser.add_argument(
        '-c', '--chinese-output',
        default='commits_with_chinese.csv',
        help='Output file for commits with Chinese characters (default: commits_with_chinese.csv)'
    )
    parser.add_argument(
        '-n', '--non-chinese-output',
        default='commits_no_chinese.csv',
        help='Output file for commits without Chinese characters (default: commits_no_chinese.csv)'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug output'
    )

    args = parser.parse_args()
    split_csv_by_chinese(args.input_file, args.non_chinese_output, args.chinese_output, debug=not args.no_debug)

if __name__ == "__main__":
    main()
