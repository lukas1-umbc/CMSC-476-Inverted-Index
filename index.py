import matplotlib.pyplot as plt
import html2text
import string
import os
import sys
import time
import math
import re

def tokenizeWords(text, filename, out_path, postings_dict, stop_set, file_lengths):

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

                if good_word in postings_dict:

                    found_file = False
                    #look for current file in word's dictionary
                    for fname in postings_dict[good_word]:

                        #found
                        if fname == filename:
                            postings_dict[good_word][fname] += 1
                            found_file = True
                            break

                    #add new entry to the word's dictionary if it didn't exist
                    if found_file == False:
                        postings_dict[good_word][filename] = 1
                #word was not in the postings_dict
                else:
                    postings_dict[good_word] = {}
                    postings_dict[good_word][filename] = 1
                    NUM_TOKENS += 1

    file_lengths[filename] = len(words)
    return NUM_TOKENS

#return dictionary of all the tokens and their total frequencies
def getTotalFreqs(postings_dict):

    total_postings_dict = {}
    for token, freq_dict in postings_dict.items():
        freq_total = 0
        for filename in freq_dict:
            freq_total += freq_dict[filename]
        total_postings_dict[token] = freq_total
    return total_postings_dict

#remove all tokens whose frequency is <= the given threshold
def removeLowFreq(postings_dict, threshold):

    total_postings_dict = getTotalFreqs(postings_dict)
    for token, freq in total_postings_dict.items():
        if freq <= threshold:
            del postings_dict[token]
    return postings_dict

#create postings dictionary, outputs postings to a file
def createIndex(out_path, postings_dict, file_lengths):

    #counter for the line being written to the postings file
    line_num = 0

    #sort postings_dict by token
    postings_dict = dict(sorted(postings_dict.items()))

    index = {}
    #index will have tokens as keys, and a list containing the number of documents
    #containing the token and the location of the first record for the token in the postings file
    index = index.fromkeys(postings_dict.keys(), [0, 0])

    postings_file = open(out_path + "postings.txt", "w+")
    index_file = open(out_path + "index.txt", "w+")

    for token in postings_dict:

        #set the value of each document in the token's dictionary to the token's tfidf for that document
        for filename in postings_dict[token]:

            #tf*idf = (tf of word in document/length of document) * log(number of documents/number of docs containting word)
            tfidf = (postings_dict[token][filename]) * math.log(len(file_lengths)/len(postings_dict[token]))
            tfidf = round(tfidf, 5)
            postings_dict[token][filename] = tfidf

        #in the index, set the number of documents the token occurs in
        index[token][0] = len(postings_dict[token])

        #in the index, set the location of the first record for the token in the postings file 
        index[token][1] = line_num

        #write the filename and weight for that file of each token to postings file
        for filename, weight in postings_dict[token].items():
            postings_file.write(filename + ", " + str(weight) + "\n")
            line_num += 1

        #write the index dictionary contents to the index file
        index_file.write(token + "\n" + str(index[token][0]) + "\n" + str(index[token][1]) + "\n")

    postings_file.close()
    index_file.close()

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
    postings_dict = {}
    #dictionary for each file's length
    file_lengths = {}

    #for each HTML input file
    for filename in os.listdir(in_path):

        html_file = open(in_path + filename, "r")
        #strip html
        text = text_maker.handle(html_file.read())

        NUM_TOKENS += tokenizeWords(text, filename, out_path, postings_dict, stop_set, file_lengths)

        html_file.close()

        NUM_DOCS_PROCESSED += 1


    #throw out low frequency tokens
    threshold = 1
    postings_dict = removeLowFreq(postings_dict, threshold)

    createIndex(out_path, postings_dict, file_lengths)
    
    print(str(NUM_TOKENS) + " distinct tokens found.")

if __name__ == "__main__":
   main(sys.argv[1:])