import matplotlib.pyplot as plt
import numpy
import html2text
import string
import os
import sys
import time

#tokenizes the words in the text object, adds them to the index
#outputs the number of new tokens
def tokenizeWords(text, filename, out_path, inv_index):

    #keep track of how many new tokens there are
    NUM_TOKENS = 0

    #put each string that is separated by a space in the list
    words = text.split()

    #put plain files in output directory
    out_file_name = "plain_" + filename
    out_file_name = out_file_name.strip("html") + "txt"
    plain_file = open(out_path + out_file_name, "w+")

    for word in words:

        #strip word of special characters and numbers, make it lowercase
        good_word = ''.join(char for char in word if char.isalpha())
        good_word = good_word.lower()

        #don't write the good words that are nothing after being stripped
        if good_word != "":
            plain_file.write(good_word + "\n")

            #add words to dictionary, update frequencies
            if good_word in inv_index:
                inv_index[good_word] += 1
            else:
                inv_index[good_word] = 1
                NUM_TOKENS += 1

    plain_file.close()
    return NUM_TOKENS

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

def main(argv):

    time_axis = []

    NUM_DOCS_PROCESSED = 0
    NUM_TOKENS = 0

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    
    in_path =  sys.argv[1]
    out_path = sys.argv[2]

    start = time.time()

    #create output directory
    os.makedirs(out_path)

    inv_index = {}

    #for each HTML input file
    for filename in os.listdir(in_path):

        file_loc = in_path + filename    
        html_file = open(file_loc, "r")
        html = html_file.read()
        #strip html away
        text = text_maker.handle(html)

        NUM_TOKENS += tokenizeWords(text, filename, out_path, inv_index)

        html_file.close()

        NUM_DOCS_PROCESSED += 1
        processed_time = time.time()
        time_axis.append(round(processed_time - start, 2))

    tokenOrderFile(inv_index)
    freqOrderFile(inv_index)
    
    docs_axis = [num for num in range(1, NUM_DOCS_PROCESSED + 1)]
    graphTimeVSDocs(time_axis, docs_axis)

    print("The program took " + str(time.time() - start) + " seconds to complete.")
    print(str(NUM_TOKENS) + " distinct tokens found.")

if __name__ == "__main__":
   main(sys.argv[1:])