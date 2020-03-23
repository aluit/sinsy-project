#!/usr/bin/python

import re
import argparse
import xml.etree.ElementTree as ET

def handleFirstSyllable( e, word, middle, extend, lastchar ):
    # start of a word
    if lastchar != '-' and lastchar != '_':
        # doesn't end in dash or underscore, so single
        e.text = 'single'
    elif lastchar == '-':
        # first syllable of a word (assuming it isn't just a dash...)
        e.text = 'begin'
        middle = True
        word = word[ 0:len(word) - 1 ] # remove dash
    elif lastchar == '_':
        # monosyllabic extended
        e.text = 'single'
        word = word[ 0:len(word) - 1 ] # remove underscore
        if len(word) > 0:
            # presumably last syllable extended
            extend = True
            #else presumably an extra note to be applied to the last syllable
    return word, middle, extend

def handleOtherSyllables( e, word, middle, extend, lastchar ):
    # middle (or end) of a word
    if lastchar != '-' and lastchar != '_':
        # end of word
        e.text = 'end'
        middle = False
    elif lastchar == '-':
        # middle of word
        e.text = 'middle'
        word = word[ 0:len(word) - 1 ] # remove dash
    elif lastchar == '_':
        # polysyllabic extended
        e.text = 'end'
        word = word[ 0:len(word) - 1 ] # remove underscore
        extend = True
        middle = False
    else:
        # how did that happen?!!
        print 'Error: how did this happen, with middle syllable and word = ', word, '?!!'
    return word, middle, extend

def addLyricsToNoteIfRequired( lyricElt, lyrics, middle, extend, i ):
    # Try to modularise this a bit, since it's become insane
    # Need to set syllabic, text and extend, or omit things
    word = ''
    n = len(lyrics)
    # print 'In addLyricsToNoteIfRequired with i = ', i, 'word is  ', lyrics[i%n]
    hasSyllabic = False
    hasLyricText = False
    for e in lyricElt.findall('syllabic'):
        hasSyllabic = True
    for e in lyricElt.findall('text'):
        hasLyricText = True
    if not hasSyllabic:
        syllabicElt = ET.SubElement( lyricElt, 'syllabic')
    # Now we definitely have a syllabic element
    for e in lyricElt.findall('syllabic'):
        word = lyrics[i%n]
        lastchar = word[len(word) - 1] 
        # print word, word[len(word) - 1] , lastchar
    if not middle:
        word, middle, extend = handleFirstSyllable( e, word, middle, extend, lastchar )
    else:
        word, middle, extend = handleOtherSyllables( e, word, middle, extend, lastchar )
    if not hasLyricText and len( word ) > 0:
        lyricTextElt = ET.SubElement( lyricElt, 'text')
    elif hasLyricText and len( word ) == 0:
        # get rid of text element
        lyricElt.remove( lyricTextElt )
    if len( word ) > 0:
        # should still have an element
        for e in lyricElt.findall('text'):
            e.text = word
    i+=1
    hasExtend = False
    for e in lyricElt.findall( 'extend'):
        hasExtend = True
    if extend and not  hasExtend:
        # syllable extends over following notes, indicated by underscore in input
        # and we need to create an extend element
        extendElt = ET.SubElement( lyricElt, 'extend' )
        extend = False
    elif not extend and hasExtend:
        # uh oh, we need to get rid of an element. How do I do that? Oh, like this.
        lyricElt.remove( extendElt )
        # else either there is an extend already and we're extending
        # or there isn't an extend and we're not extending
        # so do nothing
    return i, middle, extend

def addLyrics(root, lyrics):
    # Sandra version, process dashes as syllable markers
    # Process dashes in isolation as melisma (middle syllables auto extend unlyricked notes)
    # Also process underscores at the end of a word as melisma
    # If syllabic tags are correctly applied, and dashes removed, sinsy works better.
    #   edlyrics = list( lyrics ) # need a copy, since addLyric loops through text as often as needed
    #print edlyrics
    #print lyrics
    i = 0
    for a in root.findall('part'):
        # First initialise a few things...
        middle = False
        extend = False
        for b in a.findall('measure'):
            for c in b.findall('note'):
                hasRest = False
                for d in c.findall('rest'):
                    hasRest = True
                if hasRest:
                    # do nothing, so jump out of note loop
                    continue
                # We have an actual note, not a rest
                hasLyric = False
                for d in c.findall('lyric'):
                    hasLyric = True
                if not hasLyric:
                    lyricElt = ET.SubElement(c, 'lyric')
                # We now have a lyric element, which may be empty
                for d in c.findall('lyric'):
                    i, middle, extend = addLyricsToNoteIfRequired( lyricElt, lyrics, middle, extend, i )


                
#
# Parse command line arguments
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xmlfile", type=argparse.FileType('r'), help="name of the xml file or - for stdin")
    parser.add_argument("lyrics", help="add lyrics, syllables separated by whitespace, in a single argument enclosed in quotes")
    args = parser.parse_args()

    lyrics = args.lyrics.decode('UTF-8')
    lyrics = re.sub('[<>()]', '', lyrics)
    lyrics = re.split(r'\s+', lyrics)

    #
    # Parse XML
    #

    root = ET.fromstring(args.xmlfile.read())
    addLyrics(root, lyrics)

    #
    # Output modified XML
    #

#    print """<?xml version="1.0" encoding='UTF-8' standalone='no' ?>
#<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""
    print ET.tostring(root, encoding='UTF-8')

