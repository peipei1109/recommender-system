#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 21:26:03 2017

@author: alexandreboyker
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import time
import datetime
import random

abspath = os.path.abspath('__file__')
dname = os.path.dirname(abspath)
os.chdir(dname)

ratings=pd.io.parsers.read_csv(dname+"/BX-CSV-Dump/BX-Book-Ratings.csv",error_bad_lines=False,delimiter=";") 
ratings["Book-Rating"]=ratings["Book-Rating"]/2

#ratings=ratings.head(800)





def splitData(df, test_size=0.2):

    test_data=[]
    df=df.pivot_table(index=df.columns[0], columns=df.columns[1], values=df.columns[2])
    df.index = df.index.map(str)
    df.columns = df.columns.map(str)
    global index_,columns_

    index_= df.index 
    columns_= df.columns
    df=df.fillna(0)
    train_matrix=(df.values)
    index_=df.index
    columns_=df.columns
    uu,ii = train_matrix.nonzero()
    non_zero_entries=list(zip(uu,ii))
    number_non_zero_entries=len(non_zero_entries)
    random_idx=random.sample(range(1, number_non_zero_entries-1), int(test_size*number_non_zero_entries))
    test_indices=[non_zero_entries[idx]   for idx in random_idx]
    for idx in test_indices:
        rating=train_matrix[idx[0],idx[1]]
        test_data.append([idx[0],idx[1],rating])
        train_matrix[idx[0],idx[1]]=0
            
    return train_matrix,test_data,index_,columns_ 

def theshold(x):
    if x>5:
        return 5
    elif x<0:
        return 0
    else:
        return x

def doCV(df,epochs=15,cvRounds=1,dimensions=4,
         learning_rate=0.003,regularization_rate=0.15):
  
    print("Computing Low Rank Approximation of Rating Matrix...")
    for cvRound in list(range(0,cvRounds)):
             
        train_matrix,test_data,index_,columns_ =splitData(df, test_size=0.1)
        nUsers=train_matrix.shape[0]
        nItems=train_matrix.shape[1]
        pMat =2 * np.random.rand(nUsers,dimensions) 
        qMat= 2* np.random.rand(nItems,dimensions)

   
        uu,ii = train_matrix.nonzero()

        non_zero_entries=zip(uu,ii)
        rmse_list=[]
        train_error_list=[]
        print("")
        for epoch in list(range(0,epochs)):
            print("epoch", epoch+1,"/",epochs)
            non_zero_entries=zip(uu,ii)
            train_error=[]
            for u,i in non_zero_entries:
                
                error=train_matrix[u][i]-theshold(np.dot(pMat[u],qMat[i]))
                pMat[u]=pMat[u]+learning_rate*(error*qMat[i]-regularization_rate*pMat[u])
                qMat[i]=qMat[i]+learning_rate*(error*pMat[u]-regularization_rate*qMat[i])
                train_error.append(error**2)
            low_rank_matrix=np.dot(pMat,qMat.T)
            low_rank_matrix[low_rank_matrix>5]=5
            low_rank_matrix[low_rank_matrix<0]=0
            train_error_list.append(np.sqrt(sum(train_error)/len(train_error)))
            rmse=[]
            
            for row in test_data:
                if(row[2]>0):
                    

                    error=(low_rank_matrix[row[0]][row[1]]-row[2])**2
                    rmse.append(error)
            rmse=sum(rmse)/len(rmse)
            rmse_list.append(np.sqrt(rmse))
        
        plt.plot(list(range(epochs)), train_error_list, marker='o',color='red', label='Training Data');
        plt.plot(list(range(epochs)), rmse_list, marker='x',color='blue', label='Validation Data')
        plt.title('Training and validation error')
        plt.xlabel('Number of Epochs');
        plt.ylabel('rmse');
        plt.legend()
        plt.grid()
        plt.show()
        out_=pd.DataFrame(data=low_rank_matrix,index=index_,columns=columns_)
                
    return out_

def recommendForUser(df,userId):
    numerOfResults=20
    s=df.loc[str(userId)]
    return random.sample(s.nlargest(numerOfResults).index.tolist(),numerOfResults-5)
    
        
#
#low_rank_matrix=doCV(ratings,epochs=30,cvRounds=1)  
#
#low_rank_matrix=pd.DataFrame(data=low_rank_matrix, index=index_,columns=columns_) 
#
##low_rank_matrix.to_csv("lowRankMatrix.csv",index=False)
#
#
#
#        
#low_rank_matrix_rounded=low_rank_matrix.round(0)
#
#low_rank_matrix_rounded.iloc[:,2999].value_counts()
#low_rank_matrix_rounded.shape
#size_in_bytes=sum(low_rank_matrix_rounded.memory_usage())/1000000000
#
