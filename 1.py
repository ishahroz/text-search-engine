import sys
import os
import re
import string
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


def removePunctuations(completeList):
    returnList = []
    for i in range(len(words)):
        if words[i] not in string.punctuation:
            returnList.append(words[i])
    return returnList


def applyStop(stopList, parsedList):
    return [w for w in parsedList if not w in stopList]


def stemText(tokenizedList):
    porter = PorterStemmer()
    stem_sentence = []
    for word in tokenizedList:
        stem_sentence.append(porter.stem(word))
    return stem_sentence


def writeFiles(list1, list2):

    docIDFile = open("docids.txt", "w+", encoding="utf-8")
    termIDFile = open("termids.txt", "w+", encoding="utf-8")

    for key in list1:
        termIDFile.write(str(list1[key]) + "\t" + key + "\n")

    for key in list2:
        docIDFile.write(str(key) + "\t" + list2[key] + "\n")

    docIDFile.close()
    termIDFile.close()


if __name__ == "__main__":

    # DOCS-IDs DICTIONARY
    docsIDs = {}
    docCounter = 0

    # TERM-IDs DICTIONARY
    termsIDs = {}
    termCounter = 0

    # MAIN INDEX (Dictionary)
    invertedIndex = {}

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

        regex = re.compile('[%s]' % re.escape(string.punctuation))          # REMOVING PUNCTUATIONS
        text = regex.sub(' ', parsedText)
        words = word_tokenize(text)                                         # TOKENIZING WORDS (LOWER-CASE)
        filteredWords = applyStop(lineList, words)                          # REMOVE STOP WORDS
        stemmedText = stemText(filteredWords)                               # STEMMING WORDS

        termPositionCounter = 0
        for word in stemmedText:
            if word not in termsIDs:
                termsIDs[word] = termCounter
                # invertedIndex[termCounter] = [1, (docCounter, termPositionCounter)]
                termCounter = termCounter + 1
            # else:
            #     for key in termsIDs:
            #         if termsIDs[key] == word:
            #             invertedIndex[key][0] = invertedIndex[key][0] + 1
            #             invertedIndex[key].append((docCounter, termPositionCounter))
            # termPositionCounter = termPositionCounter + 1
        docCounter = docCounter + 1

    writeFiles(termsIDs, docsIDs)
