import matplotlib.pyplot as plt
import string
import os
import sys
import time
import math
import re

#compute cosine similarity scores for each document
def cosineSimilarity(index, postings, query):

    query_vector = [1 for token in query]
    weights_dict = {}
    cosine_dict = {}

    doc_set = set()

    for token in query:

        #location of first entry in postings list for the token
        postings_start = index[token][1]
        #number of documents that contain the token
        postings_len = index[token][0]

        weights_dict[token] = {}
    
        for i in range(postings_start, postings_start + postings_len):
            
            pair = postings[i].split(", ")
            pair[1] = float(pair[1])

            weights_dict[token][pair[0]] = pair[1]

            doc_set.add(pair[0])

    #NEED THE WEIGHTS OF EACH TOKEN FOR EACH DOCUMENT
    doc_vectors = {}
    for doc in doc_set:
        doc_vectors[doc] = []
        for token in weights_dict:
            if doc in weights_dict[token]:
                doc_vectors[doc].append(weights_dict[token][doc])
            else:
                doc_vectors[doc].append(0)
        
        #numerator
        cosine_dict[doc] = sum(doc_vectors[doc][i] * query_vector[i] for i in range(len(query_vector)))
        #denominator
        norm1 = sum(math.pow(doc_vectors[doc][i], 2) for i in range(len(query_vector)))
        norm1 = math.sqrt(norm1)
        norm2 = sum(math.pow(query_vector[i], 2) for i in range(len(query_vector)))
        norm2 = math.sqrt(norm2)
        #cosine similarity score
        cosine_dict[doc] = cosine_dict[doc] / (norm1 * norm2)

    return cosine_dict

#remove stopwords, convert to lowercase, remove tokens with length 1
#not the most efficient but queries will be fairly small
def preprocessQuery(query):

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

    good_query = []
    for token in query:
        token = token.lower()
        if len(token) > 1 and token not in stop_set:
            good_query.append(token)

    return good_query

def main(argv):
    
    start = time.time()

    #take in query words
    query = sys.argv
    query.remove("retrieve.py")

    #preprocess the query's tokens
    query = preprocessQuery(query)
    
    index_file = open("E:/UMBC/CMSC/CMSC 476 - Information Retrieval/proj1/output_dir/index.txt", "r")
    lines = index_file.readlines()

    #each line in index.txt that is a token
    token_lines = list(map(lambda x: x.strip(), lines[0::3]))
    #each line in index.txt that is the number of documents that contain the token
    docs_lines = list(map(lambda x: x.strip(), lines[1::3]))
    #each line in index.txt that is the line number of the first record for the token in postings.txt
    record_lines = list(map(lambda x: x.strip(), lines[2::3]))

    #recreate the index
    index = {}
    for i in range(0, len(token_lines)):
        index[token_lines[i]] = [int(docs_lines[i]), int(record_lines[i])]

    index_file.close()

    #recreate postings structure
    postings_file = open("E:/UMBC/CMSC/CMSC 476 - Information Retrieval/proj1/output_dir/postings.txt", "r")
    lines = postings_file.readlines()
    postings = [line.strip() for line in lines]
    postings_file.close()

    #check if the tokens in the query are in the documents at all
    for token in query:
        if token not in index:
            query.remove(token)
    if len(query) == 0:
        print("No results found.")
        return

    cosine_dict = cosineSimilarity(index, postings, query)

    #print 10 highest cosine similarity scores
    score_num = 0
    for doc, cosine_sim in sorted(cosine_dict.items(), reverse = True, key = lambda item: item[1]):
        if score_num >= 10:
            break
        print(doc + " " + str(round(cosine_sim, 5)))
        score_num += 1

    print("Results retrieved in " + str(time.time() - start) + " seconds.")

if __name__ == "__main__":
   main(sys.argv[1:])
