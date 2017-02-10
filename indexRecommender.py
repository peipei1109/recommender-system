import os
from nltk.corpus import stopwords
from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from collections import OrderedDict
import datetime

ps=PorterStemmer()
start_time=datetime.datetime.now()

stop_words=stopwords.words('english')+[',','.',';','/','+','-',"'s",'//','£','...',":"]


# set path to the directory where files are
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

initial_dir=os.getcwd()
#create an index directory to store the inverted index and the vocabulary_to_id file
try:
    os.mkdir('BooksIndex')
except:
    pass

descriptions_path=initial_dir+'/descriptions.tsv'

#create the vocabulary-id-mapping for each book description
file=open(descriptions_path,'rb')
vocabulary=set({})
booksIndex=set({})

cnt=0
for line in file:
    descri=line.decode('utf-8').split("\t")
    title=[ps.stem(word) for word in wordpunct_tokenize(descri[0].lower()) if word not in stop_words ]
    try:
        content=descri[2].split("-")
        content.pop(-1)
    except:
        content=['']
        continue
    bag_of_words=set(content)
    booksIndex.add(descri[1])
    for token in bag_of_words:
        vocabulary.add(token)
    cnt+=1
    #if(cnt==5):break;
file.close()

voc_id_dict={}
#save the voc-id-mapping to a .tsv file
idx=0
words_ID=open(initial_dir+'/BooksIndex/voc_id.tsv','wb')
for item in vocabulary:
    words_ID.write(str(item).encode('utf-8')+b'\t'+str(idx).encode('utf-8')+b'\n')
    voc_id_dict[item]=idx
    idx+=1
words_ID.close()

#create an inverted index in a dictonary
#also create a bag of words dictionary of the form {doc1=[word_id_1,word_id_2,...],...}
#This is useful to perform cosine similarities during the searching process
file=open(descriptions_path,'rb')
data_index = OrderedDict({k: [] for k in voc_id_dict.values()})
bag_of_word_ids=[]
cnt=0
for  line in (file):
    descri=line.decode('utf-8').split("\t")
    bookIndex=descri[1]
    title=[ps.stem(word) for word in wordpunct_tokenize(descri[0].lower()) if word not in stop_words  ]
    try:
        content=descri[2].split("-")
        content.pop(-1)
    except:
        content=['']
        continue
    bag_of_words=set(content)
    bag_of_word_ids=[voc_id_dict[word] for word in bag_of_words]
    [data_index[(tokenIndex)].append(str(bookIndex)) for tokenIndex in bag_of_word_ids]
    cnt+=1
    #if(cnt==5):break
file.close()

error_empty=0  

#store the inverted index into a .tsv file
inverted_index=open(initial_dir+'/BooksIndex/inverted_index.tsv','wb')
for item in data_index.items():
    
    inverted_index.write(str(item[0]).encode('utf-8')+b'\t')
    [inverted_index.write(str(doc).encode('utf-8')+b'\t') for doc in item[1][:-1]]
    try:
        inverted_index.write(str(item[1][-1]).encode('utf-8')+b'\n')
    except Exception as e:
        print(str(e))
inverted_index.close()


#store the bag of words index into a .tsv file
bag_of_words=open(initial_dir+'/BooksIndex/bag_of_words_index.tsv','wb')
file=open(descriptions_path,'rb')
cnt=0    
for  line in (file):
    descri=line.decode('utf-8').split("\t")
    #print(descri)
    bookIndex=descri[1]
    
    title=[ps.stem(word) for word in wordpunct_tokenize(descri[0].lower()) if word not in stop_words  ]
    try:
        content=descri[2].split("-")
        content.pop(-1)
    except:
        content=['']
        continue
    content=set(content)
    bag_of_word_ids=[voc_id_dict[word] for word in content]
    bag_of_words.write(str(bookIndex).encode('utf-8')+b'\t')
    [bag_of_words.write(str(doc).encode('utf-8')+b'\t') for doc in bag_of_word_ids[:-1]]
    try:
        bag_of_words.write(str(bag_of_word_ids[-1]).encode('utf-8')+b'\n')
    except Exception as e:
        bag_of_words.write(b'\n')
        #print(str(e))
    cnt+=1
    #if(cnt==5):break
bag_of_words.close()

print("Execution time: ",datetime.datetime.now()-start_time)

