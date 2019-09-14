import sys
import os
import re
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


def parseText(dirName, fileName):
    # READING FILE
    soup = BeautifulSoup(open('./' + dirName + '/' + fileName), 'html.parser')

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

    # READING STOP-LIST
    lineList = [line.rstrip('\n') for line in open('stoplist.txt')]

    # READING CORPUS DIRECTORY NAME
    corpusDirectory = sys.argv[1]
    corpusFiles = os.listdir(corpusDirectory)

    # READING FILES
    for file in corpusFiles:
        filteredSentence = re.sub(r'[^\w\s]', '', parseText(corpusDirectory, file))     # REMOVING PUNCTUATIONS
        words = word_tokenize(filteredSentence)                                         # TOKENIZING WORDS (LOWER-CASE)
        filteredWords = applyStop(lineList, words)                                      # REMOVE STOP WORDS
        stemmedText = stemText(filteredWords)                                           # STEMMING WORDS
        print(stemmedText)
        break
