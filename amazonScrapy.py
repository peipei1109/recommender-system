#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 22:24:37 2017

@author: alexandreboyker
"""
from time import sleep
from amazon.api import AmazonAPI
import os
from string import punctuation
import pandas as pd
from nltk.corpus import stopwords
from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer

ps=PorterStemmer()
stopWords=stopwords.words('english')+[',','.',';','/','+','-',"'s","a","'","__",":","<",">","><","--"]+list(punctuation)




AMAZON_ASSOC_TAG="aboyker-20"
AMAZON_ACCESS_KEY="AKIAJBME4RR2AL2IWKYA"
AMAZON_SECRET_KEY="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"
amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)


books=pd.io.parsers.read_csv(os.getcwd()+"/BX-CSV-Dump/BX-Books.csv",error_bad_lines=False,delimiter=";") 
booksList=list(books["Book-Title"].values)
print(len(booksList))
#booksList=booksList[:5]
bagOfWordsList=[]


errorCnt=0
bookCnt=0
for book in booksList:
    bookCnt+=1
    try:
        results = amazon.search(Keywords = book, SearchIndex = "Books")
    except Exception as e:
        print ('An exception occurred: ', e)
        errorCnt+=1
        continue
    sleep(1.5)
    try:
        file = open('descriptions.tsv','ab')
        file.write( book.encode('utf-8')+b"\t")
        for item in results:
            
            try:
                file.write( item.isbn.encode('utf-8')+b"\t")
            except Exception as e:
                print ('An exception occurred: ', e)
                file.write(b" NONE"+b"\t")
                errorCnt+=1
            try:
                bagOfWords=set([ps.stem(word.lower()) for word in wordpunct_tokenize(item.editorial_review) if word not in stopWords])
                for token in bagOfWords:
                    if token.isalnum():
                        file.write(token.encode('utf-8')+b"-")
            except Exception as e:
                print ('An exception occurred: ', e)
                file.write(b" NONE"+b"\t")
                errorCnt+=1
            break
        file.write( b"\n")
        file.close()
    except:
        errorCnt+=1
        pass
    print(errorCnt," errors for ",bookCnt," books")




