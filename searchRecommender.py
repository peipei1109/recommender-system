import os
from nltk.corpus import stopwords
from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from collections import OrderedDict,Counter
import datetime
import re
import operator
import numpy as np

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

initial_dir=os.getcwd()

ps=PorterStemmer()

stop_words=stopwords.words('english')+[',','.',';','/','+','-',"'s"]
#set paths
voc_path=initial_dir+'/BooksIndex/voc_id.tsv'
index_path=initial_dir+'/BooksIndex/inverted_index.tsv'
doc_path=initial_dir+'/descriptions.tsv'
bag_of_word_path=initial_dir+'/BooksIndex/bag_of_words_index.tsv'

words_ID_file=open(voc_path,'rb')
words_ID={}
for line in words_ID_file:
    items=line.decode('utf-8').split('\t')
    words_ID[items[0]]=(re.sub('\\n','',items[1]))
    
words_ID_file.close()


def search(queries,threshold=0.5):
    
    bag_of_words=set([ps.stem(word.lower()) for word in wordpunct_tokenize(queries) if word not in stop_words])
    words_ids=[words_ID[word] for word in bag_of_words if word in words_ID.keys()]
    query_bag_of_word=words_ids.copy()
    length_query=len(words_ids)
    
    if length_query==0:
        return([])
    inverted_index=open(index_path,'rb')
    res=[]
    #we want to find all documents containing at least one of the query words
    for line in inverted_index:
        word_id=line.decode('utf-8').split('\t')[0]
        if word_id  in words_ids:
            res.append([re.sub('\\n','',item) for item in line.decode('utf-8').split('\t')[1:]])
            words_ids.remove(word_id)
        else:
            continue
    inverted_index.close()
    word_cnt={}
    thresholded_results=[]
   
    for items in res:
            for item in set(items):
                
                try:
                    word_cnt[item]+=1
                except:
                    word_cnt[item]=1
    #each document must contain at least  threshold*100% of the query word
    for item in word_cnt.items():
            if item[1]>=length_query*threshold:
                thresholded_results.append (item[0])
             
    # we want to compute cosine similarity measures between the query words and the results
    bag_of_word_index=open(bag_of_word_path,'rb')
    bag_of_word_dic={}
    length_doc=0
    #here we express each book description which passed the threshold criterion by its bag of word in a dict {recipe_id:[bag of words]}
    for line in bag_of_word_index:
        doc_id=line.decode('utf-8').split('\t')[0]
        length_doc+=1
        if doc_id  in thresholded_results:
            bag_of_word_dic[doc_id] =[re.sub('\\n','',item) for item in line.decode('utf-8').split('\t')[1:]]
            thresholded_results.remove(doc_id)
        else:
            continue
    bag_of_word_index.close()
    cos_similarity={}
    set_query=set(query_bag_of_word)
    #here we compute the cosine similarity measure
    for item in bag_of_word_dic.items():
        cos_similarity[item[0]]=(len(set_query.intersection(item[1])))/np.sqrt((len(item[1])*len(query_bag_of_word)))
    sorted_results=sorted(cos_similarity.items(), key=operator.itemgetter(1),reverse=True)
    #print(sorted_results)
    #results are sorted, highest similiraty measures first
    sorted_results =[tup[0] for tup in sorted_results]
    return sorted_results


#print(search(" modern-europ-forc-idea-bloodiest-myth-six-battl-normandi-campaign-declassifi-diari-day-plan-western-written-clearli-militari-strategi-intens-went-detail-took-dare-war-document-two-invas-person-map-happen-eventu-wrong-cross ",threshold=.2))
def findContentbyIsbn(isbnList,threshold=0.3 ):
    isbnList=isbnList.split(" ")
    file=open(doc_path,'rb')
    cnt=0
    key_words=""
    for line in file:
        cnt=cnt+1

        isbn=line.decode('utf-8').split("\t")[1]
        if isbn in isbnList:
         
            key_words+=line.decode('utf-8').split("\t")[2]
        
    file.close()
    
    result= search(key_words,threshold=threshold)
    for isbn_ in isbnList:
        try:
            result.remove(isbn_)
        except:
            pass
    return result
    
    
def findContentByKeywords(keywords,threshold=0.3 ):
     
        result= search(keywords,threshold=threshold)
        return result
 
     
    
    
    
    
    
    
    
    
    