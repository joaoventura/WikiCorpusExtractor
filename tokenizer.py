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

#  Implements the following rules for each line:
#   1 - Separates each word and punctuation
#       Ex: Welcome back, my "friend -> ['Welcome', 'back', ',', 'my', '"', 'friend']
#   2 - Handles apostrophes
#       Ex: I'll don't care -> ["I'll", "don't", 'care']
#   3 - Handles minus sign separating words
#       Ex: multi-way of step-by-step -> ['multi-way', 'of', 'step-by-step']
#   4 - Sequences of 1 or 2 letters with first capital followed by a dot are kept joined
#       Ex: Mr. and Ms. Jones -> ['Mr.', 'and', 'Ms.', 'Jones']
#   5 - Handles Sequences like the previous ones but one after the other
#       Ex: Born in the U.S.A. -> ['Born', 'in', 'the', 'U.S.A.']
#   6 - Handles some number sequences as '1.23', '1,232', '3%'


import re
from utils import Utils


class Tokenizer(object):
    "Tokenizes texts"

    def __init__(self, encoding = 'UTF-8'):
        self.default_encoding = encoding
        # creates regular expression patern (alfanumeric groups of characters)
        #
        # ([A-Z][\w]?\.)+ -> Uppercase, followed by 0 or 1 letter/num, followed by
        #                     a dot, can repeat (Ex: Mr., U.S.A., Mr.Mr.Mr.)        
        # (\w+\'\w+) -> words with apostrophes in the middle
        # (\w+(\-\w+)+) -> words with a minus sign in the middle
        # \d+[^\w^\s]\d+%?)+ -> Groups numbers with any non-alphanumeric in the
        #                       middle or in the end (Ex: 2,23.11 or 3.2%)
        # (\d+\%) -> Handles numbers with percentage symbol
        # (\w+) -> groups any sequence of alphanumerics chars (including underscore)
        # (\W+) -> groups anything not alphanumeric
        # The | is interpreted as OR A|B|C|D|E..
        #
        # See: http://www.tutorialspoint.com/python/python_reg_expressions.htm
        # and http://docs.python.org/library/re.html
        self.pattern = re.compile(r"([A-Z][\w]?\.)+|(\w+\'\w+)|(\w+(\-\w+)+)|(\d+[^\w^\s]\d+%?)+|(\d+\%)|(\w+)|(\W+)", re.UNICODE)

    # Tokenizes a line
    def tokenize_line(self, line, lowerCase=False, preserveDocTags=False):
        res = []
        # convert line from default encoding to bytes
        line = line.decode(self.default_encoding)
        # check if line is a <doc> or </doc> and so, return line unchanged
        if ((line.startswith("<doc") or line.startswith("</doc>")) and preserveDocTags is True):
            return line.split()
        # else split by the pattern
        l = self.pattern.finditer(line)
        for match in l:
            # don't include whitespaces
            if (match.group(0) != " "):
                if (lowerCase is True):
                    res.append(match.group(0).strip().lower())
                else:
                    res.append(match.group(0).strip())
        return res

    # Tokenizes a text. 'text' as to be an iterator
    def tokenize(self, text, lowerCase, preserveDocTags):
        for line in text:
            yield self.tokenize_line(line, lowerCase, preserveDocTags)
            
    # Tokenizes a text
    def tokenizeText(self, text, lowerCase=False):
        res = ""
        for line in text.split("\n"):
            res += " ".join(self.tokenize_line(line, lowerCase, preserveDocTags=False)) + "\n"
        return res[:-1] # remove last \n
    
    # Tokenizes an input file
    def tokenize_file(self, filein="stdin", fileout="stdout", lowerCase=False, \
                      preserveDocTags=True):
        # opens the files
        fin = Utils.get_file_handler(filein, "r")
        fout = Utils.get_file_handler(fileout, "w")

        for line in self.tokenize(fin, lowerCase, preserveDocTags):
            # Writes to file encoded in the default encoding
            fout.write(" ".join(line).encode(self.default_encoding))
            fout.write("\n")

        # closes handlers
        fin.close()
        fout.close()
