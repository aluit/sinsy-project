#!/usr/bin/env python2.7
#
# Forked from text2cmudict
'''
Convert text into syllables.

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

def syllabify( word ):
    'Return string with dash + space between syllables '
    s = ''
    syllablecount = 0
    vowels = 0
    i = 0
    lastcharpos = len( word ) 
    smatches = 0
    prev = ' '
    for ch in word:
        i += 1 
        vmatches = re.search('[aeiouy]', ch )
        if vmatches: # it's the vowel sound of a syllable
 #               print ch+' is a vowel!!!'
            if not vowels: # first vowel of the syllable, presumably
                syllablecount += 1
                vowels = 1
            else: # it's a vowel and previous was vowel
                if smatches: # but previous was really a singable constant
                    s += '- '
        else: # it's a consonant
            smatches = re.search('[rlwnm]', ch) # treat as vowel sometimes...
            if not smatches: 
                if i < lastcharpos and vowels: # not last letter and previous letter was a vowel
                    s += '- '
                else:
#                    print "testing for 'ed' endings"
                    if i == lastcharpos and ch == 'd' and prev == 'e': # uh oh we're screwed, it's a "-ed" ending
                        # remove last dash
                        temp = s.rstrip('- ' )
                        print 'uh oh we''re screwed, it''s a "-ed" ending, temp is ', temp, ' but s is ', s, '.'
                vowels = 0
        s+=ch
        prev = ch
    return s

###############################################################################

# Main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                                 description='Convert text into syllables.')
    
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
text = re.sub('[^a-zA-Z \'\n]', ' ', text) # Anything that isn't alpha or whitespace replaced with space
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
  #      print word, len( word ), d[ word ][0], numMatches,
        if numMatches <= 1:
            print word,
        else: # more than one syllable
            print syllabify( word ),
    else:
        print syllabify( word ), #should syllabify non-cmudict word

print
