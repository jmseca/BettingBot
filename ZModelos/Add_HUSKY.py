#!/usr/bin/env python
# coding: utf-8

# # Husky
# Novo folha de dados para ML, que mantém os do ALPHA e acrescenta alguns com os dados extraídos do Understats e SkySports (u+Sky)

# In[2]:


import pandas as pd
#import xlwings as xw
#import openpyxl as op
import numpy as np
import datetime as dt
import numpy as np
import os
import math

print('Neste modelos vamos fazer uma experiência e não usar Odds')
print('Em vex disso, usamos os xPTS para calcular o "power" de uma equipa')


# In[3]:


#Muito Importante
Teams={'Prem':20,'LL':20,'L':20,'SA':20,'LP':18,'Bund':18,'Ered':18}


# In[4]:


pd.set_option('display.max_rows',2000)
pd.set_option('display.max_columns',1000)


# # Funções auxiliares
# Algumes vêm no python Notebook

# `new_find_data()` o find_data, para os ficheiros New

# In[5]:


def new_find_data(os_path):
    lista=os.listdir(os_path)
    data_newfiles=[]
    for i in lista:
        if (i[-3:]=='___') and (i[:3].lower()=='new'):
            data_newfiles+=[i]
    print(data_newfiles)
    return data_newfiles


# In[6]:


def season_index(path,season): #damos o path e a época e devolve o índice do listdir
    seas=str(season)
    seas=seas[-2:]
    lista=os.listdir(path)
    i=0
    found=False
    while i<len(lista) and not(found):
        if lista[i][-7:-5]==seas:
            found=True
        else:
            i+=1
    if not(found):
        print('Esta season não existe')
        raise('Meh')
    return i


# `round_down` arredonda (para os números decimais que quisermos) para baixo

# In[7]:


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


# In[8]:


round_down(1.39,1)


# In[9]:


def check_wrongdate(file,sheet=0):
    #file=pd.read_excel(path+'.xlsx',sheet)
    limit=len(file.index)
    over_month=0
    month2=0
    counter=0
    counter_pd=0
    for i in range(1,limit): #ao começar no 1, temos sempre um valor anterior para comparar, se começasse no zero, comparava com o último valor [-1]
        day_=file.iloc[i]['Date']
        day2=file.iloc[i-1]['Date']
        if isinstance(day_,dt.datetime):
            counter+=1
            if isinstance(day2,str):
                if len(day2)==10:
                    date_str=dt.datetime.strptime(day2,"%d/%m/%Y")
                elif len(day2)==8:                                        #serve para datas qnão têm '20' (2/3/15)
                    day2=day2[:6]+"20"+day2[6:]
                    date_str=dt.datetime.strptime(day2,"%d/%m/%Y")
                else: 
                    print("Oops! Algo está a falhar na função date, qnd a data é uma string!")
                if ((day_.month)-(date_str.month)!=1) and ((day_.month)-(date_str.month)!=0):
                    over_month=1 #qnd muda de str para datetime, e estão trocados mes e dia a diferença entre os meses é estranha (diferente de 1)
            elif isinstance(day2,dt.datetime):
                if (day2.day==day_.day) and (day2.month!=day_.month):
                    #este if é para 'apanhar' qnd troca mes com dia, então o dia é igual, mas o mês muda em linhas consecutivas
                    month2=1
        elif isinstance(day_,pd.Timestamp):
            counter_pd+=1
    if (over_month+month2)==2:
        return (True, 
               str(counter)+' Datas em Datetime',
               str(counter_pd)+' Datas em Timestamp')
    else:
        return (False, 
               str(counter)+' Datas em Datetime',
               str(counter_pd)+' Datas em Timestamp',
               'over_month = '+str(over_month),
               'month2 = '+str(month2))

def swap_datetime(date):
    return dt.datetime.strptime((dt.datetime.strftime(date,'%Y/%d/%m')),'%Y/%m/%d')

def all_datetime(path,sheet=0,write=True): #se write=True, escreve o ficheiro nos Documentos do PC
    #false, dá-nos apenas o ficheiro já tratado aqui no python
    file=pd.read_excel(path+'.xlsx',sheet)
    limit=len(file.index)
    for it in range(0,limit):    
        if isinstance(file.iloc[it]['Date'],dt.datetime):
            file.at[it,'Date']=swap_datetime(file.iloc[it]['Date'])
        elif isinstance(file.iloc[it]['Date'],str):
            d=file.iloc[it]['Date']
            if len(d)==8:
                d=d[:6]+"20"+d[6:]
            file.at[it,'Date']=dt.datetime.strptime(d,"%d/%m/%Y")
    if write:
        with pd.ExcelWriter(path+".xlsx") as writer:
            file.to_excel(writer, 'Sheet1', index=None)
            writer.save()
    else:
        return file


# In[10]:


def findall_clubs(path,teams):
    import pandas as pd
    file=pd.read_excel(path+'.xlsx')
    lista_c=[]
    counter=0
    i=0
    done=False
    while i<len(file.index) and not(done):
        if i==teams+50:
            print('Está a ver demasiadas linhas, tem erro')
        if file.iloc[i]['HomeTeam'] in lista_c:
            pass
        else:
            lista_c+=[file.iloc[i]['HomeTeam']]
            counter+=1
        if file.iloc[i]['AwayTeam'] in lista_c:
            pass
        else:
            lista_c+=[file.iloc[i]['AwayTeam']]
            counter+=1
        if counter==teams:
            done=True
        i+=1
    return lista_c 


# In[11]:


def findall_clubs2_new(path,read=True): #menos eficiente, mas não precisa do número das equipas
    import pandas as pd
    #import xlwings
    #xwfile=xw.Book(path+".xlsx") #assim não dá permission error
    #xwfile.close()
    if read:
        file=pd.read_excel(path+'.xlsx')
    else:
        file = path
    lista_c=[]
    for i in range(0,len(file)):
        H=file.iloc[i]['HT']
        A=file.iloc[i]['AT']
        if H not in lista_c:
            lista_c+=[H]
        if A not in lista_c:
            lista_c+=[A]
            
    return lista_c
    
    


# # ALPHA Functions

# In[12]:


def form1(df,clubs,x,diff=True): #usa xG, model 5, Ean/Eadv
    if x!=5:
        print('We gotta redo this fuction maman')
        print('Cause x != 5 :(')
        raise('Ja foste')
    for club in clubs:
        vars()[club]=[[],[],0] # 0 xG // 1 Form per game
    H_form=[]
    A_form=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_form+=[0]
        else:
            H_form+=[
                round((round((vars()[H][1][-5])*0.1,2))+(round((vars()[H][1][-4])*0.15,2))+(round((vars()[H][1][-3])*0.2,2))+
                (round((vars()[H][1][-2])*0.25,2))+(round((vars()[H][1][-1])*0.3,2)),1)
            ]
            
        if vars()[A][-1]<x:
            A_form+=[0]
        else:
            A_form+=[
                round((round((vars()[A][1][-5])*0.1,2))+(round((vars()[A][1][-4])*0.15,2))+(round((vars()[A][1][-3])*0.2,2))+
                      (round((vars()[A][1][-2])*0.25,2))+(round((vars()[A][1][-1])*0.3,2)),1)
            ]
        #  # #  # # # # # # #
        vars()[H][0]+=[df.iloc[i]['HxG']]
        vars()[A][0]+=[df.iloc[i]['AxG']]
        
        if vars()[H][-1]<x:
            vars()[H][1]+=[
                (((sum(vars()[H][0]))/(sum(vars()[A][0])))*(vars()[H][0][-1]))
            ]
        elif vars()[H][-1]>=x:
            vars()[H][1]+=[
                (((sum(vars()[H][0][-x:]))/(sum(vars()[A][0][-x:])))*(vars()[H][0][-1]))
            ]
        else:
            raise('Meh')
            
            
        if vars()[A][-1]<x:
            vars()[A][1]+=[
                (((sum(vars()[A][0]))/(sum(vars()[H][0])))*(vars()[A][0][-1]))
            ]
        elif vars()[A][-1]>=x:
            vars()[A][1]+=[
                (((sum(vars()[A][0][-x:]))/(sum(vars()[H][0][-x:])))*(vars()[A][0][-1]))
            ]
        else:
            raise('Meh2')
        
        
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
            
    form_diff=list(map(lambda x,y:x-y,H_form,A_form))
    if diff:
        output=pd.DataFrame({'Form1_Diff'+str(x):form_diff})
    else:
        output=pd.DataFrame({'Form1_H'+str(x):H_form,
                            'Form1_A'+str(x):A_form,
                            'Form1_Diff'+str(x):form_diff})
    return output
        
        
        


# In[48]:


def form2(df,clubs,x,diff=True): #usa xPTS, model 4 Eadv/Ean
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 xPTS / Form per Game
    H_form2=[]
    A_form2=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        if vars()[H][-1]<x:
            H_form2+=[0]
        else:
            H_form2+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35),1)
            ]
            
        if vars()[A][-1]<x:
            A_form2+=[0]
        else:
            A_form2+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35),1)
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HxPTS']]
        vars()[A][0]+=[df.iloc[i]['AxPTS']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            if sum(vars()[H][0][:-1])==0 and H=='Alaves': #Alaves em 2016 Vs Atleti Mad. teve xPTS=0.0 (e ficou 1-1 xD)
                print('Le Lord Alaves Vs Atleti 2016 (1-1 xD)')
                vars()[H][1]+=[
                    (((sum(vars()[A][0][:-1]))/(0.01))*(vars()[H][0][-1])) 
                ]
            elif sum(vars()[H][0][:-1])==0 and H=='Udinese': #Udinese também tem um jogo com xPTS=0.0 (perdeu 4-0)
                print('Roma Vs Lord Udinese 2017 (4-0)')
                vars()[H][1]+=[
                    (((sum(vars()[A][0][:-1]))/(0.01))*(vars()[H][0][-1])) 
                ]
            else:
                vars()[H][1]+=[
                    (((sum(vars()[A][0][:-1]))/(sum(vars()[H][0][:-1])))*(vars()[H][0][-1])) 
                ]
        else:
            if sum(vars()[H][0][-x:-1])==0:
                print(H,A,'2')
            vars()[H][1]+=[
                (((sum(vars()[A][0][-x:-1]))/(sum(vars()[H][0][-x:-1])))*(vars()[H][0][-1]))
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            if sum(vars()[A][0][:-1])==0:
                print(H,A,'3')
            vars()[A][1]+=[
                (((sum(vars()[H][0][:-1]))/(sum(vars()[A][0][:-1])))*(vars()[A][0][-1]))
            ]
        else: 
            if sum(vars()[A][0][-x:-1])==0:
                print(H,A,'4')
            vars()[A][1]+=[
                (((sum(vars()[H][0][-x:-1]))/(sum(vars()[A][0][-x:-1])))*(vars()[A][0][-1]))
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # form2 diff H-A
    form2_diff=list(map(lambda x,y:x-y,H_form2,A_form2))
    
    if diff:
        output=pd.DataFrame({'Form2_Diff'+str(x):form2_diff})
    else:
        output=pd.DataFrame({'Form2_H'+str(x):H_form2,
                            'Form2_A'+str(x):A_form2,
                            'Form2_Diff'+str(x):form2_diff})
        
    return output


# In[14]:


def form3(df,clubs,x,diff=True): #usa xPTS, model 4, Ean/Eadv
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 xPTS / Form per Game
    H_form2=[]
    A_form2=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_form2+=[0]
        else:
            H_form2+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35),1)
            ]
            
        if vars()[A][-1]<x:
            A_form2+=[0]
        else:
            A_form2+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35),1)
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HxPTS']]
        vars()[A][0]+=[df.iloc[i]['AxPTS']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            if sum(vars()[A][0][:-1]) == 0:
                vars()[H][1]+=[
                    (((sum(vars()[H][0][:-1]))/((df.iloc[i]['AxPTS'])*len(vars()[H][0][:-1])))*(vars()[H][0][-1])) 
                ]
            else:
                vars()[H][1]+=[
                    (((sum(vars()[H][0][:-1]))/(sum(vars()[A][0][:-1])))*(vars()[H][0][-1])) 
                ]
        else:
            if sum(vars()[A][0][-x:-1]) == 0:
                vars()[H][1]+=[
                    (((sum(vars()[H][0][-x:-1]))/((df.iloc[i]['AxPTS'])*x))*(vars()[H][0][-1]))
                ]
            else:
                vars()[H][1]+=[
                    (((sum(vars()[H][0][-x:-1]))/(sum(vars()[A][0][-x:-1])))*(vars()[H][0][-1]))
                ]
                
        #### #  # # #  # # # #  # # #  # # # #  # # #  # # #  # 
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            if sum(vars()[H][0][:-1]) == 0:
                vars()[A][1]+=[
                    (((sum(vars()[A][0][:-1]))/((df.iloc[i]['HxPTS'])*len(vars()[A][0][:-1])))*(vars()[A][0][-1]))
                ]
            else:
                vars()[A][1]+=[
                    (((sum(vars()[A][0][:-1]))/(sum(vars()[H][0][:-1])))*(vars()[A][0][-1]))
                ]
        else: 
            if sum(vars()[H][0][-x:-1]) == 0:
                vars()[A][1]+=[
                    (((sum(vars()[A][0][-x:-1]))/((df.iloc[i]['HxPTS'])*x))*(vars()[A][0][-1]))
                ]
            else:
                vars()[A][1]+=[
                    (((sum(vars()[A][0][-x:-1]))/(sum(vars()[H][0][-x:-1])))*(vars()[A][0][-1]))
                ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # form2 diff H-A
    form2_diff=list(map(lambda x,y:x-y,H_form2,A_form2))
    
    if diff:
        output=pd.DataFrame({'Form3_Diff'+str(x):form2_diff})
    else:
        output=pd.DataFrame({'Form3_H'+str(x):H_form2,
                            'Form3_A'+str(x):A_form2,
                            'Form3_Diff'+str(x):form2_diff})
        
    return output


# In[15]:


def new_form(df,clubs,x,diff=True):
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 xPTS / Form per Game
    H_newform=[]
    A_newform=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_newform+=[0]
        else:
            H_newform+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35),1)
            ]
            
        if vars()[A][-1]<x:
            A_newform+=[0]
        else:
            A_newform+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35),1)
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HxPTS']]
        vars()[A][0]+=[df.iloc[i]['AxPTS']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    newform_diff=list(map(lambda x,y:x-y,H_newform,A_newform))
    
    if diff:
        output=pd.DataFrame({'NewForm_Diff'+str(x):newform_diff})
    else:
        output=pd.DataFrame({'NewForm_H'+str(x):H_newform,
                            'NewForm_A'+str(x):A_newform,
                            'NewForm_Diff'+str(x):newform_diff})
        
    return output


# In[16]:


def ST_form(df,clubs,x,diff=True):
    #usa o método new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 ShotsT / Form per Game
    H_ST=[]
    A_ST=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_ST+=[0]
        else:
            H_ST+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_ST+=[0]
        else:
            A_ST+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HST']]
        vars()[A][0]+=[df.iloc[i]['AST']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    st_form_diff=list(map(lambda x,y:x-y,H_ST,A_ST))
    
    if diff:
        output=pd.DataFrame({'STForm_Diff'+str(x):st_form_diff})
    else:
        output=pd.DataFrame({'STForm_H'+str(x):H_ST,
                            'STForm_A'+str(x):A_ST,
                            'STForm_Diff'+str(x):st_form_diff})
        
    return output


# In[17]:


def CCC_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 CCC / Form per Game
    H_CCC=[]
    A_CCC=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_CCC+=[0]
        else:
            H_CCC+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_CCC+=[0]
        else:
            A_CCC+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HCCC']]
        vars()[A][0]+=[df.iloc[i]['ACCC']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    cccform_diff=list(map(lambda x,y:x-y,H_CCC,A_CCC))
    
    if diff:
        output=pd.DataFrame({'CCCForm_Diff'+str(x):cccform_diff})
    else:
        output=pd.DataFrame({'CCCForm_H'+str(x):H_CCC,
                            'CCCForm_A'+str(x):A_CCC,
                            'CCCForm_Diff'+str(x):cccform_diff})
        
    return output


# In[18]:


def DEEP_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 CCC / Form per Game
    H_DEEP=[]
    A_DEEP=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_DEEP+=[0]
        else:
            H_DEEP+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_DEEP+=[0]
        else:
            A_DEEP+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HDEEP']]
        vars()[A][0]+=[df.iloc[i]['ADEEP']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    deepform_diff=list(map(lambda x,y:x-y,H_DEEP,A_DEEP))
    
    if diff:
        output=pd.DataFrame({'DEEPForm_Diff'+str(x):deepform_diff})
    else:
        output=pd.DataFrame({'DEEPForm_H'+str(x):H_DEEP,
                            'DEEPForm_A'+str(x):A_DEEP,
                            'DEEPForm_Diff'+str(x):deepform_diff})
        
    return output


# In[19]:


def PPDA_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 CCC / Form per Game
    H_PPDA=[]
    A_PPDA=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_PPDA+=[0]
        else:
            H_PPDA+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_PPDA+=[0]
        else:
            A_PPDA+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HPPDA']]
        vars()[A][0]+=[df.iloc[i]['APPDA']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    ppdaform_diff=list(map(lambda x,y:x-y,H_PPDA,A_PPDA))
    
    if diff:
        output=pd.DataFrame({'PPDAForm_Diff'+str(x):ppdaform_diff})
    else:
        output=pd.DataFrame({'PPDAForm_H'+str(x):H_PPDA,
                            'PPDAForm_A'+str(x):A_PPDA,
                            'PPDAForm_Diff'+str(x):ppdaform_diff})
        
    return output


# In[20]:


def Pass_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],0] #0 CCC / Form per Game
    H_Pass=[]
    A_Pass=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_Pass+=[0]
        else:
            H_Pass+=[
                round(((vars()[H][1][-4])*0.15)+((vars()[H][1][-3])*0.2)+
                      ((vars()[H][1][-2])*0.3)+((vars()[H][1][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_Pass+=[0]
        else:
            A_Pass+=[
                round(((vars()[A][1][-4])*0.15)+((vars()[A][1][-3])*0.2)+
                      ((vars()[A][1][-2])*0.3)+((vars()[A][1][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HPass']]
        vars()[A][0]+=[df.iloc[i]['APass']]
        if vars()[H][-1]==0:
            vars()[H][1]+=[0]
        
        elif 0<vars()[H][-1]<x:
            vars()[H][1]+=[
                (sum(vars()[A][0][:-1]))*(vars()[H][0][-1]) 
            ]
        else:
            vars()[H][1]+=[
                (sum(vars()[A][0][-x:-1]))*(vars()[H][0][-1])
            ]
        
        if vars()[A][-1]==0:
            vars()[A][1]+=[0]
        elif 0<vars()[A][-1]<x:
            vars()[A][1]+=[
                (sum(vars()[H][0][:-1]))*(vars()[A][0][-1])
            ]
        else: 
            vars()[A][1]+=[
                (sum(vars()[H][0][-x:-1]))*(vars()[A][0][-1])
            ]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    passform_diff=list(map(lambda x,y:x-y,H_Pass,A_Pass))
    
    if diff:
        output=pd.DataFrame({'PassForm_Diff'+str(x):passform_diff})
    else:
        output=pd.DataFrame({'PassForm_H'+str(x):H_Pass,
                            'PassForm_A'+str(x):A_Pass,
                            'PassForm_Diff'+str(x):passform_diff})
        
    return output


# In[21]:


def unlucky(df,clubs,x,diff=True):
    #if x!=5:
    #    print('Maman, o x tem de ser 5, caso contrario, muda a função')
    #    raise('Meh')
    for club in clubs:
        vars()[club]=[[],0] 
    H_unlucky=[]
    A_unlucky=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        if vars()[H][-1]<x:
            H_unlucky+=[0]
        else:
            H_unlucky+=[
                round(sum(vars()[H][0][-x:]),1)
            ]
            
        if vars()[A][-1]<x:
            A_unlucky+=[0]
        else:
            A_unlucky+=[
                round(sum(vars()[A][0][-x:]),1)
            ]
            
        # # # # # # # #  # # #
        HxPTS=df.iloc[i]['HxPTS']
        AxPTS=df.iloc[i]['AxPTS']
        FTR=df.iloc[i]['FTR']
        if HxPTS<=AxPTS:
            vars()[H][0]+=[0]
            one=AxPTS-HxPTS
            coef=one*(0 if FTR=='A' else 2 if FTR=='D' else 3) #pontos perdidos, neste caso pela AwayTeam
            vars()[A][0]+=[coef]
        else:
            vars()[A][0]+=[0]
            one=HxPTS-AxPTS
            coef=one*(0 if FTR=='H' else 2 if FTR=='D' else 3) #pontos perdidos, neste caso pela HomeTeam
            vars()[H][0]+=[coef]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # relação de diferença H-A
    unlucky_diff = list(map(lambda x,y:x-y,H_unlucky,A_unlucky))
    
    if diff:
        output=pd.DataFrame({'Unlucky_Diff'+str(x):unlucky_diff})
    else:
        output=pd.DataFrame({'Unlucky_H'+str(x):H_unlucky,
                            'Unlucky_A'+str(x):A_unlucky,
                            'Unlucky_Diff'+str(x):unlucky_diff})
        
    return output
            
        


# In[22]:


def lucky(df,clubs,x,diff=True):
    for club in clubs:
        vars()[club]=[[],0] 
    H_lucky=[]
    A_lucky=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_lucky+=[0]
        else:
            H_lucky+=[
                round(sum(vars()[H][0][-x:]),1)
            ]
            
        if vars()[A][-1]<x:
            A_lucky+=[0]
        else:
            A_lucky+=[
                round(sum(vars()[A][0][-x:]),1)
            ]
            
        # #  # # # # # # # # # # # #
        HxPTS=df.iloc[i]['HxPTS']
        AxPTS=df.iloc[i]['AxPTS']
        FTR=df.iloc[i]['FTR']
        Hpts= 0 if FTR=='A' else 1 if FTR=='D' else 3
        Apts= 0 if FTR=='H' else 1 if FTR=='D' else 3
        coefH= Hpts-HxPTS
        coefA= Apts-AxPTS
        #vars()[H][0]+=[coefH if coefH>0 else 0]
        #vars()[A][0]+=[coefA if coefA>0 else 0]
        vars()[H][0]+=[coefH]
        vars()[A][0]+=[coefA]
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    #### lucky diff H-A
    lucky_diff=list(map(lambda x,y:x-y,H_lucky,A_lucky))
    
    if diff:
        output=pd.DataFrame({'Lucky_Diff'+str(x):lucky_diff})
    else:
        output=pd.DataFrame({'Lucky_H'+str(x):H_lucky,
                            'Lucky_A'+str(x):A_lucky,
                            'Lucky_Diff'+str(x):lucky_diff})
        
    return output        


# In[23]:


def shot_quality(df,clubs,x,diff=True):
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 xG// 1 ST // 2 xG/ST
    H_quality=[]
    A_quality=[]
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            H_quality+=[0]
        else:
            H_quality+=[round((sum(vars()[H][0][-x:])/(sum(vars()[H][1][-x:]))),1)]
        if vars()[A][-1]<x:
            A_quality+=[0]
        else:
            A_quality+=[round((sum(vars()[A][0][-x:])/(sum(vars()[A][1][-x:]))),1)]
            
        # # #  # # # # #  # # # #
        
        vars()[H][0]+=[df.iloc[i]['HxG']]
        vars()[H][1]+=[df.iloc[i]['HST']]
        
        
        vars()[A][0]+=[df.iloc[i]['AxG']]
        vars()[A][1]+=[df.iloc[i]['AST']]
        
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    differ=list(map(lambda x,y:x-y,H_quality,A_quality))
    
    if diff:
        output=pd.DataFrame({'SQuality_Diff'+str(x):differ})
    else:
        output=pd.DataFrame({
            'SQuality_H'+str(x):H_quality,'SQuality_A'+str(x):A_quality,'SQuality_Diff'+str(x):differ
        })
        
    return output
        


# In[24]:


def xpoints_made(df,clubs,x,diff=True):
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 total de pts // 1 ppontos casa // 2 pontos fora
    H_xpoints=[[],[]] #0 total de pts // 1 pontos em casa
    A_xpoints=[[],[]]  #0 total de pontos // 1 pontos fora
    xpoints_diff=[[],[]] #0 diff total // 1 diff H-A
    #df=pd.read_excel(file+'.xlsx',0)
    size=len(df.index)
    for i in range(size):
        res=df.iloc[i]['FTR']
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        HW=False
        D=False
        AW=False
        if vars()[H][-1]<x:
            H_xpoints[0]+=[0]
            H_xpoints[1]+=[0]
        else:
            H_xpoints[0]+=[round((sum(vars()[H][0])/len(vars()[H][0])),1)]
            H_xpoints[1]+=[round((sum(vars()[H][1])/len(vars()[H][1])),1)]
        if vars()[A][-1]<x:
            A_xpoints[0]+=[0]
            A_xpoints[1]+=[0]
        else:
            A_xpoints[0]+=[round((sum(vars()[A][0])/len(vars()[A][0])),1)]
            A_xpoints[1]+=[round((sum(vars()[A][2])/len(vars()[A][2])),1)]
            
        # trata da diff    
        #if vars()[H][-1]>=x and vars()[A][-1]>=x:
        #    xpoints_diff[0]+=[(sum(vars()[H][0])/len(vars()[H][0]))-(sum(vars()[A][0])/len(vars()[A][0]))] 
        #    xpoints_diff[1]+=[(sum(vars()[H][1])/len(vars()[H][1]))-(sum(vars()[A][2])/len(vars()[A][2]))]
        #else:
        #    xpoints_diff[0]+=[0]
        #    xpoints_diff[1]+=[0]
            
        # # # # #  # # # # #  # # #
        vars()[H][0]+=[df.iloc[i]['HxPTS']]
        vars()[H][1]+=[df.iloc[i]['HxPTS']]
        vars()[A][0]+=[df.iloc[i]['AxPTS']]
        vars()[A][2]+=[df.iloc[i]['AxPTS']]
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1    
        
    xpoints_diff[0]=list(map(lambda x,y:x-y,H_xpoints[0],A_xpoints[0]))
    xpoints_diff[1]=list(map(lambda x,y:x-y,H_xpoints[1],A_xpoints[1]))
    
    if diff:
        output=pd.DataFrame({'xPoints_Diff_Total':xpoints_diff[0],'xPoints_Diff_H-A':xpoints_diff[1]})
    else:
        output=pd.DataFrame({'H_xPts_Total':H_xpoints[0],'H_xPts_H':H_xpoints[1],
                             'A_xPts_Total':A_xpoints[0],'A_xPts_A':A_xpoints[1],
                             'xPoints_Diff_Total':xpoints_diff[0],'xPoints_Diff_H-A':xpoints_diff[1],
                             })
    return output


# In[25]:


def s_st_g_c(df,clubs,x,diff=True):
    for club in clubs:
        vars()[club]=[[],[],[],[],0]
    L_list=[[],[],[],[]] #0s,1st,2g,3c
    H_list=[[],[],[],[]]
    diff_list=[[],[],[],[]]
    l_rel=[[],[],[],[]] #relação >< que a média Low (1, maior q a media/0, menor/igual à média )
    h_rel=[[],[],[],[]] #relação >< que a média High
    #df=pd.read_excel(file+'.xlsx',0)
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
            
        
        if vars()[H][-1]<x:
            L_list[0]+=[0]
            L_list[1]+=[0]
            L_list[2]+=[0]
            L_list[3]+=[0]
            l_rel[0]+=[0]
            l_rel[1]+=[0]
            l_rel[2]+=[0]
            l_rel[3]+=[0]
        else:
            L_list[0]+=[int(round(sum(vars()[H][0][-x:])/x))]
            if (sum(vars()[H][0][-x:])/x) < vars()[H][0][-1]:
                l_rel[0]+=[1]
            else:
                l_rel[0]+=[0]
                
            L_list[1]+=[int(round(sum(vars()[H][1][-x:])/x))]
            if (sum(vars()[H][1][-x:])/x) < vars()[H][1][-1]:
                l_rel[1]+=[1]
            else:
                l_rel[1]+=[0]
                
            L_list[2]+=[int(round(sum(vars()[H][2][-x:])/x))]
            if (sum(vars()[H][2][-x:])/x) < vars()[H][2][-1]:
                l_rel[2]+=[1]
            else:
                l_rel[2]+=[0]
                
            L_list[3]+=[int(round(sum(vars()[H][3][-x:])/x))]
            if (sum(vars()[H][3][-x:])/x) < vars()[H][3][-1]:
                l_rel[3]+=[1]
            else:
                l_rel[3]+=[0]
            
        if vars()[A][-1]<x:
            H_list[0]+=[0]
            H_list[1]+=[0]
            H_list[2]+=[0]
            H_list[3]+=[0]
            h_rel[0]+=[0]
            h_rel[1]+=[0]
            h_rel[2]+=[0]
            h_rel[3]+=[0]
        else:
            H_list[0]+=[int(round(sum(vars()[A][0][-x:]))/x)]
            if (sum(vars()[A][0][-x:])/x) < vars()[A][0][-1]:
                h_rel[0]+=[1]
            else:
                h_rel[0]+=[0]
                
            H_list[1]+=[int(round(sum(vars()[A][1][-x:]))/x)]
            if (sum(vars()[A][1][-x:])/x) < vars()[A][1][-1]:
                h_rel[1]+=[1]
            else:
                h_rel[1]+=[0]
                
            H_list[2]+=[int(round(sum(vars()[A][2][-x:])/x))]
            if (sum(vars()[A][2][-x:])/x) < vars()[A][2][-1]:
                h_rel[2]+=[1]
            else:
                h_rel[2]+=[0]
                
            H_list[3]+=[int(round(sum(vars()[A][3][-x:])/x))]
            if (sum(vars()[A][3][-x:])/x) < vars()[A][3][-1]:
                h_rel[3]+=[1]
            else:
                h_rel[3]+=[0]
                
        # trata da relação de diferença     #   #   #  #  #   #   #  #   #  #  #   #   
        if vars()[H][-1]>=x and vars()[A][-1]>=x:
            diff_list[0]+=[int(round((sum(vars()[H][0][-x:])/x)-(sum(vars()[A][0][-x:])/x)))]
            diff_list[1]+=[int(round((sum(vars()[H][1][-x:])/x)-(sum(vars()[A][1][-x:])/x)))]
            diff_list[2]+=[int(round((sum(vars()[H][2][-x:])/x)-(sum(vars()[A][2][-x:])/x)))]
            diff_list[3]+=[int(round((sum(vars()[H][3][-x:])/x)-(sum(vars()[A][3][-x:])/x)))]
        else:
            diff_list[0]+=[0]
            diff_list[1]+=[0]
            diff_list[2]+=[0]
            diff_list[3]+=[0]
        # # ###   ##     #     #   #  #  #   #   #  #   #  #   #  #  #  #   #  #  #         
        vars()[H][0]+=[df.iloc[i]['HS']]
        vars()[A][0]+=[df.iloc[i]['AS']]
        vars()[H][1]+=[df.iloc[i]['HST']]
        vars()[A][1]+=[df.iloc[i]['AST']]
        vars()[H][2]+=[df.iloc[i]['FTHG']]
        vars()[A][2]+=[df.iloc[i]['FTAG']]
        vars()[H][3]+=[df.iloc[i]['FTAG']]
        vars()[A][3]+=[df.iloc[i]['FTHG']]
        
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
            
            
    if diff:
        output=pd.DataFrame({'S_Diff_H-A_'+str(x):diff_list[0],'ST_Diff_H-A_'+str(x):diff_list[1],'Scrd_Diff_H-A_'+str(x):diff_list[2],'Concd_Diff_H-A_'+str(x):diff_list[3]})
    else:
        output=pd.DataFrame({'HS_'+str(x):L_list[0],'Last_H_S':l_rel[0],'HST_'+str(x):L_list[1],'Last_H_ST':l_rel[1],
                             'HScrd_'+str(x):L_list[2],'Last_H_Scrd':l_rel[2],'HConcd_'+str(x):L_list[3],'Last_H_Concd':l_rel[3],
                            'AS_'+str(x):H_list[0],'Last_A_S':h_rel[0],'AST_'+str(x):H_list[1],'Last_A_ST':h_rel[1],
                             'AScrd_'+str(x):H_list[2],'Last_A_Scrd':h_rel[2],'AConcd_'+str(x):H_list[3],'Last_A_Concd':h_rel[3],
                            'S_Diff_H-A_'+str(x):diff_list[0],'ST_Diff_H-A_'+str(x):diff_list[1],
                             'Scrd_Diff_H-A_'+str(x):diff_list[2],'Concd_Diff_H-A_'+str(x):diff_list[3]})
            
    return output 


# In[26]:


def non_odd_counter(df,clubs):
    for club in clubs:
        vars()[club]=[0,0,0,0,0,0,0,0,0,0] #-1 counter ||| 0 Win, 1 Scrd, 2 Concd,3/4 WinH/A,5/6 ScrdH/A,7/8ConcdH/A
    L_count=[[],[],[]]
    H_count=[[],[],[]]
    HA_count=[[],[],[],[],[],[]]
    Draw_count=[[],[],[],[]] #AINDA NÃOOOOOOOOOOOOOOOOOOO ADICIONEIIIIIIIIIIIIIIIIIII
    #df=pd.read_excel(file+'.xlsx',0)    
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
               
        L_count[0]+=[vars()[H][0]]
        L_count[1]+=[vars()[H][1]]
        L_count[2]+=[vars()[H][2]]
        
        H_count[0]+=[vars()[A][0]]
        H_count[1]+=[vars()[A][1]]
        H_count[2]+=[vars()[A][2]]
        
        HA_count[0]+=[vars()[H][3]]
        HA_count[1]+=[vars()[A][4]]
        HA_count[2]+=[vars()[H][5]]
        HA_count[3]+=[vars()[A][6]]
        HA_count[4]+=[vars()[H][7]]
        HA_count[5]+=[vars()[A][8]]
        
        
        #if df.iloc[i]['Lowest_Odd']=='H':   #Odd + baixa CASA 
        if df.iloc[i]['FTR']=='H': #se a equipa de casa ganha, como fica o counter
            if vars()[H][0]>0:
                vars()[H][0]+=1 
            else:
                vars()[H][0]=1
            if vars()[A][0]>0:
                vars()[A][0]=-1 
            else:
                vars()[A][0]-=1 
            #H/A-> focando só nas prestações H/A
            if vars()[H][3]>0:
                vars()[H][3]+=1 
            else:
                vars()[H][3]=1
            if vars()[A][4]>0:
                vars()[A][4]=-1 
            else:
                vars()[A][4]-=1
        if df.iloc[i]['FTR']=='A': #se a equipa de fora ganha, como fica o counter
            if vars()[H][0]>0:
                vars()[H][0]=-1 
            else:
                vars()[H][0]-=1
            if vars()[A][0]>0:
                vars()[A][0]+=1 
            else:
                vars()[A][0]=1 
            #H/A-> focando só nas prestações H/A    
            if vars()[H][3]>0:
                vars()[H][3]=-1 
            else:
                vars()[H][3]-=1
            if vars()[A][4]>0:
                vars()[A][4]+=1 
            else:
                vars()[A][4]=1 
        if df.iloc[i]['FTR']=='D': #se há empate, os counter de jogos ganhos vão todos a zero
            if vars()[H][0]>0:
                vars()[H][0]=-1 
            else:
                vars()[H][0]-=1
            if vars()[A][0]>0:
                vars()[A][0]=-1 
            else:
                vars()[A][0]-=1 
            #H/A-> focando só nas prestações H/A       
            if vars()[H][3]>0:
                vars()[H][3]=-1 
            else:
                vars()[H][3]-=1
            if vars()[A][4]>0:
                vars()[A][4]=-1 
            else:
                vars()[A][4]-=1 
        if df.iloc[i]['FTHG']>0 and df.iloc[i]['FTAG']>0: # se ambas marcam
            if vars()[H][1]>0:
                vars()[H][1]+=1 
            else:
                vars()[H][1]=1    
            if vars()[A][1]>0:
                vars()[A][1]+=1    
            else:
                vars()[A][1]=1    
            if vars()[H][2]>0:
                vars()[H][2]=-1
            else:
                vars()[H][2]-=1
            if vars()[A][2]>0:
                vars()[A][2]=-1 
            else:
                vars()[A][2]-=1 
            #H/A-> focando só nas prestações H/A   
            if vars()[H][5]>0:
                vars()[H][5]+=1 
            else:
                vars()[H][5]=1    
            if vars()[A][6]>0:
                vars()[A][6]+=1    
            else:
                vars()[A][6]=1    
            if vars()[H][7]>0:
                vars()[H][7]=-1
            else:
                vars()[H][7]-=1
            if vars()[A][8]>0:
                vars()[A][8]=-1 
            else:
                vars()[A][8]-=1 
        if df.iloc[i]['FTHG']>0 and df.iloc[i]['FTAG']==0: # se só casa marca
            #print('(+,0)')
            if vars()[H][1]>0:
                vars()[H][1]+=1 
            else:
                vars()[H][1]=1    
            if vars()[A][1]>0:
                vars()[A][1]=-1    
            else:
                vars()[A][1]-=1    
            if vars()[H][2]>0:
                vars()[H][2]+=1
            else:
                vars()[H][2]=1
            if vars()[A][2]>0:
                vars()[A][2]=-1 
            else:
                vars()[A][2]-=1 
            #H/A-> focando só nas prestações H/A
            if vars()[H][5]>0:
                vars()[H][5]+=1 
            else:
                vars()[H][5]=1    
            if vars()[A][6]>0:
                vars()[A][6]=-1    
            else:
                vars()[A][6]-=1    
            if vars()[H][7]>0:
                vars()[H][7]+=1
            else:
                vars()[H][7]=1
            if vars()[A][8]>0:
                vars()[A][8]=-1 
            else:
                vars()[A][8]-=1 
        if df.iloc[i]['FTHG']==0 and df.iloc[i]['FTAG']>0: # se só fora marca
            #print('(0,+)')
            if vars()[H][1]>0:
                vars()[H][1]=-1 
            else:
                vars()[H][1]-=1    
            if vars()[A][1]>0:
                vars()[A][1]+=1    
            else:
                vars()[A][1]=1    
            if vars()[H][2]>0:
                vars()[H][2]=-1
            else:
                vars()[H][2]-=1
            if vars()[A][2]>0:
                vars()[A][2]+=1 
            else:
                vars()[A][2]=1 
            #H/A-> focando só nas prestações H/A
            if vars()[H][5]>0:
                vars()[H][5]=-1 
            else:
                vars()[H][5]-=1    
            if vars()[A][6]>0:
                vars()[A][6]+=1    
            else:
                vars()[A][6]=1    
            if vars()[H][7]>0:
                vars()[H][7]=-1
            else:
                vars()[H][7]-=1
            if vars()[A][8]>0:
                vars()[A][8]+=1 
            else:
                vars()[A][8]=1
        if df.iloc[i]['FTHG']==0 and df.iloc[i]['FTAG']==0: # se nenhuma marca
            #print('(0,0)')
            if vars()[H][1]>0:
                vars()[H][1]=-1 
            else:
                vars()[H][1]-=1    
            if vars()[A][1]>0:
                vars()[A][1]=-1    
            else:
                vars()[A][1]-=1    
            if vars()[H][2]>0:
                vars()[H][2]+=1
            else:
                vars()[H][2]=1
            if vars()[A][2]>0:
                vars()[A][2]+=1 
            else:
                vars()[A][2]=1 
            #H/A-> focando só nas prestações H/A
            if vars()[H][5]>0:
                vars()[H][5]=-1 
            else:
                vars()[H][5]-=1    
            if vars()[A][6]>0:
                vars()[A][6]=-1    
            else:
                vars()[A][6]-=1    
            if vars()[H][7]>0:
                vars()[H][7]+=1
            else:
                vars()[H][7]=1
            if vars()[A][8]>0:
                vars()[A][8]+=1 
            else:
                vars()[A][8]=1
        
        
    #Total, regista todos os jogos
    #_H/A regista o registo em casa de H e fora de A
    output=pd.DataFrame({'WinCounterTotal_H':L_count[0],'WinCounterTotal_A':H_count[0],
                         'WinCounter_H':HA_count[0],'WinCounter_A':HA_count[1],
                         'ScrdCounterTotal_H':L_count[1],'ScrdCounterTotal_A':H_count[1],
                         'ScrdCounter_H':HA_count[2],'ScrdCounter_A':HA_count[3],
                         'ConcdCounterTotal_H':L_count[2],'ConcdCounterTotal_A':H_count[2],
                         'ConcdCounter_H':HA_count[4],'ConcdCounter_A':HA_count[5]
                        })
    return output


# In[27]:


def lowest_lost(df,clubs):
    for club in clubs:
        vars()[club]=1000
    llost=[]
    size=len(df.index)
    for i in range(size):
        H=False
        A=False
        if df.iloc[i]['Lowest_Odd']=='H':
            L=df.iloc[i]['HomeTeam']
            Hi=df.iloc[i]['AwayTeam'] #high odd
            H=True
        else:
            L=df.iloc[i]['AwayTeam']
            Hi=df.iloc[i]['HomeTeam'] #high odd
            A=True
            
        llost+=[round_down(vars()[L],1)] #uso o round_down(,1)
        
        if H and (df.iloc[i]['FTR']!='H'):
            if df.iloc[i]['ODDH_Aver.']<vars()[L]:
                vars()[L]=df.iloc[i]['ODDH_Aver.']
        elif A and (df.iloc[i]['FTR']!='A'):
            if df.iloc[i]['ODDA_Aver.']<vars()[L]:
                vars()[L]=df.iloc[i]['ODDA_Aver.']
                
        if H and (df.iloc[i]['FTR']!='A'):
            if df.iloc[i]['ODDA_Aver.']<vars()[Hi]:
                vars()[Hi]=df.iloc[i]['ODDA_Aver.']
        elif A and (df.iloc[i]['FTR']!='H'):
            if df.iloc[i]['ODDH_Aver.']<vars()[Hi]:
                vars()[Hi]=df.iloc[i]['ODDH_Aver.']
                
    output=pd.DataFrame({'L_LowestLost':llost})
    return output


# In[72]:


def won_notwon(df):
    size=len(df.index)
    wnw=[]
    for i in range(size):
        if (df.iloc[i]['FTHG']>df.iloc[i]['FTAG']):
            wnw+=[1]
        else:
            wnw+=[0]
                
    output=pd.DataFrame({'Won/NotWon':wnw})
    return output


# In[29]:


def x_pass(df,clubs,x,diff=True):
    #média dos últimos x jogos de:
    #xG, xPTS, Pass%, PPDA, DEEP, CCC, xGConcd
    for club in clubs:
        vars()[club]=[[],[],[],[],[],[],[],0]
    L_list=[[],[],[],[],[],[],[]] #0xG,1xPTS,2Pass%,3PPDA,4DEEP,5CCC
    H_list=[[],[],[],[],[],[],[]]
    diff_list=[[],[],[],[],[],[],[]]
    l_rel=[[],[],[],[],[],[],[]] #relação >< que a média Low (1, maior q a media/0, menor/igual à média )
    h_rel=[[],[],[],[],[],[],[]] #relação >< que a média High
    #df=pd.read_excel(file+'.xlsx',0)
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
            
        
        if vars()[H][-1]<x:
            L_list[0]+=[0]
            L_list[1]+=[0]
            L_list[2]+=[0]
            L_list[3]+=[0]
            L_list[4]+=[0]
            L_list[5]+=[0]
            L_list[6]+=[0]
            l_rel[0]+=[0]
            l_rel[1]+=[0]
            l_rel[2]+=[0]
            l_rel[3]+=[0]
            l_rel[4]+=[0]
            l_rel[5]+=[0]
            l_rel[6]+=[0]
        else:
            L_list[0]+=[int(round(sum(vars()[H][0][-x:])/x))]
            if (sum(vars()[H][0][-x:])/x) < vars()[H][0][-1]:
                l_rel[0]+=[1]
            else:
                l_rel[0]+=[0]
                
            L_list[1]+=[round(sum(vars()[H][1][-x:])/x,1)]
            if (sum(vars()[H][1][-x:])/x) < vars()[H][1][-1]:
                l_rel[1]+=[1]
            else:
                l_rel[1]+=[0]
                
            L_list[2]+=[int(round(sum(vars()[H][2][-x:])/x))]
            if (sum(vars()[H][2][-x:])/x) < vars()[H][2][-1]:
                l_rel[2]+=[1]
            else:
                l_rel[2]+=[0]
                
            L_list[3]+=[int(round(sum(vars()[H][3][-x:])/x))]
            if (sum(vars()[H][3][-x:])/x) < vars()[H][3][-1]:
                l_rel[3]+=[1]
            else:
                l_rel[3]+=[0]
            
            L_list[4]+=[int(round(sum(vars()[H][4][-x:])/x))]
            if (sum(vars()[H][4][-x:])/x) < vars()[H][4][-1]:
                l_rel[4]+=[1]
            else:
                l_rel[4]+=[0]
            
            L_list[5]+=[int(round(sum(vars()[H][5][-x:])/x))]
            if (sum(vars()[H][5][-x:])/x) < vars()[H][5][-1]:
                l_rel[5]+=[1]
            else:
                l_rel[5]+=[0]
                
            L_list[6]+=[int(round(sum(vars()[H][6][-x:])/x))]
            if (sum(vars()[H][6][-x:])/x) < vars()[H][6][-1]:
                l_rel[6]+=[1]
            else:
                l_rel[6]+=[0]
            
        if vars()[A][-1]<x:
            H_list[0]+=[0]
            H_list[1]+=[0]
            H_list[2]+=[0]
            H_list[3]+=[0]
            H_list[4]+=[0]
            H_list[5]+=[0]
            H_list[6]+=[0]
            h_rel[0]+=[0]
            h_rel[1]+=[0]
            h_rel[2]+=[0]
            h_rel[3]+=[0]
            h_rel[4]+=[0]
            h_rel[5]+=[0]
            h_rel[6]+=[0]
        else:
            H_list[0]+=[int(round(sum(vars()[A][0][-x:])/x))]
            if (sum(vars()[A][0][-x:])/x) < vars()[A][0][-1]:
                h_rel[0]+=[1]
            else:
                h_rel[0]+=[0]
                
            H_list[1]+=[round(sum(vars()[A][1][-x:])/x,1)]
            if (sum(vars()[A][1][-x:])/x) < vars()[A][1][-1]:
                h_rel[1]+=[1]
            else:
                h_rel[1]+=[0]
            H_list[2]+=[int(round(sum(vars()[A][2][-x:])/x))]
            if (sum(vars()[A][2][-x:])/x) < vars()[A][2][-1]:
                h_rel[2]+=[1]
            else:
                h_rel[2]+=[0]
                
            H_list[3]+=[int(round(sum(vars()[A][3][-x:])/x))]
            if (sum(vars()[A][3][-x:])/x) < vars()[A][3][-1]:
                h_rel[3]+=[1]
            else:
                h_rel[3]+=[0]
                
            H_list[4]+=[int(round(sum(vars()[A][4][-x:])/x))]
            if (sum(vars()[A][4][-x:])/x) < vars()[A][4][-1]:
                h_rel[4]+=[1]
            else:
                h_rel[4]+=[0]
                
            H_list[5]+=[int(round(sum(vars()[A][5][-x:])/x))]
            if (sum(vars()[A][5][-x:])/x) < vars()[A][5][-1]:
                h_rel[5]+=[1]
            else:
                h_rel[5]+=[0]
                
            H_list[6]+=[int(round(sum(vars()[A][6][-x:])/x))]
            if (sum(vars()[A][6][-x:])/x) < vars()[A][6][-1]:
                h_rel[6]+=[1]
            else:
                h_rel[6]+=[0]    
        # trata da relação de diferença     #   #   #  #  #   #   #  #   #  #  #   #   
        if vars()[H][-1]>=x and vars()[A][-1]>=x:
            diff_list[0]+=[int(round((sum(vars()[H][0][-x:])/x)-(sum(vars()[A][0][-x:])/x)))]
            diff_list[1]+=[round((sum(vars()[H][1][-x:])/x)-(sum(vars()[A][1][-x:])/x),1)]
            diff_list[2]+=[int(round((sum(vars()[H][2][-x:])/x)-(sum(vars()[A][2][-x:])/x)))]
            diff_list[3]+=[int(round((sum(vars()[H][3][-x:])/x)-(sum(vars()[A][3][-x:])/x)))]
            diff_list[4]+=[int(round((sum(vars()[H][4][-x:])/x)-(sum(vars()[A][4][-x:])/x)))]
            diff_list[5]+=[int(round((sum(vars()[H][5][-x:])/x)-(sum(vars()[A][5][-x:])/x)))]
            diff_list[6]+=[int(round((sum(vars()[H][6][-x:])/x)-(sum(vars()[A][6][-x:])/x)))]
        else:
            diff_list[0]+=[0]
            diff_list[1]+=[0]
            diff_list[2]+=[0]
            diff_list[3]+=[0]
            diff_list[4]+=[0]
            diff_list[5]+=[0]
            diff_list[6]+=[0]
        # # ###   ##     #     #   #  #  #   #   #  #   #  #   #  #  #  #   #  #  #     
            
        
        vars()[H][0]+=[df.iloc[i]['HxG']]
        vars()[A][0]+=[df.iloc[i]['AxG']]
        vars()[H][1]+=[df.iloc[i]['HxPTS']]
        vars()[A][1]+=[df.iloc[i]['AxPTS']]
        vars()[H][2]+=[df.iloc[i]['HPass']]
        vars()[A][2]+=[df.iloc[i]['APass']]
        vars()[H][3]+=[df.iloc[i]['HPPDA']]
        vars()[A][3]+=[df.iloc[i]['APPDA']]
        vars()[H][4]+=[df.iloc[i]['HDEEP']]
        vars()[A][4]+=[df.iloc[i]['ADEEP']]
        vars()[H][5]+=[df.iloc[i]['HCCC']]
        vars()[A][5]+=[df.iloc[i]['ACCC']]
        vars()[H][6]+=[df.iloc[i]['AxG']]
        vars()[A][6]+=[df.iloc[i]['HxG']]
            
               
        vars()[H][-1]+=1
        vars()[A][-1]+=1
            
    
    if diff:
        output=pd.DataFrame({'xG_Diff_'+str(x):diff_list[0],'xPTS_Diff_'+str(x):diff_list[1],
                             'Pass%_Diff_'+str(x):diff_list[2],'PPDA_Diff_'+str(x):diff_list[3],
                             'DEEP_Diff_'+str(x):diff_list[4],'CCC_Diff_'+str(x):diff_list[5],
                             'xConcd_Diff_'+str(x):diff_list[6]
                            })
    else:
        output=pd.DataFrame({'HxG_'+str(x):L_list[0],'Last_HxG':l_rel[0],'HxPTS_'+str(x):L_list[1],'Last_HxPTS':l_rel[1],
                            'HPass%_'+str(x):L_list[2],'Last_HPass%':l_rel[2],'HPPDA_'+str(x):L_list[3],'Last_HPPDA':l_rel[3],
                            'HDEEP_'+str(x):L_list[4],'Last_HDEEP':l_rel[4],
                            'HCCC_'+str(x):L_list[5],'Last_HCCC':l_rel[5],
                            'HxConcd_'+str(x):L_list[6],'Last_HxConcd':l_rel[6],
                            'AxG_'+str(x):H_list[0],'Last_AxG':h_rel[0],'AxPTS_'+str(x):H_list[1],'Last_AxPTS':h_rel[1],
                            'APass%_'+str(x):H_list[2],'Last_APass%':h_rel[2],'APPDA_'+str(x):H_list[3],'Last_APPDA':h_rel[3],
                            'ADEEP_'+str(x):H_list[4],'Last_ADEEP':h_rel[4],
                            'ACCC_'+str(x):H_list[5],'Last_ACCC':h_rel[5],
                            'AxConcd_'+str(x):H_list[6],'Last_AxConcd':h_rel[6],
                             ####
                            'xG_Diff_'+str(x):diff_list[0],'xPTS_Diff_'+str(x):diff_list[1],
                            'Pass%_Diff_'+str(x):diff_list[2],'PPDA_Diff_'+str(x):diff_list[3],
                            'DEEP_Diff_'+str(x):diff_list[4],'CCC_Diff_'+str(x):diff_list[5],
                            'xConcd_Diff_'+str(x):diff_list[6]
                            })
            
    return output 


# In[30]:


def HA_points(df,clubs,x,diff=True):
    #média de pontos feitos em casa e fora
    #faz se a média de todos os jogos até x,
    #dps de x, faz-se a média dos últimos x jogos
    for club in clubs:
        vars()[club]=[[],[],0,0] #2Hcounter, 3Acounter
    HA_list=[[],[]] #0H,1A
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
            
        if vars()[H][2]==0:
            HA_list[0]+=[0]
        elif vars()[H][2]<x:
            HA_list[0]+=[round((sum(vars()[H][0])/len(vars()[H][0])),1)]
        elif vars()[H][2]>=x:
            HA_list[0]+=[round((sum(vars()[H][0][(-x):])/x),1)]
        else:
            print('Erro')
            raise('HA_points')
            
        if vars()[A][3]==0:
            HA_list[1]+=[0]
        elif vars()[A][3]<x:
            HA_list[1]+=[round((sum(vars()[A][1])/len(vars()[A][1])),1)]
        elif vars()[A][3]>=x:
            HA_list[1]+=[round((sum(vars()[A][1][(-x):])/x),1)]
        else:
            print('Erro')
            raise('HA_points')
            
            
        #trata de acrescentar à lista
        if df.iloc[i]['FTR']=='H':
            vars()[H][0]+=[3]
            vars()[A][1]+=[0]
        elif df.iloc[i]['FTR']=='D':
            vars()[H][0]+=[1]
            vars()[A][1]+=[1]
        else:
            vars()[H][0]+=[0]
            vars()[A][1]+=[3]
            
        
        vars()[H][2]+=1
        vars()[A][3]+=1
        
    
    HAAH=list(map(lambda x,y:x-y,HA_list[0],HA_list[1]))
    output=pd.DataFrame({'HT_HPoints_'+str(x):HA_list[0],'AT_APoints_'+str(x):HA_list[1],'HA_PointsDiff':HAAH})
                
    return output       
    


# In[49]:


def join_husky(df,clubs,x,diff=True,read=False):
    
    if read:
        df=pd.read_excel(df+'.xlsx',0)
        
    league=df['League']
    ht=df['HT']
    at=df['AT']
    date=df['Date']
    time=df['Time']
    try:
        oddh=df['ODDH_Aver.']
        oddd=df['ODDD_Aver.']
        odda=df['ODDA_Aver.']
    except:
        print('Não usou as Odds')
        pass
    print('done extra')
    a=xpoints_made(df,clubs,x,diff=diff)
    print('done a')
    b=HA_points(df,clubs,x,diff=diff)
    print('done b')
    c=x_pass(df,clubs,x,diff=diff)
    print('done c')
    d=shot_quality(df,clubs,x,diff=diff)
    print('done d')
    e=s_st_g_c(df,clubs,x,diff=diff)
    print('done e')
    f=non_odd_counter(df,clubs)
    print('done f')
    g=lucky(df,clubs,x,diff=diff)
    print('done g')
    h=unlucky(df,clubs,x,diff=diff)
    print('done h')
    i=ST_form(df,clubs,x,diff=diff)
    print('done i')
    j=CCC_form(df,clubs,x,diff=diff)
    print('done j')
    k=DEEP_form(df,clubs,x,diff=diff)
    print('done k')
    l=PPDA_form(df,clubs,x,diff=diff)
    print('done l')
    m=Pass_form(df,clubs,x,diff=diff)
    print('done m')
    n=form1(df,clubs,x,diff=diff)
    print('done n')
    o=form2(df,clubs,x,diff=diff)
    print('done o')
    p=form3(df,clubs,x,diff=diff)
    print('done p')
    q=new_form(df,clubs,x,diff=diff)
    print('done q')
    r=won_notwon(df)
    print('done r')
    try:
        df1=pd.concat([league,date,time,ht,at,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,oddh,oddd,odda],sort=False,axis=1)
    except:
        df1=pd.concat([league,date,time,ht,at,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r],sort=False,axis=1)
    df1=df1.sort_values(['Date','Time'],ascending=[True,True])
    return df1


# In[32]:


#clubs=findall_clubs2_new('NewPL14_15')


# In[33]:


#dfPL=pd.read_excel('NewPL14_15.xlsx')


# In[34]:


#test1=join_husky(dfPL,clubs,5,diff=False)


# In[35]:


#test1.to_excel('HuskyTestPL14_15.xlsx',index=False)


# In[36]:


def alpha_concat(files): #faz concat da lista de files e ordena-os já por date e time
    df1=pd.concat(files,sort=False)
    df=df1.sort_values(['Date'], ascending=True)
    return df


# Este `new_cut_zeros` só serve para criar os ficheiros que juntam épocas de várias ligas  

# In[37]:


def new_cut_zeros(file,x): #retira os dados com counters/médias/pontos a zero
    #precisamos de indicar o x dos jogos para a média
    size=len(file.index) #vamos só usar uma coluna, cuidado com erros
    i=0
    done=False
    conter=0
    ind=[]
    while i<size and not(done):
        if not((file.iloc[i]['Pass%_Diff_'+str(x)]==0) and (file.iloc[i]['S_Diff'+str(x)]==0) and (file.iloc[i]['ST_Diff'+str(x)]==0)):
            ind+=[i]
            counter+=1
        else:
            counter=0
        i+=1
        if counter==100: #se encontrarmos 100 jogos seguidos sem zeros, acaba o cicl0
            done=True
    conc=[]
    for n in ind:
        conc+=[pd.DataFrame(file.iloc[n,:]).T]
    conc+=[file[i:]]
    df=pd.concat(conc,sort=False)
    return df


# `new_cut_zeros2` é para só para ser usado numa época de uma só liga

# In[38]:


def new_cut_zeros2(file,x):
    #precisamos de indicar o x dos jogos para a média
    size=len(file.index) #vamos só usar uma coluna, cuidado com erros
    i=0
    done=False
    conter=0
    ind=[]
    while i<size and not(done):
        if not((file.iloc[i]['Pass%_Diff_'+str(x)]==0) and (file.iloc[i]['S_Diff_H-A_'+str(x)]==0) and (file.iloc[i]['ST_Diff_H-A_'+str(x)]==0)):
            ind+=[i]
            counter+=1
        else:
            counter=0
        i+=1
        if counter==25: #se encontrarmos 100 jogos seguidos sem zeros, acaba o cicl0
            done=True
    conc=[]
    for n in ind:
        conc+=[pd.DataFrame(file.iloc[n,:]).T]
    conc+=[file[i:]]
    df=pd.concat(conc,sort=False)
    return df


# In[39]:


def husky_pos(df,clubs,x,diff=True,read=True):
    df=join_husky(df,clubs,x,diff=diff,read=read)
    df=new_cut_zeros2(df,x)
    return df


# `year_husky` junta num só ficheiro tds as ligas de uma época. 

# In[40]:


def year_husky(os_path,x,season,diff=True,read=True): 
    #junta num só ficheiro tds as ligas de uma época
    import os
    ind=new_find_data(os_path)
    rep=[] #repositorio para fazer concat
    for data_file in ind:
        try:
            season_list=os.listdir(os_path+data_file+'\\')
            i=season_index(os_path+data_file+'\\',season)
            #print(os_path+data_file+'\\'+season_list[i][:-5])
            clubs=findall_clubs2_new(os_path+data_file+'\\'+season_list[i][:-5])
            print(os_path+data_file+'\\'+season_list[i][:-5])
            file=husky_pos(os_path+data_file+'\\'+season_list[i][:-5],clubs,x,diff=diff,read=read)
            rep+=[file]
        except:
            print('except')
            print(data_file,'season:',season)
        #    pass
    print(len(rep))
    df=pd.concat(rep,sort=False)
    df=df.sort_values(['Date','Time'],ascending=[True,True])
    df=df.reset_index(drop=True)
    return df


# `league_husky` junta num só ficheiro as épocas que queremos de uma liga

# In[41]:


def league_husky(path,f_season,l_season,x,diff=True,read=True):
    os_path='C:\\Users\\joaom\\Documents\\Projetos\\PYTHON\\Apostas\\'+path+'___\\'
    i1=season_index(os_path,f_season)
    i2=season_index(os_path,l_season)
    seasons=os.listdir(os_path)
    rep=[]
    for i in range(i1,i2+1):
        clubs=findall_clubs2_new(os_path+seasons[i][:-5])
        file=husky_pos(os_path+seasons[i][:-5],clubs,x,diff=diff,read=read)
        rep+=[file]
    df=pd.concat(rep,sort=False)
    df=df.sort_values(['Date','Time'],ascending=[True,True])
    df=df.reset_index(drop=True)
    return df
    


# `year_complete` junta o AllOddCounter, e faz o cut_zeros (e também põe o Won/NotWon na última coluna).
# 
# Recebe o file de `year_alpha` 
# 
# Como não temos Time, os jogos não estão bem por ordem (entre ligas), por iss, nesses casos não vamos usar all_odd_counter

# In[42]:


def year_complete(file,x,odd_allcounter=False):
    if odd_allcounter:
        file=odd_allcounter_alpha(file)
        colunas=list(file.columns.values)
        file=file[colunas[:-2]+[colunas[-1]]+[colunas[-2]]]
        file=cut_zeros(file,x)
        file=file.reset_index(drop=True)
    else:
        file=cut_zeros(file,x)
        file=file.reset_index(drop=True)
    return file


# `all_alpha` prepara o ficheiro para passar para as pastas do PC e faz o `year_alpha` para os anos que queremos

# In[43]:


def all_husky(os_path,x,f_season,l_season,diff=True,read=True):
    rep=[]
    for i in range(f_season,l_season+1):
        df=year_husky(os_path,x,i,diff=diff,read=read)
        rep+=[df]
        print('---'+str(i)+'----')
    bigfile=pd.concat(rep,sort=False)
    bigfile=bigfile.sort_values(['Date','Time'],ascending=[True,True])
    bigfile=bigfile.reset_index(drop=True)
    return bigfile


# ____________________

# ### Let the tests begin

# In[41]:







