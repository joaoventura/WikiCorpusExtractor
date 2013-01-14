WikiCorpusExtractor is a python library for creating corpora from Wikipedia XML dump files. The target audience are people which need a collection of texts for Language Processing tools.

The output of this library is a text file of the form:

    <doc id="xx" title="Autism">
    Text which is tokenized , i.e., words and punctuation are separated by a space .
    Some special words like step-by-step or U.S.A. are correctly handled .
    </doc>
    <doc id="xxx" title="zzz">
    ...
    </doc>


Usage for building an English corpus (search in the other Wikipedias for other languages)



DOWNLOAD XML DUMP FILE
- Download a wikipedia XML dump file from http://en.wikipedia.org/wiki/Wikipedia:Database_download
- If you want to build a corpus from articles of a specific category, start for searching the category (e.g.: Medicin). Then go to http://toolserver.org/~magnus/catscan_rewrite.php and add the category to the "Categories" text box. Change the depth to something like 2 or 3 (how many subcategories below you want - the depth like in a tree), and in the bottom change to CSV. Save the results to a CSV file, open in LibreOffice Calc and copy the articles' titles. Go to http://en.wikipedia.org/wiki/Special:Export, paste the titles and download the XML dump file with only those articles.



CREATE A CORPUS FROM THE XML DUMP FILE (Python example)

    from wikiXMLDump import WikiXMLDumpFile

    if __name__ == "__main__":

        # Sources
        enSource = 'Resources/sources/EN_Medicine_depth2.xml.bz2'
    
        # Create object
        wk = WikiXMLDumpFile(enSource)
        # Show a document
        wkDoc = wk.getWikiDocumentByTitle('Abortion')
        print wkDoc
        # Print portuguese translation of the title (if available)
        print wkDoc.getTranslatedTitle('pt')
        # Clean wikipedia markup and tokenize the text
        wkDoc.cleanText()
        wkDoc.tokenizeText()
        print wkDoc
        # Create a corpus of about 4M words and a minimum of about 500 words per document
        wk.createCorpus(filename='Resources/corpora/EN_Medicin_corpora.txt', minWordsByDoc=500, maxWords=4000000)

Enjoy! :)
