# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 00:51:42 2020

@author: joaom
"""

print('Prepare_Husky')

import random
import pandas as pd

def remove_columns(file):
    file=file.drop(['League','Date','Time','HT','AT'],axis=1)
    try:
        file=file.drop(['ODDH_Aver.','ODDD_Aver.','ODDA_Aver.'],axis=1)
    except:
        pass
    return file

def train_test_split(file,test_percentage=10,end=False):
    if end:
        size=len(file.index)
        print(size,'size')
        test_size=int((size*test_percentage)/100)
        print(test_size,'test_size')
        Test=file[(-test_size):].reset_index(drop=True)
        Train=file[:(-test_size)].reset_index(drop=True)
        print('len(Test): ',len(Test),'Total len: ',len(Test)+len(Train))
        return Train, Test    
    else:   
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



def Covid_Test(df_Test):
# para eliminar os jogos do intervalo do Covid
    df = df_Test.sort_values(['Date','Time'],ascending=[True,True])
    maxi=[0,0]
    for i in range(len(df)-1):
        ok = ((df.iloc[i]['Date']-df.iloc[i+1]['Date']).days)
        if ok>maxi[0]:
            maxi[0]=ok
            maxi[1]=i+1
    teams = list(np.unique(df['HT']))
    if maxi[1]<30:
        return df
    for t in teams:
        vars()[t]=0
    dropz=[]
    for i in range(maxi[1],len(df)):
        HT = df.iloc[i]['HT']
        AT = df.iloc[i]['AT']
        if (vars()[AT]<5) or (vars()[HT]<5):
            dropz+=[i]
        vars()[AT]+=1
        vars()[HT]+=1
    df = df.drop(dropz,axis=0)
    return df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)