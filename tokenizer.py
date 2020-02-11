import matplotlib.pyplot as plt
import numpy
import html2text
import string
import os
import sys
import time

def main(argv):

    time_axis = []

    NUM_DOCS_PROCESSED = 0

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    #ignore image stuff
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

        #put each string that is separated by a space in a list
        words = text.split()

        #put plain files in output directory
        out_file_name = "plain_" + filename
        out_file_name = out_file_name.strip("html") + "txt"
        plain_file = open(out_path + out_file_name, "w+")

        for word in words:

            #strip the word of special characters and numbers, make it lowercase
            good_word = ''.join(char for char in word if char.isalpha())
            good_word = good_word.lower()

            #don't print the good_words that are nothing after being stripped
            if good_word != "":
                plain_file.write(good_word + "\n")

                #add words to dictionary, update frequencies
                if good_word in inv_index:
                    inv_index[good_word] += 1
                else:
                    inv_index[good_word] = 1

        html_file.close()
        plain_file.close()

        NUM_DOCS_PROCESSED += 1
        processed_time = time.time()
        time_axis.append(round(processed_time - start, 2))

    #list the words and their frequencies by token
    f = open("token_sort.txt", "w")
    for word in sorted(inv_index.keys()):
        f.write(word.strip() + ": " + str(inv_index[word]) + "\n")
    f.close()

    #list the words and their frequencies by frequency
    g = open("freq_sort.txt", "w")
    for word, freq in sorted(inv_index.items(), key=lambda item: item[1], reverse=True):
        g.write(word.strip() + ": " + str(freq) + "\n")
    g.close()

    docs_axis = [num for num in range(1, NUM_DOCS_PROCESSED + 1)]
    fig = plt.figure()
    #line graph - time vs num docs processed
    plt.plot(time_axis, docs_axis)
    fig.suptitle("Number of Documents Processed as a Function of Time")
    plt.xlabel("Time (s)")
    plt.ylabel("# Documents Processed")
    plt.savefig("time_vs_docs.png")

if __name__ == "__main__":
   main(sys.argv[1:])