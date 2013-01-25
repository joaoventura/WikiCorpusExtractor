#!/usr/bin/python
# -*- coding: utf-8 -*-

# ==============================================================================
#  Extracts text from WikiMedia XML Dump files
#  Author: João Ventura (joaojonesventura@gmail.com)
#
# =============================================================================
#  Copyright (c) 2013. João Ventura (joaojonesventura@gmail.com).
# ==============================================================================
#  This file is part of WikiCorpusExtractor.
#
#  WikiCorpusExtractor is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License, version 3,
#  as published by the Free Software Foundation.
#
#  WikiCorpusExtractor is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

import os
import random
from datetime import datetime
import wikiExtractor
from utils import Utils
from tokenizer import Tokenizer


class WikiXMLDumpFile(object):
    
    def __init__(self, filename, encoding = 'UTF-8'):
        self.filename = filename
        self.default_encoding = encoding
        
    #================================================#
    #              FILE AND XML HANDLING             #
    #================================================#
        
    # Returns a file line iterator with the file position of the begin/end of line
    #  Ex: (line, file_pos_begin_line, file_pos_end_line)
    def __XML_read_lines_and_positions__(self):
        fin = Utils.get_file_handler(self.filename, 'r')
        pos = fin.tell()
        for line in fin:
            yield (line, pos, pos+len(line))
            pos += len(line)
        fin.close()
    
    # For each wiki page returns (title, id, text)
    def __XML_iterate_pages__(self):
        # Flags to keep text
        currText = None
        fillText = False
        for (line, startPos, endPos) in self.__XML_read_lines_and_positions__():
            # ignore leading and trailing whitespaces
            line = line.strip()
            # Process the several fields
            if (line.startswith('<page>')):
                revisionTag = False
            elif (line.startswith('<title>') and line.endswith('</title>')):
                title = line[7:-8].replace('&amp;', '&')
            elif (line.startswith('<revision>')):
                revisionTag = True
            elif (line.startswith('<id>') and line.endswith('</id>') and revisionTag is False):
                id = int(line[4:-5])
            elif (line.startswith('</page>')):
                yield (title, id, currText)
            elif (line.startswith('<text')):
                # Clean and start appending the text
                currText = ""
                fillText = True
            elif (line.endswith('</text>') or (line.startswith('<text') and line.endswith('/>'))):
                # Still add final line and stop appending the text
                currText += line
                fillText = False
            # Whether to add to current page text
            if (fillText is True):
                currText += line + "\n"
    
    #================================================#
    #            XML DUMP FILE HANDLING              #
    #================================================#
    
    # Yields wiki documents
    def getWikiDocuments(self):
        for (title, id, text) in self.__XML_iterate_pages__():
            yield WikiDocument(title, id, text)
    
    # Returns a wiki document by title
    def getWikiDocumentByTitle(self, title):
        for wikiDoc in self.getWikiDocuments():
            if (wikiDoc.title == title):
                return wikiDoc
        return None
    
    # Returns a wiki document by id
    def getWikiDocumentById(self, id):
        for wikiDoc in self.getWikiDocuments():
            if (wikiDoc.id == id):
                return wikiDoc
        return None
    
    #================================================#
    #                    CORPUS                      #
    #================================================#
    
    # Selects documents that match some criteria
    def selectDocuments(self, minWordsByDoc, maxWords):
        # Keep titles of documents with the minimum words
        titles = []
        for wkDoc in self.getWikiDocuments():
            if (wkDoc.numWords > minWordsByDoc):
                titles.append((wkDoc.title, wkDoc.numWords))
        # Remove random documents to keep estimated number of words bellow maxWords
        # Estimate reduction for 65% for when wiki text is cleaned and tokenized
        estimatedNumWords = sum([nWords for (title, nWords) in titles]) * 0.65
        while (estimatedNumWords > maxWords):
            # Get a random document
            randPos = random.randint(0, len(titles)-1)
            estimatedNumWords -= (titles[randPos][1] * 0.65)
            del titles[randPos]
        print ("Estimated %s documents with a total of %s words" % (len(titles), estimatedNumWords))
        return titles
        
    # Creates a corpus that matches some criteria for number of documents and letter case
    def createCorpus(self, filename, minWordsByDoc=1000, maxWords=10000000, forceLowerCase=False):
        startTime = datetime.now()
        # Select able documents and clean/tokenize text to a output temp file
        titles = self.selectDocuments(minWordsByDoc, maxWords)
        tmpFilename = filename + ".tmp"
        fout = open(tmpFilename, 'w')
        totWords = 0
        i = 0
        for wkDoc in self.getWikiDocuments():
            if (wkDoc.title in [title for (title, numWords) in titles]):
                wkDoc.cleanText()
                wkDoc.tokenizeText(forceLowerCase)
                print ("%s/%s [%s, %s]" % (i, len(titles), wkDoc.title, wkDoc.numWords))
                fout.write(wkDoc.__str__())
                i += 1
                totWords += wkDoc.numWords
        fout.close()
        # Create output file and copy from the temp file
        fout = open(filename, 'w')
        fout.write('<stats numDocs=%s numWords=%s />\n' % (i, totWords))
        with open(tmpFilename, 'r') as fin:
            fout.writelines(fin.readlines())
        fout.close()
        # Remove temp file
        os.remove(tmpFilename)
        print ("Processed %s docs with %s words in %s." % (i, totWords, datetime.now()-startTime))
            
        
#Represents a Wiki Document
class WikiDocument:

    def __init__(self, title="", id="", text=""):
        self.id = id
        self.title = title
        self.__setText__(text)
        self.isTextRaw = True
        
    # Sets the current text and counts number of words
    def __setText__(self, text):
        self.text = text
        self.numWords = len(self.text.split(None))
        self.isTextRaw = False
        
    # Sets the cleaned wikipedia text as current text
    def cleanText(self):
        self.__setText__(wikiExtractor.cleanText(self.text))
    
    # Tokenizes the current text
    def tokenizeText(self, forceLowerCase=False):
        self.__setText__(Tokenizer().tokenizeText(self.text, forceLowerCase))
    
    # Gets translated title for Wikipedia in other languages
    # Eg. "pt" > Portuguese, "es" > Spanish
    def getTranslatedTitle(self, targetLang):
        if (self.isTextRaw is False):
            raise Exception("Should be done before cleaning text")
        matchStr = "[[%s:" % targetLang
        for line in self.text.split("\n"):
            if (line.startswith(matchStr)):
                return line[len(matchStr) : line.find(']]')]
        return None
    
    def __str__(self):
        return '<doc id="%d" title="%s" numWords="%s">\n%s\n</doc>\n' % \
                    (self.id, self.title, self.numWords, self.text)