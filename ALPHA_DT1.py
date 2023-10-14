# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 16:00:39 2020

@author: joaom
"""
import random
import pandas as pd

def odd_to_file(path,odd):
    o=round(odd*100)
    ind=int((o-100)//10)+1
    file=pd.read_excel(path+'.xlsx',ind)
    return file


def prepare_df(file):
    file=file.drop(['Div','Date','LO_Team','HO_Team','LowOdd'],axis=1)
    return file

def train_test_split(file,test_percentage=10):
    size=len(file.index)
    print(size,'size')
    test_size=int((size*test_percentage)/100)
    print(test_size,'test_size')
    limit=size-test_size
    print(limit)
    test_ind=random.randrange(0,limit)
    print(test_ind,test_ind+test_size)
    Test=file[test_ind:(test_ind+test_size)].reset_index(drop=True)
    Train=pd.concat([file[:test_ind],file[(test_ind+test_size):]],sort=False).reset_index(drop=True)
    return Train, Test


def round_type1(odd):
    i=int(odd)
    Y=odd-i
    if Y>=0.75:
        return (i+1)
    elif Y<0.25:
        return (i)
    else:
        return (i+0.5)
    
def round_odd(file,odd):
    size=len(file.index)
    new_draw=[]
    new_high=[]
    if 1<=odd<=1.3:
         for i in range(size):
                new_draw+=[round(file.iloc[i]['DrawOdd'])]
                new_high+=[round(file.iloc[i]['HighOdd'])]
    elif 1.4<=odd<=1.6:
        for i in range(size):
            new_draw+=[round_type1(file.iloc[i]['DrawOdd'])]
            new_high+=[round(file.iloc[i]['HighOdd'])]
    else:
        for i in range(size):
            new_draw+=[round_type1(file.iloc[i]['DrawOdd'])]
            new_high+=[round_type1(file.iloc[i]['HighOdd'])]
        
    file['DrawOdd']=new_draw
    file['HighOdd']=new_high
    return file


print('Este módulo serve para extrair o Train/Test de um file de dados Alpha')