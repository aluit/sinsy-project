#!/usr/bin/env python3

'''
    
Subtract the words in one set from another set.

Run with -h for help text.

Version: 0.1 - 28/02/2014

Author: aidan.martin@rmit.edu.au

'''

import sys
import os
import argparse
import unicodedata
import string
import re

def getTextFromFile(filename):
    'Return contents of file as a single string'
    try:
        with open(filename, 'rt', encoding=args.encoding) as f:
            data = f.read()

    except (UnicodeDecodeError):
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: file isn\'t ' + args.encoding + ' [' + filename + ']')
    except (PermissionError):
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: check file permissions [' + filename + ']')
    except Exception:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: unexpected problem [' + filename + ']')
    return data

def getSetFromFile(filename):
    'Return contents of file as a set of words'
    text = getTextFromFile(filename)

    # Decompose unicode -> chars + combining chars
    normalText = unicodedata.normalize('NFKD', text)

    # Drop the unicode combining chars
    normalText = normalText.encode('ascii', 'ignore').decode('ascii')

    # -> lowercase
    normalText = normalText.lower()

    # Split lines on linefeed, return, form feed:
    lines = re.split(r'[\n\r\f\v]', normalText)

    wordSet = set()

    # Take the first word on each line, ignore rest of line:
    for line in lines:
        words = re.split(r'[ ,;:|\t]', line)
        firstWord = words[0].strip()
        if len(firstWord) > 0:
            wordSet.add(firstWord)

    return wordSet

# Command-line arguments definitions (including help text):
parser = argparse.ArgumentParser(
    description='Subtract the words in one set from another set. Sets are specified with files containing one word per line. The first word on each line is read. Words after the first word are ignored. Returns filename1 - filename2.')

parser.add_argument(dest='filename1', metavar='filename1')

parser.add_argument(dest='filename2', metavar='filename2')

parser.add_argument('-e', dest='encoding', metavar='Encoding', action='store',
                    choices={'utf-8','utf-16','ascii'}, default='ascii',
                    help='utf-8, utf-16 or ascii (default=ascii)')

args = parser.parse_args()

# A file has been specified redundantly?
filenames = [args.filename1, args.filename2]
redundantFiles = {filename for filename in filenames if filenames.count(filename) > 1}
if len(redundantFiles) > 0:
    raise SystemExit(os.path.basename(sys.argv[0]) +
                     ': error: did you mean to substract the file from itself? ' + str(redundantFiles))

# requested files don't exist?
missingFiles = [filename for filename in filenames if not os.path.isfile(filename)]
if len(missingFiles) > 0:
    raise SystemExit(os.path.basename(sys.argv[0]) +
                     ': error: no such file ' + str(missingFiles))

# Do set subtraction & display result:
wordSet1 = getSetFromFile(args.filename1)
wordSet2 = getSetFromFile(args.filename2)
resultsWordSet = list(wordSet1 - wordSet2)
resultsWordSet.sort()
for word in resultsWordSet:
    print (word)
