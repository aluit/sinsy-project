#!/usr/bin/env python3.4

'''
Find most common words in textfiles.

Run with -h for help text.

Version: 0.2 - 4/4/2014

'''

import sys
import os
import argparse
import unicodedata
import string

###############################################################################

def countWordsInText(text):
    'Return a dictionary containing (word, frequency) pairs'
    
    # Text is sanitized in various ways before counting the words:
    # 1) Decompose unicode -> chars + combining chars
    # 2) Drop the unicode combining chars
    # 3) Remove punctuation
    # 4) -> lowercase
    # 5) Get words by splitting text on whitespace or line breaks
    # 6) Discard words containing numbers
    # 7) TODO not implemented - use the nltk lemmatiser?

    normalText = unicodedata.normalize('NFKD', text)
    normalText = normalText.encode('ascii', 'ignore').decode('ascii')
    normalText = normalText.translate(dict.fromkeys([ord(c) for c in string.punctuation]))
    normalText = normalText.lower()

    wordDictionary = {}
    words = normalText.split()
    for word in words:
        if word.isalpha():
            wordDictionary[word] = wordDictionary.get(word, 0) + 1

    return wordDictionary

###############################################################################

def getTextFromFile(filename):
    'Return contents of file as a string'
    
    try:
        with open(filename, 'rt', encoding=args.encoding) as f: data = f.read()

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

###############################################################################

# Main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                                 description='Find the most common words in text files.')
    
    parser.add_argument(dest='filenames', metavar='filename', nargs='*',
                        help='one or more text files')
                        
    parser.add_argument('-m', metavar='Count', dest='mincount', action='store',
                        default='1',
                        help='output words which occur at least Count times (default = 1); when processing multiple files, output words which occur at least Count times in at least one file')

    parser.add_argument('-s', metavar='Separator', dest='separator', action='store',
                        default=' ',
                        help='character or string used to separate words and counts in output (default = " ")')

    parser.add_argument('-q', dest='quiet', action='store_true',
                        help='suppress word counts in output')

    parser.add_argument('-e', dest='encoding', metavar='Encoding', action='store',
                        choices={'utf-8','utf-16','ascii'}, default='utf-8',
                        help='utf-8, utf-16 or ascii (default=utf-8)')
                        
    args = parser.parse_args()

    # Confirm that the arguments supplied from command line make sense:

    if not str(args.mincount).isdigit() or int(args.mincount) == 0:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: the minimum count should be a positive integer.')

    if len(args.filenames) == 0:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: one or more filenames must be specified.')

    missingFiles = [filename for filename in args.filenames if not os.path.isfile(filename)]
    if len(missingFiles) > 0:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: no such file ' + str(missingFiles))

    redundantFiles = {filename for filename in args.filenames if args.filenames.count(filename) > 1}
    if len(redundantFiles) > 0:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: redundant file[s] ' + str(redundantFiles))

    # Run the analysis:

    globalWordSet = set()
    allWordDictionaries = {}
    for filename in args.filenames:
        wordDictionary = countWordsInText(getTextFromFile(filename))
        allWordDictionaries[filename] = wordDictionary
        globalWordSet.update(wordDictionary.keys())

    allWords = list(globalWordSet)
    allWords.sort()
    for word in allWords:
        countsString = ""
        maxWordCount = 0
        for filename in args.filenames:
            wordDictionary = allWordDictionaries[filename]
            wordCount = wordDictionary.get(word, 0)
            maxWordCount = wordCount if (wordCount > maxWordCount) else maxWordCount
            countsString = countsString + args.separator + str(wordCount)
        if maxWordCount >= int(args.mincount):
            if args.quiet:
                print (word)
            else:
                print (word + countsString)

###############################################################################
