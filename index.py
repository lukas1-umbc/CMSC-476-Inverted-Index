import matplotlib.pyplot as plt
import html2text
import string
import os
import sys
import time
import math
import re

def tokenizeWords(text, filename, out_path, index, stop_set, file_lengths):

    #statistics
    NUM_TOKENS = 0

    words = text.split()

    for word in words:
        #use regex to split tokens based on special characters and numbers
        good_word_list = re.split("[\W|_|\d]+", word)

        for good_word in good_word_list:
            good_word = good_word.lower()

            #don't want stop words or empty strings
            if good_word not in stop_set and good_word != "":

                if good_word in index:

                    found_file = False
                    #look for current file in word's dictionary
                    for fname in index[good_word]:

                        #found
                        if fname == filename:
                            index[good_word][fname] += 1
                            found_file = True
                            break

                    #add new entry to the word's dictionary if it didn't exist
                    if found_file == False:
                        index[good_word][filename] = 1
                #word was not in the index
                else:
                    index[good_word] = {}
                    index[good_word][filename] = 1
                    NUM_TOKENS += 1

    file_lengths[filename] = len(words)
    return NUM_TOKENS

#return dictionary of all the tokens and their total frequencies
def getTotalFreqs(index):

    total_index = {}
    for token, freq_dict in index.items():
        freq_total = 0
        for filename in freq_dict:
            freq_total += freq_dict[filename]
        total_index[token] = freq_total
    return total_index

#remove all tokens whose frequency is <= the given threshold
def removeLowFreq(index, threshold):

    total_index = getTotalFreqs(index)
    for token, freq in total_index.items():
        if freq <= threshold:
            del index[token]
    return index

#create postings dictionary, outputs postings to a file
def createPostings(out_path, index, file_lengths):

    postings_file = open(out_path + "postings.txt", "w+")

    for token in index:

        #set the value of each document in the token's dictionary to the token's tfidf for that document
        for filename in index[token]:

            #tf*idf = (tf of word in document/length of document) * log(number of documents/number of docs containting word)
            tfidf = (index[token][filename]) * math.log(len(file_lengths)/len(index[token]))
            tfidf = round(tfidf, 5)
            index[token][filename] = tfidf

        #write the filename and weight for that file of each token to postings file
        for filename, weight in index[token].items():
            postings_file.write(filename + ", " + str(weight) + "\n")

    postings_file.close()

def main(argv):

    #statistics
    NUM_DOCS_PROCESSED = 0
    NUM_TOKENS = 0

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True

    #directory paths are command line inputs
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    #start = time.time()

    #create output directory
    os.makedirs(out_path)

    #create set of stopwords
    stop_file = open("stoplist.txt", "r")
    stop_set = set()
    for word in stop_file:
        #take out special characters like apostraphes
        #this will still work since leftover stuff that got split will not be wanted
        stop_word_list = re.split("[\W]+", word)
        for stop_word in stop_word_list:
            stop_set.add(stop_word)
    stop_file.close()

    #dictionary for the tokens and their frequencies for each file
    index = {}
    #dictionary for each file's length
    file_lengths = {}

    #for each HTML input file
    for filename in os.listdir(in_path):

        html_file = open(in_path + filename, "r")
        #strip html
        text = text_maker.handle(html_file.read())

        NUM_TOKENS += tokenizeWords(text, filename, out_path, index, stop_set, file_lengths)

        html_file.close()

        NUM_DOCS_PROCESSED += 1


    #throw out low frequency tokens
    threshold = 1
    index = removeLowFreq(index, threshold)

    createPostings(out_path, index, file_lengths)
    
    print(str(NUM_TOKENS) + " distinct tokens found.")

if __name__ == "__main__":
   main(sys.argv[1:])