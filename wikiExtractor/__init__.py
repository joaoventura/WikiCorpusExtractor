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

from wikiExtractor.wikiExtractor15 import WikiExtractor
from wikiExtractor import wikiExtractor22


# Use WikiExtractor version
WIKIEXTRACTOR_VERSION = "1.5"

# Represents an empty class
class fakeDoc():
    def __init__(self):
        pass

# Export clean text function
def cleanText(text):
    if (WIKIEXTRACTOR_VERSION == "1.5"):
        wkDoc = fakeDoc()
        wkDoc.text = text
        wikiEx = WikiExtractor()
        wikiEx.extract(wkDoc)
        return wkDoc.text
    elif (WIKIEXTRACTOR_VERSION == "2.2"):
        text = wikiExtractor22.clean(text)
        text = '\n'.join(wikiExtractor22.compact(text))
        return text
    return None