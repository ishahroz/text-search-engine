import sys
import os
import re
import string
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


def takeFirst(elem):
    return elem[0]


def takeThird(elem):
    return elem[2]


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


def searchInHashMap(listo, invlisto, term):
    if term in listo:
        termID = listo[term]
        if termID in invlisto:
            tempoList = invlisto[termID]
            print("Listing for term: " + term)
            print("TERMID: " + str(termID))
            print("Number of documents containing term: " + str(tempoList[1]))
            print("Term frequency in corpus: " + str(tempoList[0]))


def mergeInvList(listo):
    retList = []
    prevTermId = listo[0][0]
    retList.append(prevTermId)
    retList[prevTermId] = [(listo[0][1], listo[0][2])]
    for tupleo in listo:
        if tupleo[0] == prevTermId:
            retList[prevTermId].append((tupleo[1], tupleo[2]))
        else:
            prevTermId = tupleo[0]
            retList.append(prevTermId)
            retList[prevTermId] = [(tupleo[1], tupleo[2])]
    return retList


def removePunctuations(completeList):
    returnList = []
    for i in range(len(words)):
        if words[i] not in string.punctuation:
            returnList.append(words[i])
    return returnList


def applyStop(stopList, parsedList):
    return [w for w in parsedList if not w in stopList]


def deltaEncode(invertedList):
    for key in invertedList:
        postingList = invertedList[key]
        for i in range(len(postingList)):
            if i == 0 or i == 1:
                continue
            if i == 2:
                prevDoc = postingList[i][0]
                prevPos = postingList[i][1]
            else:
                currDoc = postingList[i][0]
                currPos = postingList[i][1]
                currPosting = list(postingList[i])
                currPosting[0] = currDoc - prevDoc
                if currDoc == prevDoc:
                    currPosting[1] = currPos - prevPos
                else:
                    postingList[1] = postingList[1] + 1
                    currPosting[1] = currPos
                postingList[i] = tuple(currPosting)
                prevDoc = currDoc
                prevPos = currPos


def stemText(tokenizedList):
    porter = PorterStemmer()
    stem_sentence = []
    for word in tokenizedList:
        stem_sentence.append(porter.stem(word))
    return stem_sentence


def writeEncodedFile(invertedList):
    invFile = open("term_index1.txt", "w+", encoding="utf-8")
    for key in invertedList:
        invFile.write(str(key) + " ")
        postingList = invertedList[key]
        for i in range(len(postingList)):
            if i == 0 or i == 1:
                invFile.write(str(postingList[i]) + " ")
            else:
                invFile.write(str(postingList[i][0]) + "," + str(postingList[i][1]) + " ")
        invFile.write("\n")
    invFile.close()

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

    # TERM-IDs LIST
    termIDss = []

    # MAIN INDEX (Dictionary)
    invertedIndex = {}

    invList = []

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

            # =============== WITH HASH-MAP ==============

            # if word not in termsIDs:
            #     termsIDs[word] = termCounter
            #     invertedIndex[termCounter] = [1, 0, (docCounter, termPositionCounter)]
            #     termCounter += 1
            # else:
            #     tempList = invertedIndex[termsIDs[word]]
            #     tempList[0] += 1
            #     tempList.append((docCounter, termPositionCounter))

            # =================== WITHOUT HASH-MAP ===================

            if word not in termIDss:
                termIDss.append(word)
                invList.append((termCounter, docCounter, termPositionCounter))
                termCounter += 1
            else:
                invList.append((termIDss.index(word), docCounter, termPositionCounter))


            termPositionCounter += 1

        docCounter += 1
        if docCounter == 20:
            break

    invList.sort(key=takeFirst)

    print(invList)

    invvList = mergeInvList(invList)

    print(invvList)

    # deltaEncode(invertedIndex)
    #
    # writeEncodedFile(invertedIndex)

    # writeFiles(termsIDs, docsIDs)

    # =================== SEARCH IN INVERTED INDEX ==================
    # try:
    #     if sys.argv[2] == "--term":
    #         try:
    #             searchInHashMap(termsIDs, invertedIndex, sys.argv[3])
    #         except:
    #             exit()
    # except:
    #     exit()
