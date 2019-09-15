import sys
import os
import re
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


def parseText(dirName, fileName):
    # READING FILE
    soup = BeautifulSoup(open('./' + dirName + '/' + fileName, encoding="utf8", errors='ignore'), 'html.parser')

    # REMOVING STYLES and SCRIPTS
    for script in soup(["script", "style"]):
        script.decompose()

    # EXTRACTING BODY CONTENT
    body = soup.find('body')

    # REMOVE HTML TAGS
    text = body.get_text()

    # BREAKING INTO LINES and REMOVING LEADING and TRAILING SPACES
    lines = (line.strip() for line in text.splitlines())

    # BREAKING MULTI-HEADLINES TO NEW LINE
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # DROPPING BLANK LINES
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # RETURN LOWER-CASE TEXT
    return text.lower()


def applyStop(stopList, parsedList):
    return [w for w in parsedList if not w in stopList]


def stemText(tokenizedList):
    porter = PorterStemmer()
    stem_sentence = []
    for word in tokenizedList:
        stem_sentence.append(porter.stem(word))
    return stem_sentence


if __name__ == "__main__":

    docIDFile = open("docids.txt", "w+")
    termIDFile = open("termids.txt", "w+")

    # DOCS-IDs DICTIONARY
    docsIDs = {}
    docCounter = 0

    # TERM-IDs DICTIONARY
    termsIDs = {}
    termCounter = 0

    # MAIN INDEX
    mainIndex = []

    # READING STOP-LIST
    lineList = [line.rstrip('\n') for line in open('stoplist.txt')]

    # READING CORPUS DIRECTORY NAME
    corpusDirectory = sys.argv[1]
    corpusFiles = os.listdir(corpusDirectory)

    # READING FILES
    for file in corpusFiles:

        # ADDING FILE TO DOCS DICTIONARY
        docsIDs[docCounter] = file

        # PARSING TEXT FROM HTML BODY TAGS
        try:
            parsedText = parseText(corpusDirectory, file)
        except:
            continue

        filteredSentence = re.sub(r'[^\w\s]', '', parsedText)                   # REMOVING PUNCTUATIONS
        words = word_tokenize(filteredSentence)                                 # TOKENIZING WORDS (LOWER-CASE)
        filteredWords = applyStop(lineList, words)                              # REMOVE STOP WORDS
        stemmedText = stemText(filteredWords)                                   # STEMMING WORDS

        for word in stemmedText:
            if word not in termsIDs:
                termsIDs[termCounter] = word
                termIDFile.write(str(termCounter) + "\t" + word + "\n")
                termCounter = termCounter + 1
                # mainIndex.append((docCounter, termCounter))
            # else:
            #     for key in termsIDs:
            #         if termsIDs[key] == word:
            #             mainIndex.append((docCounter, key))

        docIDFile.write(str(docCounter) + "\t" + file + "\n")
        docCounter = docCounter + 1

    docIDFile.close()
    termIDFile.close()

