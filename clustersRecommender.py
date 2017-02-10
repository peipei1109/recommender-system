#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 21:23:21 2016

@author: alexandreboyker
"""

import os
import pandas as pd
import numpy as np
import re
from scipy.spatial.distance import pdist
import datetime
import fastcluster


abspath = os.path.abspath('__file__')
dname = os.path.dirname(abspath)
os.chdir(dname)



def buildUtilityMat():
    """read data sets"""
    ratings=pd.io.parsers.read_csv(dname+"/BX-CSV-Dump/BX-Book-Ratings.csv",error_bad_lines=False,delimiter=";") 
    
    books=pd.io.parsers.read_csv(dname+"/BX-CSV-Dump/BX-Books.csv",error_bad_lines=False,delimiter=";") 
    books=books.set_index("ISBN")
    books.index = books.index.values.astype(str)


    users=pd.io.parsers.read_csv(dname+"/BX-CSV-Dump/BX-Users.csv",error_bad_lines=False,delimiter=";") 
    users=users.set_index("User-ID")
    
    utility_Matrix=ratings.pivot_table(index=ratings.columns[0], columns=ratings.columns[1], values=ratings.columns[2])
    utility_Matrix[utility_Matrix>=0]=1
    #utility_Matrix=utility_Matrix.dropna(axis=0,how='all')

    #utility_Matrix=utility_Matrix.dropna(axis=1,how='all')
    print("Utility Matrix Shape: ",utility_Matrix.shape)
    utility_Matrix=utility_Matrix.fillna(0)
    """remove special characters from ISBN"""
    columns=[re.sub("[^\w']|_","",col) for col in utility_Matrix.columns.values ]
    dic_col={}

    for i,col1 in enumerate(utility_Matrix.columns.values):
        dic_col[col1]=columns[i]

    utility_Matrix=utility_Matrix.rename(columns=dic_col)
    
    #non_zero_per_row=(utility_Matrix != 0).astype(int).sum(axis=1)

    #non_zero_per_row.value_counts()

    
    
    return utility_Matrix




def averageNonNull(x):
    somme=sum(x)
    if somme==0:
        return 0
    else:
        return 1
    
def kMeansClusterUtilityItems(U,n_round=8):
    #n_clusters=list(range(2,20))

    
    U_copy=U.copy()
    while n_round>0:
            print("round ",n_round," ongoing")
            print("clustering...")
            n_row=U_copy.shape[1]
            
            start_time= datetime.datetime.now()
            distance = pdist(U_copy.transpose().values,'cosine')
            linkage = fastcluster.linkage(distance,method="complete")
            clusternum =int(n_row*0.5)
            clustdict = {i:[i] for i in range(len(linkage)+1)}
            for i in range(len(linkage)-clusternum+1):
                clust1= int(linkage[i][0])
                clust2= int(linkage[i][1])
                clustdict[max(clustdict)+1] = clustdict[clust1] + clustdict[clust2]
                del clustdict[clust1], clustdict[clust2]
            
            print(datetime.datetime.now()-start_time)

            print("merging...")
            start_time= datetime.datetime.now()
            df=pd.DataFrame(index=U_copy.index)
            eade=0
            for item in clustdict.items():
                if(eade%1000==0):
                    print(eade,"/",len(clustdict.keys())+1," columns done")
                names=(U_copy.ix[:,item[1]].columns.values)
                new_name='-'.join(names)
                eade+=1
                
                df[new_name]=U_copy.ix[:,item[1]].apply(averageNonNull, axis=1).values
            
            del  U_copy
            U_copy=df.copy()
            print(datetime.datetime.now()-start_time)
            print("size of new utility matrix: ",U_copy.shape)
            n_round-=1
                
            
    return  U_copy     

    
def doTheJob():
    
    uMat=buildUtilityMat()

    uMat[uMat==0]=np.nan

    uMat=uMat.dropna(axis=0,how='all')

    uMat=uMat.dropna(axis=1,how='all') 
    uMat=uMat.fillna(0)



    new_U=kMeansClusterUtilityItems(uMat,5)
    clustersofISBN=new_U.columns.values
    file=open(dname+"/clustersOfItems.txt",'wb')
    for clstr in clustersofISBN:
        file.write(str(clstr).encode('utf-8')+b'\n')
        
    file.close()



def getClusters():
    clusters=[]
    file=open(dname+"/clustersOfItems.txt",'rb')
    for line in file:
        line=line.decode("utf-8").split("-")
        line[-1]=re.sub("\\n","",line[-1])
        clusters.append(line)
    return clusters
        
    
def findClusters(listOfIsbn):
    clusters=[]
    cluster_list=getClusters()
    for isbn in listOfIsbn.split(" "):
        for clst in cluster_list:
            if (isbn in clst) and (isbn not in clusters):
                clusters.append(set(clst))
    return (clusters)


def kMeansClusterUtilityUsers(U,n_round=1):

    
    U_copy=U.copy()
    while n_round>0:
            print("round ",n_round," ongoing")
            print("clustering...")
            n_row=U_copy.shape[0]
            
            start_time= datetime.datetime.now()
            distance = pdist(U_copy.values,'cosine')
            linkage = fastcluster.linkage(distance,method="complete")
            clusternum =int(n_row*0.5)
            clustdict = {i:[i] for i in range(len(linkage)+1)}
            for i in range(len(linkage)-clusternum+1):
                clust1= int(linkage[i][0])
                clust2= int(linkage[i][1])
                clustdict[max(clustdict)+1] = clustdict[clust1] + clustdict[clust2]
                del clustdict[clust1], clustdict[clust2]
            
            print(datetime.datetime.now()-start_time)

            print("merging...")
            start_time= datetime.datetime.now()
            
            eade=0
            data=[]
            index=[]
            for item in clustdict.items():
                if(eade%100==0):
                    print(eade,"/",len(clustdict.keys())+1," rows done")
                ind=(U_copy.iloc[np.array(item[1]),:].index.values)
                print(ind)
                index.append(list(ind))
               

                data.append(np.array(U_copy.iloc[np.array(item[1]),:].apply(averageNonNull,axis=0).values))
                eade+=1
            
            df=pd.DataFrame(columns=U_copy.columns,data=data,index=index)
            del  U_copy
            U_copy=df.copy()
            print(datetime.datetime.now()-start_time)
            print("size of new utility matrix: ",U_copy.shape)
            n_round-=1
                
            
    return  U_copy ,clustdict
    
    
    
                