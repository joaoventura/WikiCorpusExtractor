#!/usr/bin/python
# -*- coding: utf-8 -*-

# ==============================================================================
#  Extracts text from WikiMedia XML Dump files
#  Author: João Ventura (joaojonesventura@gmail.com)
#
# =============================================================================
#  Copyright (c) 2014. João Ventura (joaojonesventura@gmail.com).
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
import sys
from bz2 import BZ2File
from zipfile import ZipFile


class Utils(object):
    "Provides utilities for the Wiki Corpus Extractor"

    # Properties
    encoding = 'UTF-8'

    #Returns a file handler
    @staticmethod
    def get_file_handler(filename, mode):
        #Check if is stdin or stdout
        if (filename == "stdin"):
            return sys.stdin
        elif (filename == "stdout"):
            return sys.stdout
        #Opens the file based on filetype
        filetype = os.path.splitext(filename)[1]
        if (filetype == ".bz2"):
            file = BZ2File(filename, mode)
        elif (filetype == ".zip"):
            file = ZipFile(filename, mode)
        else:
            file = open(filename, mode)
        return file

    #Returns all the files in a given directory
    @staticmethod
    def _files(dir, base = ""):
        #Get the contents of a directory
        filelist = os.listdir(dir)
        #For each content (file and dir)
        for content in filelist:
            #Build the path
            path = os.path.join(dir, content)        
            #if is file, return the tuple (base, filename, filepath)
            if (os.path.isfile(path)):
                yield(base, content, path)
            #else, explore the path and return the files inside
            elif (os.path.isdir(path)):
                for f in Utils._files(path, os.path.join(base, content)):
                    yield f

    #Recursively adds text files on a path into a single file
    @staticmethod
    def append_dir_files_into_one(dir, out):
        #Create the output file
        fout = Utils.get_file_handler(out, 'w')
        id = 0
        #For every file inside the path
        for (base, filename, filepath) in Utils._files(dir):
            #opens the file
            fin = Utils.get_file_handler(filepath, 'r')
            #writes the header
            fout.write('<doc id="%s" title="%s_%s">\n' % \
                (id, base.replace('/','_').replace('\\','_'), filename))
            #copies each line
            for line in fin:
                fout.write("%s" % line)
            #writes the footer
            fout.write('</doc>\n')
            id += 1