import html2text
import string
import os

def main():

    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    #ignore image stuff
    text_maker.ignore_images = True
    
    in_path = input("Enter the path to the directory of HTML files, ending with a forward slash (/): ")
    out_path = input("Enter the path to the directory where the plain files will be stored, ending with a forward slash (/): ")

    #create output directory
    os.makedirs(out_path)

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
        plain_file = open(out_path + out_file_name, "w")

        for word in words:

            #strip the word of special characters and numbers
            good_word = ''.join(char for char in word if char.isalpha())

            #don't print the good_words that are nothing after being stripped
            if good_word != "":
                #print(good_word.lower())
                plain_file.write(good_word + "\n")

        html_file.close()
        plain_file.close()

main()