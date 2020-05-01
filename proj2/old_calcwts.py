import matplotlib.pyplot as plt
import html2text
import llist
import string
import os
import sys
import time
import re

#tokenizes the words in the text object, adds them to the index
#each token in the index has a linked list of tuples that contain a filename and the frequency of the token in that file
def tokenizeWithWeights(text, filename, out_path, inv_index, stop_set):
    #keep track of how many new tokens there are
    NUM_TOKENS = 0

    #put each string that is separated by a space in the list
    words = text.split()

    for word in words:

        #use regex to split tokens based on special characters (\W), underscores, and decimals (\d)
        good_word_list = re.split("[\W|_|\d]+", word)

        for good_word in good_word_list:

            good_word = good_word.lower()
            
            #don't write words that are nothing after being stripped, or any stopwords
            if good_word in inv_index:

                node_num = 0 #llist iterator
                has_node = False

                #loop through good_word's list to look for current file
                while node_num < inv_index[good_word].size and has_node == False:

                    #if the current file is found
                    if inv_index[good_word][node_num][0] == filename:
                        #increment frequency for the file
                        inv_index[good_word][node_num] = (filename, inv_index[good_word][node_num][1]+1)
                        has_node = True
                    else:
                        node_num += 1

                if has_node == False:
                    inv_index[good_word].append((filename, 1))

            else:

                freq_list = llist.dllist()
                #elements of llist are tuples of the filename and the frequency for that file
                freq_list.append((filename, 1))
                #good word not in the index so add it and give it a list
                inv_index[good_word] = freq_list

                NUM_TOKENS += 1
    
    #need weight files
    #put weight files in output directory
    out_file_name = "weighted_" + filename
    out_file_name = out_file_name.strip("html") + "txt"
    weighted_file = open(out_path + out_file_name, "w+")

    for token in inv_index:
        found_file = False
        node_num = 0
        tfidf = 0
        while found_file == False:
            if inv_index[token][node_num][0] == filename:
                tfidf = inv_index[token][node_num][1]
                found_file = True
            else:
                node_num += 1

    weighted_file.close()
    return NUM_TOKENS

#remove all tokens whose frequency is less than the given threshold
def removeLowFreq(inv_index, threshold):

    total_index = getTotalFreqs(inv_index)
    for token, freq in total_index.items():
        if freq <= threshold:
            del inv_index[token]
    return inv_index

#gets the total frequencies for each token and returns a dictionary of them
def getTotalFreqs(inv_index):

    total_index = {}
    for token, freq_list in inv_index.items():
        freq_total = 0
        for node in freq_list:
            freq_total += node[1]
        total_index[token] = freq_total
    return total_index

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

    NUM_FILES = len(os.listdir(in_path))

    #for each HTML input file
    for filename in os.listdir(in_path):

        file_loc = in_path + filename    
        html_file = open(file_loc, "r")
        html = html_file.read()
        #strip html away
        text = text_maker.handle(html)

        NUM_TOKENS += tokenizeWithWeights(text, filename, out_path, inv_index, stop_set)

        html_file.close()

        NUM_DOCS_PROCESSED += 1
        processed_time = time.time()
        time_axis.append(round(processed_time - start, 2))

    #throw out tokens with frequency of 1
    threshold = 1
    inv_index = removeLowFreq(inv_index, threshold)

    
    
    #Make graph
    #docs_axis = [num for num in range(1, NUM_DOCS_PROCESSED + 1)]
    #graphTimeVSDocs(time_axis, docs_axis)

    print("The program took " + str(time.time() - start) + " seconds to complete.")
    print(str(NUM_TOKENS) + " distinct tokens found.")

if __name__ == "__main__":
   main(sys.argv[1:])