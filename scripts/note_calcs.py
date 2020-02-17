#!/usr/bin/env python3.4

'''
Calculate MIDI note numbers for input file

Run with -h for help text.

Version: 0.1 - 10/1/19

Still being written. Currently correctly calculates constants, but seems to not process the last line of
input.

'''

import sys
import os
import argparse
import unicodedata
import string
import math
from math import *
import xml.etree.ElementTree as ET

###############################################################################

def getWordFreqs(text):
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
    tokens = normalText.split()
    for token in tokens:
#        print( 'processing ' +  token)
        sys.stdout.flush()
        if token.isalpha():
            word = token
        else:
            if token.isdigit():
                wordDictionary[word] = int(token);
            else:
                raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: file isn\'t  in the correct format' + ' [' + word + ' ' + token + ']')

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

def MIDI2Note( midinumber ):
    'Returns the note name and octave of a given MIDI note number'
    
    notes = [ 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B' ]
    numberOfNotes = len(notes)
    index = midinumber % numberOfNotes
    if len(notes[index] )> 1:
           index -= 1
           alter = 1
    else:
           alter = 0
           
    return notes[ index ], int(midinumber/numberOfNotes)-1, alter


def generateXML(combinedList, tempo):
    score_partwise = ET.Element('score-partwise')
    part_list = ET.SubElement(score_partwise, 'part-list')
    score_part = ET.SubElement(part_list, 'score-part')
    score_part.attrib['id'] = 'P1'
    part = ET.SubElement(score_partwise, 'part')
    part.attrib['id'] = 'P1'
    measureNumber = 1
    measure = None

    for item in combinedList:
    #   for i in range(0, len(arr)):
            measure = ET.SubElement(part, 'measure')
            measure.attrib['number'] = str(measureNumber)
            if measureNumber == 1:
                attributes = ET.SubElement(measure, 'attributes')
                divisions = ET.SubElement(attributes, 'divisions')
                divisions.text = '12'
                key = ET.SubElement( attributes, 'key')
                fifths = ET.SubElement( key, 'fifths')
                fifths.text = '0'
                time = ET.SubElement(attributes, 'time')
                beats = ET.SubElement( time, 'beats')
                beats.text = '2'
                beattype = ET.SubElement( time, 'beat-type')
                beattype.text = '4'
                direction = ET.SubElement(measure, 'direction')
                sound = ET.SubElement(direction, 'sound')
                sound.attrib['tempo'] = tempo
            measureNumber += 1
            note = ET.SubElement(measure, 'note')
            duration = ET.SubElement(note, 'duration')
            duration.text = '12'
            voice = ET.SubElement(note, 'voice')
            voice.text = '1'
            pitch = ET.SubElement(note, 'pitch')
            step = ET.SubElement(pitch, 'step')
            alter = ET.SubElement(pitch, 'alter')
            octave = ET.SubElement(pitch, 'octave')
            newWord = item[0]
            newOctave = item[1]
            newNote = item[2]
            newAlter = item[3]
            step.text = newNote
            alter.text = str(newAlter)
            octave.text = str(newOctave)
            notetype = ET.SubElement(note, 'type')
            notetype.text = 'quarter'
            lyricElt = ET.SubElement(note, 'lyric')
            lyricTextElt = ET.SubElement(lyricElt, 'text')
            lyricTextElt.text = newWord
# add a rest after the note
            note = ET.SubElement(measure, 'note')
            rest = ET.SubElement(note, 'rest')
            duration = ET.SubElement(note, 'duration')
            duration.text = '12'
            voice = ET.SubElement(note, 'voice')
            voice.text = '1'
            notetype = ET.SubElement(note, 'type')
            notetype.text = 'quarter'

    return score_partwise


###############################################################################

# Main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                                 description='Calculate notes from input data.')
    
    parser.add_argument(dest='filenames', metavar='filename', nargs='*',
                        help='one or more text files')
                        
    parser.add_argument('-L', metavar='midinote', dest='minnote', action='store',
                        default='43',
                        help='minimum MIDI note number (default = 43, or bass low G, i.e. G2); ')

    parser.add_argument('-H', metavar='midinote', dest='maxnote', action='store',
                        default='78',
                        help='maximum MIDI note number (default = 78, or soprano high F#, i.e. F#5); ')

    parser.add_argument('-s', metavar='Separator', dest='separator', action='store',
                        default=' ',
                        help='character or string used to separate words and counts in output (default = " ")')

    parser.add_argument('-q', dest='quiet', action='store_true',
                        help='suppress word counts in output')

    parser.add_argument('-e', dest='encoding', metavar='Encoding', action='store',
                        choices={'utf-8','utf-16','ascii'}, default='utf-8',
                        help='utf-8, utf-16 or ascii (default=utf-8)')
                        
    parser.add_argument('-t', metavar = 'tempo', dest = 'tempo', action = 'store', default = '700',
                        help = 'Tempo of output in ticks, default = 700')
    args = parser.parse_args()

    # Confirm that the arguments supplied from command line make sense:

    if not str(args.minnote).isdigit() or int(args.minnote) == 0 or int(args.minnote) > 127:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: the minimum MIDI note should be a non-negative integer < 128')

    minnote = int(args.minnote)

    if not str(args.maxnote).isdigit() or int(args.maxnote) == 0 or int(args.maxnote) > 127:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: the maximum MIDI note should be a positive integer < 128.')

    maxnote = int(args.maxnote)
    noterange = maxnote - minnote

    if noterange < 0:
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: the maximum MIDI note should be larger than the minimum MIDI note.')

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

    if not str(args.tempo).isdigit() or int(args.tempo) <= 0 :
        raise SystemExit(os.path.basename(sys.argv[0]) +
                         ': error: the tempo should be a non-negative integer ')

    tempo = int(args.tempo)

# Run the analysis:

    globalWordSet = set()
    globalFreqSet = set()
    allWordDictionaries = {}
    midiDictionary = {}

# Get the words and frequencies from the file
    for filename in args.filenames:
        wordDictionary = getWordFreqs(getTextFromFile(filename))
        allWordDictionaries[filename] = wordDictionary
        midiDictionary[filename] = wordDictionary
        globalWordSet.update(wordDictionary.keys())

    allWords = list(globalWordSet)
#    allWords.sort()

# Find the minimum and maximum word counts

maxWordCount = 0
minWordCount = sys.maxsize;
countsString = ""
for word in allWords:
    for filename in args.filenames:
        wordDictionary = allWordDictionaries[filename]
        wordCount = wordDictionary.get(word, 0)
        maxWordCount = wordCount if (wordCount > maxWordCount) else maxWordCount
        minWordCount = wordCount if (wordCount < minWordCount) else minWordCount

#print ('maxwordcount = ' + str(maxWordCount) + ' and minwordcount = ' + str(minWordCount))
#print ('max note = ' + str(maxnote) + ' and minnote = ' + str(minnote))
            
# Based on min and max word counts, work out frequencies and midi note numbers

maxaudio = 2 ** ((maxnote - 69)/12) * 440
minaudio = 2 ** ((minnote - 69)/12) * 440

#print( 'maxaudio = ' + str(maxaudio) + ' and minaudio = ' + str(minaudio))

k = log(maxaudio/minaudio, 2)
const = (maxWordCount/minWordCount)**(1.0/k)
log_const = 1/log(const,2)
#print( 'k = ' + str( k) )
#print( 'const = ' + str( const) )
#print( 'log_const = ' + str( log_const) )
# Create a dictionary containing the words and their MIDI note numbers
#midiDictionary = getMIDIDictionary(allWordDictionaries, allWords, maxaudio, maxWordCount, log_const)
for word in allWords:
    for filename in args.filenames:
        wordDictionary = allWordDictionaries[filename]
        wordCount = wordDictionary.get(word, 0)
        audiofreq = maxaudio * (wordCount/maxWordCount)**log_const
        midiDictionary[filename][word] = round( 69 + 12 * log( audiofreq/440, 2))

sortedDictionary = {}

#    print( midiDictionary[filename] )
sortedList = sorted( midiDictionary[filename].items(), key = 
                  lambda kv:(kv[1], kv[0]), reverse = True )
    
#    print( sortedList )

# Output  notes

tempDictionary = {}
noteDictionary={}
octaveDictionary={}
alterDictionary={}

#for word in allWords:
#    for filename in args.filenames:
#        wordDictionary = midiDictionary[filename]
#        wordDictionary = sortedDictionary
  #      
    #    countsString =  args.separator + str(midinumber) + ' '
      #  
#        print (word + countsString + note + ' ' + str(alter) + ' ' + str(octave) )
        #noteDictionary[filename] = wordDictionary
        #noteDictionary[filename][word]=note
        #octaveDictionary[filename] = wordDictionary
        #octaveDictionary[filename][word] = str(octave)
        #alterDictionary[filename] = wordDictionary
        #alterDictionary[filename][word] = str(alter)

noteList = []
octaveList = []
alterList = []
combinedList = []

for item in sortedList:
    midinumber = item[1]
    note, octave, alter = MIDI2Note( midinumber)
#    print( item[0] + ' ' + str(item[1] ) + ' ' + note + ' ' + str(alter) + ' ' + str(octave) )
    octaveList.append( (item[0], octave) )
    noteList.append( ( item[0], note ) )
    alterList.append( (item[0], alter ) )
    combinedList.append( (item[0], octave, note, alter ) )
    

#print( octaveList, noteList, alterList )
#print( combinedList )




root = generateXML( combinedList, args.tempo)
###############################################################################
#output = ET.tostring(root, encoding='UTF-8')
output = ET.tostring(root, encoding='unicode')

print( output)
