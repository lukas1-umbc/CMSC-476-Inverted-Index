import matplotlib.pyplot as plt
import numpy
import html2text
import string
import os
import sys
import time
import re

#tokenizes the words in the text object, adds them to the index
#outputs the number of new tokens
def tokenizeWords(text, filename, out_path, inv_index, stop_set):

    #keep track of how many new tokens there are
    NUM_TOKENS = 0

    #put each string that is separated by a space in the list
    words = text.split()

    #put plain files in output directory
    out_file_name = "plain_" + filename
    out_file_name = out_file_name.strip("html") + "txt"
    plain_file = open(out_path + out_file_name, "w+")

    for word in words:

        #use regex to split tokens based on special characters (\W), underscores, and decimals (\d)
        good_word_list = re.split("[\W|_|\d]+", word)

        for good_word in good_word_list:

            good_word = good_word.lower()
            
            #don't write words that are nothing after being stripped, or any stopwords
            if good_word not in stop_set and good_word != "":
                plain_file.write(good_word + "\n")

                #add words to dictionary, update frequencies
                if good_word in inv_index:
                    inv_index[good_word] += 1
                else:
                    inv_index[good_word] = 1
                    NUM_TOKENS += 1

    plain_file.close()
    return NUM_TOKENS

#remove all tokens whose frequency is less than the given threshold
def removeLowFreq(inv_index, threshold):

    #need copy of the dictionary because we can't delete from a dictionary while iterating through it
    inv_index_copy = inv_index.copy()
    for token, freq in inv_index_copy.items():
        if freq <= threshold:
            del inv_index[token]
    return inv_index

#creates file with list of tokens in alphabetical order
def tokenOrderFile(inv_index):

    token_start = time.time()
    f = open("token_sort.txt", "w")
    for word in sorted(inv_index.keys()):
        f.write(word.strip() + ": " + str(inv_index[word]) + "\n")
    f.close()
    token_end = time.time()
    print("The token-ordered file was created in " + str(token_end - token_start) + " seconds.")

#creates file with list of tokens in order of frequency
def freqOrderFile(inv_index):

    freq_start = time.time()
    g = open("freq_sort.txt", "w")
    for word, freq in sorted(inv_index.items(), key=lambda item: item[1], reverse=True):
        g.write(word.strip() + ": " + str(freq) + "\n")
    g.close()
    freq_end = time.time()
    print("The frequency-ordered file was created in " + str(freq_end - freq_start) + " seconds.")

def graphTimeVSDocs(time_axis, docs_axis):

    fig = plt.figure()
    #line graph - time vs num docs processed
    plt.plot(time_axis, docs_axis)
    fig.suptitle("Number of Documents Processed as a Function of Time")
    plt.xlabel("Time (s)")
    plt.ylabel("# Documents Processed")
    plt.savefig("time_vs_docs.png")

#test to ensure stopwords are not in the index
def testIndex(inv_index, stop_set):

    for stop_word in stop_set:
        if stop_word in inv_index.items():
            print("fail")
        else:
            print("success")

def main(argv):

    time_axis = []

    NUM_DOCS_PROCESSED = 0
    NUM_TOKENS = 0

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True

    #directory paths are command line inputs    
    in_path =  sys.argv[1]
    out_path = sys.argv[2]

    start = time.time()

    #create output directory
    os.makedirs(out_path)
        
    #create set of stopwords
    stop_file = open("stoplist.txt", "r")
    stop_set = set()
    for word in stop_file:
        #stop words have special characters (apostraphe), but the tokens will not
        #should work out because even though "she's" gets split into "she" and "s", "s" is in the stoplist anyway
        #anything leftover like that will not be wanted anyway
        stop_word_list = re.split("[\W]+", word)
        for stop_word in stop_word_list:
            stop_set.add(stop_word)
    stop_file.close()

    #dictionary for all the tokens
    inv_index = {}

    #for each HTML input file
    for filename in os.listdir(in_path):

        file_loc = in_path + filename    
        html_file = open(file_loc, "r")
        html = html_file.read()
        #strip html away
        text = text_maker.handle(html)

        NUM_TOKENS += tokenizeWords(text, filename, out_path, inv_index, stop_set)

        html_file.close()

        NUM_DOCS_PROCESSED += 1
        processed_time = time.time()
        time_axis.append(round(processed_time - start, 2))

    #throw out tokens with frequency of 1
    threshold = 1
    inv_index = removeLowFreq(inv_index, threshold)

    #Make files
    tokenOrderFile(inv_index)
    freqOrderFile(inv_index)
    
    #Make graph
    docs_axis = [num for num in range(1, NUM_DOCS_PROCESSED + 1)]
    graphTimeVSDocs(time_axis, docs_axis)

    print("The program took " + str(time.time() - start) + " seconds to complete.")
    print(str(NUM_TOKENS) + " distinct tokens found.")

if __name__ == "__main__":
   main(sys.argv[1:])