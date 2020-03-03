#!/usr/bin/env python2.7

'''
Convert text into cmudict sinsy-compatible syllables.

Run with -h for help text.

Version: 0.2 

'''

import sys
import os
import argparse
import unicodedata
import string
import re

import nltk, numpy
from nltk.corpus import cmudict
import curses
from curses.ascii import isdigit

d = cmudict.dict()  # global...

###############################################################################

def getTextFromFile(filename):
    'Return contents of file as a string'
    
    print 'file is ', filename
    f = open( filename );    
    return f.read()

###############################################################################

# Main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                                 description='Convert text into cmudict sinsy-compatible syllables.')
    
    parser.add_argument(  "lyricsfile", type =argparse.FileType('r'),   help='a text file containing lyrics' )
                        
    parser.add_argument('-e', dest='encoding', metavar='Encoding', action='store',
                        choices={'utf-8','utf-16','ascii'}, default='utf-8',
                        help='utf-8, utf-16 or ascii (default=utf-8)')
                        
    args = parser.parse_args()

    # Confirm that the arguments supplied from command line make sense:

 #   print 'file name is ' + args.lyricsfile.name
  
  #  if not os.path.isfile(args.filename)
     #  raise SystemExit(os.path.basename(sys.argv[0]) +
        #                 ': error: no such file ' + args.filename)

    # Do the thing...


globalWordSet = set()
allWordDictionaries = {}

lyrics = args.lyricsfile.read()
 
# print lyrics

text = lyrics.decode('UTF-8').lower() # converts all to lower case
text = re.sub('[^a-zA-Z \']', ' ', text) # Anything that isn't alpha or whitespace replaced with space
text = re.split(r'\s+', text) # splits into "words"

#print text

results = []
for word in text:
    if word == ','  or word == '': # This gets rid of the empy string at the end of the list
        continue
    else:
        results.append( word )

for word in results:
    numMatches = 0
    if word  in d:
        for phone in d[word][0]: # counting syllables
                matches = re.search('[0-9]', phone )
                if matches:
                    numMatches += 1
     #   print word, len( word ), d[ word ][0], numMatches,
        syllablecount = 0
        phonecount = 0
        s=''
        for phone in d[word][0]:
            pphone = re.sub('[0-9]','',phone )
            if phonecount == 0:
                s += '['+pphone
            else:
                s += ','+ pphone
                #    while not re.search('[0-9]', phone ):
                #       print ',', phone,
            matches = re.search('[0-9]', phone )
            if matches: # it's the vowel sound of a syllable
                    syllablecount += 1
                    if syllablecount < numMatches: # not last syllable vowel
                        s += ']- '
                        phonecount = -1
            phonecount+= 1
        s += ']'
        print s.lower()
    else:
        print '['+word+']'



