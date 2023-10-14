


import pandas as pd
#import xlwings as xw
import openpyxl as op
import numpy as np
import datetime as dt
import numpy as np
import os
import math

print('Neste modelos vamos fazer uma experiência e não usar Odds')
print('Em vex disso, usamos os xPTS para calcular o "power" de uma equipa')


# In[2]:


np.seterr(all='raise')


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


def points_aux(h_p,a_p,ha):
    if ha=='H':
        return 3 if h_p>a_p else 1 if h_p==a_p else 0
    elif ha=='A':
        return 3 if h_p<a_p else 1 if h_p==a_p else 0
    else:
        raise Exception('Not valid argument')


# In[6]:


def new_find_data(os_path):
    lista=os.listdir(os_path)
    data_newfiles=[]
    for i in lista:
        if (i[-3:]=='___') and (i[:3].lower()=='new'):
            data_newfiles+=[i]
    print(data_newfiles)
    return data_newfiles


# In[7]:


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

# In[8]:


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


# In[9]:




# In[10]:


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


# In[11]:


def findall_clubs2_new(path,read=True): #menos eficiente, mas não precisa do número das equipas
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


def ST_form(df,clubs,x,diff=True):
    #usa o método new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 ShotsT / 1 ST reverse / Form per Game
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
                round(((vars()[H][2][-4])*0.15)+((vars()[H][2][-3])*0.2)+
                      ((vars()[H][2][-2])*0.3)+((vars()[H][2][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_ST+=[0]
        else:
            A_ST+=[
                round(((vars()[A][2][-4])*0.15)+((vars()[A][2][-3])*0.2)+
                      ((vars()[A][2][-2])*0.3)+((vars()[A][2][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HST']]
        vars()[A][0]+=[df.iloc[i]['AST']]
        vars()[H][1]+=[df.iloc[i]['AST']]
        vars()[A][1]+=[df.iloc[i]['HST']]
        if vars()[H][-1]==0:
            vars()[H][2]+=[0]
        
        elif 0<vars()[H][-1]<x:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][:-1])))+(vars()[H][0][-1]) 
                ]
            except:
                vars()[H][2]+=[0]
        else:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][-x:-1])))+(vars()[H][0][-1])
                ]
            except:
                vars()[H][2]+=[0]
        
        if vars()[A][-1]==0:
            vars()[A][2]+=[0]
        elif 0<vars()[A][-1]<x:
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
        else: 
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][-x:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
            
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


# In[13]:


def Goal_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 CCC / 1 xPTS / Form per Game
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
                round(((vars()[H][2][-4])*0.15)+((vars()[H][2][-3])*0.2)+
                      ((vars()[H][2][-2])*0.3)+((vars()[H][2][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_CCC+=[0]
        else:
            A_CCC+=[
                round(((vars()[A][2][-4])*0.15)+((vars()[A][2][-3])*0.2)+
                      ((vars()[A][2][-2])*0.3)+((vars()[A][2][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['FTHG']]
        vars()[A][0]+=[df.iloc[i]['FTAG']]
        vars()[H][1]+=[df.iloc[i]['FTAG']]
        vars()[A][1]+=[df.iloc[i]['FTHG']]
        if vars()[H][-1]==0:
            vars()[H][2]+=[0]
        
        elif 0<vars()[H][-1]<x:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][:-1])))+(vars()[H][0][-1]) 
                ]
            except:
                vars()[H][2]+=[0]
        else:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][-x:-1])))+(vars()[H][0][-1])
                ]
            except:
                vars()[H][2]+=[0]
        
        if vars()[A][-1]==0:
            vars()[A][2]+=[0]
        elif 0<vars()[A][-1]<x:
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
        else: 
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][-x:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    cccform_diff=list(map(lambda x,y:x-y,H_CCC,A_CCC))
    
    if diff:
        output=pd.DataFrame({'GoalForm_Diff'+str(x):cccform_diff})
    else:
        output=pd.DataFrame({'GoalForm_H'+str(x):H_CCC,
                            'GoalForm_A'+str(x):A_CCC,
                            'GoalForm_Diff'+str(x):cccform_diff})
        
    return output


# In[14]:


def CCC_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 CCC / 1 xPTS / Form per Game
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
                round(((vars()[H][2][-4])*0.15)+((vars()[H][2][-3])*0.2)+
                      ((vars()[H][2][-2])*0.3)+((vars()[H][2][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_CCC+=[0]
        else:
            A_CCC+=[
                round(((vars()[A][2][-4])*0.15)+((vars()[A][2][-3])*0.2)+
                      ((vars()[A][2][-2])*0.3)+((vars()[A][2][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HCCC']]
        vars()[A][0]+=[df.iloc[i]['ACCC']]
        vars()[H][1]+=[df.iloc[i]['ACCC']]
        vars()[A][1]+=[df.iloc[i]['HCCC']]
        if vars()[H][-1]==0:
            vars()[H][2]+=[0]
        
        elif 0<vars()[H][-1]<x:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][:-1])))+(vars()[H][0][-1]) 
                ]
            except:
                vars()[H][2]+=[0]
        else:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][-x:-1])))+(vars()[H][0][-1])
                ]
            except:
                vars()[H][2]+=[0]
        
        if vars()[A][-1]==0:
            vars()[A][2]+=[0]
        elif 0<vars()[A][-1]<x:
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
        else: 
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][-x:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
            
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


# In[15]:


def Points_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 CCC / 1 xPTS / Form per Game
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
                round(((vars()[H][2][-4])*0.15)+((vars()[H][2][-3])*0.2)+
                      ((vars()[H][2][-2])*0.3)+((vars()[H][2][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_CCC+=[0]
        else:
            A_CCC+=[
                round(((vars()[A][2][-4])*0.15)+((vars()[A][2][-3])*0.2)+
                      ((vars()[A][2][-2])*0.3)+((vars()[A][2][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[points_aux(df.iloc[i]['FTHG'],df.iloc[i]['FTAG'],'H')]
        vars()[A][0]+=[points_aux(df.iloc[i]['FTHG'],df.iloc[i]['FTAG'],'A')]
        vars()[H][1]+=[points_aux(df.iloc[i]['FTHG'],df.iloc[i]['FTAG'],'A')]
        vars()[A][1]+=[points_aux(df.iloc[i]['FTHG'],df.iloc[i]['FTAG'],'H')]
        if vars()[H][-1]==0:
            vars()[H][2]+=[0]
        
        elif 0<vars()[H][-1]<x:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][:-1])))+(vars()[H][0][-1]) 
                ]
            except:
                vars()[H][2]+=[0]
        else:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][-x:-1])))+(vars()[H][0][-1])
                ]
            except:
                vars()[H][2]+=[0]
        
        if vars()[A][-1]==0:
            vars()[A][2]+=[0]
        elif 0<vars()[A][-1]<x:
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
        else: 
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][-x:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
            
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    # # newform diff H-A
    cccform_diff=list(map(lambda x,y:x-y,H_CCC,A_CCC))
    
    if diff:
        output=pd.DataFrame({'PointsForm_Diff'+str(x):cccform_diff})
    else:
        output=pd.DataFrame({'PointsForm_H'+str(x):H_CCC,
                            'PointsForm_A'+str(x):A_CCC,
                            'PointsForm_Diff'+str(x):cccform_diff})
        
    return output


# In[16]:


def Pass_form(df,clubs,x,diff=True):
    #usa o método do new_form
    if x!=5:
        print('Maman, o x tem de ser 5, caso contrario, muda a função')
        raise('Meh')
    for club in clubs:
        vars()[club]=[[],[],[],0] #0 Pass / 1 Pass reverse / Form per Game
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
                round(((vars()[H][2][-4])*0.15)+((vars()[H][2][-3])*0.2)+
                      ((vars()[H][2][-2])*0.3)+((vars()[H][2][-1])*0.35))
            ]
            
        if vars()[A][-1]<x:
            A_Pass+=[0]
        else:
            A_Pass+=[
                round(((vars()[A][2][-4])*0.15)+((vars()[A][2][-3])*0.2)+
                      ((vars()[A][2][-2])*0.3)+((vars()[A][2][-1])*0.35))
            ]
            
        # # # # # # #  # # # #
        vars()[H][0]+=[df.iloc[i]['HPass']]
        vars()[A][0]+=[df.iloc[i]['APass']]
        vars()[H][1]+=[df.iloc[i]['APass']]
        vars()[A][1]+=[df.iloc[i]['HPass']]
        if vars()[H][-1]==0:
            vars()[H][2]+=[0]
        
        elif 0<vars()[H][-1]<x:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][:-1])))+(vars()[H][0][-1]) 
                ]
            except:
                vars()[H][2]+=[0]
        else:
            try:
                vars()[H][2]+=[
                    (-(np.mean(vars()[A][1][-x:-1])))+(vars()[H][0][-1])
                ]
            except:
                vars()[H][2]+=[0]
        
        if vars()[A][-1]==0:
            vars()[A][2]+=[0]
        elif 0<vars()[A][-1]<x:
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
        else: 
            try:
                vars()[A][2]+=[
                    (-(np.mean(vars()[H][1][-x:-1])))+(vars()[A][0][-1])
                ]
            except:
                vars()[A][2]+=[0]
                
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


# In[17]:


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
                round(5*((0.3*(vars()[H][0][-1]))+(0.25*(vars()[H][0][-2]))+
                        (0.2*(vars()[H][0][-3]))+(0.15*(vars()[H][0][-4]))+(0.1*(vars()[H][0][-5]))),1)
            ]
            
        if vars()[A][-1]<x:
            A_lucky+=[0]
        else:
            A_lucky+=[
                round(5*((0.3*(vars()[A][0][-1]))+(0.25*(vars()[A][0][-2]))+
                        (0.2*(vars()[A][0][-3]))+(0.15*(vars()[A][0][-4]))+(0.1*(vars()[A][0][-5]))),1)
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


# In[18]:


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
            H_quality+=[ #10x só pq sim (tenho medo dos valores serem pequenos)
                round(10*((0.3*(vars()[H][2][-1]))+(0.25*(vars()[H][2][-2]))+
                         (0.2*(vars()[H][2][-3]))+(0.15*(vars()[H][2][-4]))+(0.1*(vars()[H][2][-5]))),1)
            ]
            
        if vars()[A][-1]<x:
            A_quality+=[0]
        else:
            A_quality+=[
                round(10*((0.3*(vars()[A][2][-1]))+(0.25*(vars()[A][2][-2]))+
                         (0.2*(vars()[A][2][-3]))+(0.15*(vars()[A][2][-4]))+(0.1*(vars()[A][2][-5]))),1)
            ]
            
        # # #  # # # # #  # # # #
        
        vars()[H][0]+=[df.iloc[i]['FTHG']]
        vars()[H][1]+=[df.iloc[i]['HST']]
        
        
        vars()[A][0]+=[df.iloc[i]['FTAG']]
        vars()[A][1]+=[df.iloc[i]['AST']]
        
        try:
            vars()[H][2]+=[(vars()[H][0][-1])/(vars()[H][1][-1])]
        except:
            vars()[H][2]+=[0] #qnd não há ST dizemos que é 0
            
        try:
            vars()[A][2]+=[(vars()[A][0][-1])/(vars()[A][1][-1])]
        except:
            vars()[A][2]+=[0] #qnd não há ST dizemos que é 0
        
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
        


# In[19]:


def Tackles(df,clubs,x,diff=True):
    #media dos tackles () uma espécie de Def Form
    for club in clubs:
        vars()[club]=[[],0]
    T = [[],[]]
    for i in range(len(df)):
        H = df.iloc[i]['HT']
        A = df.iloc[i]['AT']
        
        if vars()[H][-1]<x:
            T[0]+=[0]
        else: 
            T[0]+=[round(sum(vars()[A][0][-x:])/x)]
        if vars()[A][-1]<x:
            T[1]+=[0]
        else: 
            T[1]+=[round(sum(vars()[A][0][-x:])/x)] 
            
        vars()[H][0]+=[df.iloc[i]['HTack']]
        vars()[A][0]+=[df.iloc[i]['ATack']]
        vars()[H][-1]+=1
        vars()[A][-1]+=1
    Diff = list(map(lambda x,y:x-y,T[0],T[1]))
    
    output = pd.DataFrame({'TacklesH':T[0],'TacklesA':T[1],'Tackles_Diff':Diff})
    return output
            
        
            


# In[20]:


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
            L_list[0]+=[int(round((0.3*(vars()[H][0][-1]))+(0.25*(vars()[H][0][-2]))+
                                 (0.2*(vars()[H][0][-3]))+(0.15*(vars()[H][0][-4]))+(0.1*(vars()[H][0][-5]))))]
            if L_list[0][-1] < vars()[H][0][-1]:
                l_rel[0]+=[1]
            else:
                l_rel[0]+=[0]
                
            L_list[1]+=[int(round((0.3*(vars()[H][1][-1]))+(0.25*(vars()[H][1][-2]))+
                                 (0.2*(vars()[H][1][-3]))+(0.15*(vars()[H][1][-4]))+(0.1*(vars()[H][1][-5]))))]
            if L_list[1][-1] < vars()[H][1][-1]:
                l_rel[1]+=[1]
            else:
                l_rel[1]+=[0]
                
            L_list[2]+=[int(round((0.3*(vars()[H][2][-1]))+(0.25*(vars()[H][2][-2]))+
                                 (0.2*(vars()[H][2][-3]))+(0.15*(vars()[H][2][-4]))+(0.1*(vars()[H][2][-5]))))]
            if L_list[2][-1] < vars()[H][2][-1]:
                l_rel[2]+=[1]
            else:
                l_rel[2]+=[0]
                
            L_list[3]+=[int(round((0.3*(vars()[H][3][-1]))+(0.25*(vars()[H][3][-2]))+
                                 (0.2*(vars()[H][3][-3]))+(0.15*(vars()[H][3][-4]))+(0.1*(vars()[H][3][-5]))))]
            if L_list[3][-1] < vars()[H][3][-1]:
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
            H_list[0]+=[int(round((0.3*(vars()[A][0][-1]))+(0.25*(vars()[A][0][-2]))+
                                 (0.2*(vars()[A][0][-3]))+(0.15*(vars()[A][0][-4]))+(0.1*(vars()[A][0][-5]))))]
            if H_list[0][-1] < vars()[A][0][-1]:
                h_rel[0]+=[1]
            else:
                h_rel[0]+=[0]
                
            H_list[1]+=[int(round((0.3*(vars()[A][1][-1]))+(0.25*(vars()[A][1][-2]))+
                                 (0.2*(vars()[A][1][-3]))+(0.15*(vars()[A][1][-4]))+(0.1*(vars()[A][1][-5]))))]
            if H_list[1][-1] < vars()[A][1][-1]:
                h_rel[1]+=[1]
            else:
                h_rel[1]+=[0]
                
            H_list[2]+=[int(round((0.3*(vars()[A][2][-1]))+(0.25*(vars()[A][2][-2]))+
                                 (0.2*(vars()[A][2][-3]))+(0.15*(vars()[A][2][-4]))+(0.1*(vars()[A][2][-5]))))]
            if H_list[2][-1] < vars()[A][2][-1]:
                h_rel[2]+=[1]
            else:
                h_rel[2]+=[0]
                
            H_list[3]+=[int(round((0.3*(vars()[A][3][-1]))+(0.25*(vars()[A][3][-2]))+
                                 (0.2*(vars()[A][3][-3]))+(0.15*(vars()[A][3][-4]))+(0.1*(vars()[A][3][-5]))))]
            if H_list[3][-1] < vars()[A][3][-1]:
                h_rel[3]+=[1]
            else:
                h_rel[3]+=[0]
                
        # trata da relação de diferença     #   #   #  #  #   #   #  #   #  #  #   #   
        if vars()[H][-1]>=x and vars()[A][-1]>=x:
            diff_list[0]+=[int(round(L_list[0][-1]-H_list[0][-1]))]
            diff_list[1]+=[int(round(L_list[1][-1]-H_list[1][-1]))]
            diff_list[2]+=[int(round(L_list[2][-1]-H_list[2][-1]))]
            diff_list[3]+=[int(round(L_list[3][-1]-H_list[3][-1]))]
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


# In[21]:


def WSC_auxlimit(l,val): # para os counter terem limites
    if val>l:
        return l
    elif (-l)>val:
        return -l
    else:
        return val


# In[22]:


def WSC(df,clubs):
    #nova função para o Win,Scrd,Concd
    for club in clubs:
        vars()[club]=[0,0,0,0,0,0,0,0,0,0] #-1 counter,-2 counterH, -3 counterA ||| 0 Win, 1 Scrd, 2 Concd,3/4 WinH/A,5/6 ScrdH/A,7/8ConcdH/A
    Hone = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter)
    Aone = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter)
    Htwo = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter) (Percentagens)
    Atwo = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter) (Percentagens)
    HA = [[],[],[],[],[],[]] #0/1 WinH/A,2/3 ScrdH/A,4/5ConcdH/A
    HAP = [[],[],[],[],[],[]] #0/1 WinH/A,2/3 ScrdH/A,4/5ConcdH/A  (Percentagens)
    size = len(df)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        
        Hone[0]+=[WSC_auxlimit(5,vars()[H][0])]
        Hone[1]+=[WSC_auxlimit(5,vars()[H][1])]
        Hone[2]+=[WSC_auxlimit(5,vars()[H][2])]
        Aone[0]+=[WSC_auxlimit(5,vars()[A][0])]
        Aone[1]+=[WSC_auxlimit(5,vars()[A][1])]
        Aone[2]+=[WSC_auxlimit(5,vars()[A][2])]
        HA[0]+=[WSC_auxlimit(2,vars()[H][3])]
        HA[2]+=[WSC_auxlimit(2,vars()[H][5])]
        HA[4]+=[WSC_auxlimit(2,vars()[H][7])]
        HA[1]+=[WSC_auxlimit(2,vars()[H][4])]
        HA[3]+=[WSC_auxlimit(2,vars()[H][6])]
        HA[5]+=[WSC_auxlimit(2,vars()[H][8])]
        
        if vars()[H][-1]>0:
            Htwo[0]+=[round(100*(vars()[H][0]/(vars()[H][-1])))]
            Htwo[1]+=[round(100*(vars()[H][1]/(vars()[H][-1])))]
            Htwo[2]+=[round(100*(vars()[H][2]/(vars()[H][-1])))]
        else:
            Htwo[0]+=[0]
            Htwo[1]+=[0]
            Htwo[2]+=[0]
        if vars()[H][-2]>0:
            HAP[0]+=[round(100*(vars()[H][3]/(vars()[H][-2])))]
            HAP[2]+=[round(100*(vars()[H][5]/(vars()[H][-2])))]
            HAP[4]+=[round(100*(vars()[H][7]/(vars()[H][-2])))]
        else:
            HAP[0]+=[0]
            HAP[2]+=[0]
            HAP[4]+=[0]
                
        if vars()[A][-1]>0:
            Atwo[0]+=[round(100*(vars()[A][0]/(vars()[A][-1])))]
            Atwo[1]+=[round(100*(vars()[A][1]/(vars()[A][-1])))]
            Atwo[2]+=[round(100*(vars()[A][2]/(vars()[A][-1])))]
        else:
            Atwo[0]+=[0]
            Atwo[1]+=[0]
            Atwo[2]+=[0]
        if vars()[A][-3]>0:
            HAP[1]+=[round(100*(vars()[A][4]/(vars()[A][-3])))]
            HAP[3]+=[round(100*(vars()[A][6]/(vars()[A][-3])))]
            HAP[5]+=[round(100*(vars()[A][8]/(vars()[A][-3])))]
        else:
            HAP[1]+=[0]
            HAP[3]+=[0]
            HAP[5]+=[0]
            
            
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
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        vars()[H][-2]+=1
        vars()[A][-3]+=1
        
    output = pd.DataFrame({'WinCounterTotal_H':Hone[0],'WinCounterTotal_A':Aone[0],'ScrdCounterTotal_H':Hone[1],
                           'ScrdCounterTotal_A':Aone[1],'ConcdCounterTotal_H':Hone[2],'ConcdCounterTotal_A':Aone[2],
                           'WinPercTotal_H':Htwo[0],'WinPercTotal_A':Atwo[0],'ScrdPercTotal_H':Htwo[1],
                           'ScrdPercTotal_A':Atwo[1],'ConcdPercTotal_H':Htwo[2],'ConcdPercTotal_A':Atwo[2],
                           'WinCounterH_H':HA[0],'WinCounterA_A':HA[1],'ScrdCounterH_H':HA[2],
                           'ScrdCounterTotalA_A':HA[3],'ConcdCounterH_H':HA[4],'ConcdCounterA_A':HA[5],
                           'WinPercH_H':HAP[0],'WinPercA_A':HAP[1],'ScrdPercH_H':HAP[2],
                           'ScrdPercTotalA_A':HAP[3],'ConcdPercH_H':HAP[4],'ConcdPercA_A':HAP[5]
        
    })
    Hone = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter)
    Aone = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter)
    Htwo = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter) (Percentagens)
    Atwo = [[],[],[]] #indices iguais ao vars()[club] (mas sem counter) (Percentagens)
    HA = [[],[],[],[],[],[]] #0/1 WinH/A,2/3 ScrdH/A,4/5ConcdH/A
    HAP = [[],[],[],[],[],[]] #0/1 WinH/A,2/3 ScrdH/A,4/5ConcdH/A  (Percentagens)  
    return output
            
        


# In[23]:


def non_odd_counter(df,clubs):
    for club in clubs:
        vars()[club]=[0,0,0,0,0,0,0,0,0,0] #-1 counter ||| 0 Win, 1 Scrd, 2 Concd,3/4 WinH/A,5/6 ScrdH/A,7/8ConcdH/A
        vars()[club+'_2']=[[],[],[],[],[],[],[],[],[]] #guarda os counter e dps fazemos max e min
    L_count=[[],[],[]]
    H_count=[[],[],[]]
    HA_count=[[],[],[],[],[],[]]
    Maxi=[[],[],[],[],[],[],[],[],[],[],[],[]]
    Mini=[[],[],[],[],[],[],[],[],[],[],[],[]]
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
        
        
        if vars()[H][-1]<5:
            Maxi[0]+=[-10] #o valor dos Mini nunca vai ser positivo
            Mini[0]+=[10] #por isso quando ainda não temos dados suficientes
            Maxi[2]+=[-10] #podemos usar um número positivo para ser diferente
            Mini[2]+=[10]
            Maxi[4]+=[-10]
            Mini[4]+=[10] #o valor dos Mini nunca vai ser negativo
            Maxi[6]+=[-10] #por isso quando ainda não temos dados suficientes
            Mini[6]+=[10] #podemos usar um número negativo para ser diferente
            Maxi[8]+=[-10]
            Mini[8]+=[10]
            Maxi[10]+=[-10]
            Mini[10]+=[10]
            
        else:
            Maxi[0]+=[max(vars()[H+'_2'][0])-vars()[H][0]]
            Mini[0]+=[min(vars()[H+'_2'][0])-vars()[H][0]]
            Maxi[2]+=[max(vars()[H+'_2'][1])-vars()[H][1]]
            Mini[2]+=[min(vars()[H+'_2'][1])-vars()[H][1]]
            Maxi[4]+=[max(vars()[H+'_2'][2])-vars()[H][2]]
            Mini[4]+=[min(vars()[H+'_2'][2])-vars()[H][2]]
            Maxi[6]+=[max(vars()[H+'_2'][3])-vars()[H][3]]
            Mini[6]+=[min(vars()[H+'_2'][3])-vars()[H][3]]
            Maxi[8]+=[max(vars()[H+'_2'][5])-vars()[H][5]]
            Mini[8]+=[min(vars()[H+'_2'][5])-vars()[H][5]]
            Maxi[10]+=[max(vars()[H+'_2'][7])-vars()[H][7]]
            Mini[10]+=[min(vars()[H+'_2'][7])-vars()[H][7]]
            
        if vars()[A][-1]<5:
            Maxi[1]+=[-10]
            Mini[1]+=[10]
            Maxi[3]+=[-10]
            Mini[3]+=[10]
            Maxi[5]+=[-10]
            Mini[5]+=[10]
            Maxi[7]+=[-10]
            Mini[7]+=[10]
            Maxi[9]+=[-10]
            Mini[9]+=[10]
            Maxi[11]+=[-10]
            Mini[11]+=[10]
        else:
            Maxi[1]+=[max(vars()[A+'_2'][0])-vars()[A][0]]
            Mini[1]+=[min(vars()[A+'_2'][0])-vars()[A][0]]
            Maxi[3]+=[max(vars()[A+'_2'][1])-vars()[A][1]]
            Mini[3]+=[min(vars()[A+'_2'][1])-vars()[A][1]]
            Maxi[5]+=[max(vars()[A+'_2'][2])-vars()[A][2]]
            Mini[5]+=[min(vars()[A+'_2'][2])-vars()[A][2]]
            Maxi[7]+=[max(vars()[A+'_2'][4])-vars()[A][4]]
            Mini[7]+=[min(vars()[A+'_2'][4])-vars()[A][4]]
            Maxi[9]+=[max(vars()[A+'_2'][6])-vars()[A][6]]
            Mini[9]+=[min(vars()[A+'_2'][6])-vars()[A][6]]
            Maxi[11]+=[max(vars()[A+'_2'][8])-vars()[A][8]]
            Mini[11]+=[min(vars()[A+'_2'][8])-vars()[A][8]]
            
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
                
        for i in range(len(vars()[H+'_2'])):
            vars()[H+'_2'][i]+=[vars()[H][i]]
            vars()[A+'_2'][i]+=[vars()[A][i]]
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    #Total, regista todos os jogos
    #_H/A regista o registo em casa de H e fora de A
    output=pd.DataFrame({'WinCounterTotal_H':L_count[0],'WinCounterTotal_A':H_count[0],
                         'WinCounter_H':HA_count[0],'WinCounter_A':HA_count[1],
                         'ScrdCounterTotal_H':L_count[1],'ScrdCounterTotal_A':H_count[1],
                         'ScrdCounter_H':HA_count[2],'ScrdCounter_A':HA_count[3],
                         'ConcdCounterTotal_H':L_count[2],'ConcdCounterTotal_A':H_count[2],
                         'ConcdCounter_H':HA_count[4],'ConcdCounter_A':HA_count[5],
                         
                         'Max_WinCounterTotal_H':Maxi[0],'Max_WinCounterTotal_A':Maxi[1],
                         'Max_WinCounter_H':Maxi[6],'Max_WinCounter_A':Maxi[6],
                         'Max_ScrdCounterTotal_H':Maxi[2],'Max_ScrdCounterTotal_A':Maxi[3],
                         'Max_ScrdCounter_H':Maxi[8],'Max_ScrdCounter_A':Maxi[9],
                         'Max_ConcdCounterTotal_H':Maxi[4],'Max_ConcdCounterTotal_A':Maxi[5],
                         'Max_ConcdCounter_H':Maxi[10],'Max_ConcdCounter_A':Maxi[11],
                         
                         'Min_WinCounterTotal_H':Mini[0],'Min_WinCounterTotal_A':Mini[1],
                         'Min_WinCounter_H':Mini[6],'Min_WinCounter_A':Mini[7],
                         'Min_ScrdCounterTotal_H':Mini[2],'Min_ScrdCounterTotal_A':Mini[3],
                         'Min_ScrdCounter_H':Mini[8],'Min_ScrdCounter_A':Mini[9],
                         'Min_ConcdCounterTotal_H':Mini[4],'Min_ConcdCounterTotal_A':Mini[5],
                         'Min_ConcdCounter_H':Mini[10],'Min_ConcdCounter_A':Mini[11]
                        })
    return output


# In[24]:


def won_notwon(df):
    size=len(df.index)
    wnw=[]
    for i in range(size):
        if df.iloc[i]['FTR']=='H':
            wnw+=[1]
        else:
            wnw+=[0]
                
    output=pd.DataFrame({'Won/NotWon':wnw})
    return output


# In[25]:


def HA_points(df,clubs,x,diff=True):
    #média de pontos feitos em casa e fora
    #faz se a média de todos os jogos até x,
    #dps de x, faz-se a média dos últimos x jogos
    for club in clubs:
        vars()[club]=[[],[],[],[],0] #0 pts em Casa, 1 pts Fora, 2Pts TotalH, 3Pts TotalA 
    HA_list=[[],[],[],[]] #0H,1A,2TotalH, 3 TotalA
    size=len(df.index)
    for i in range(size):
        H=df.iloc[i]['HT']
        A=df.iloc[i]['AT']
        if len(vars()[H][0])==0:
            HA_list[0]+=[0]
        else:
            if len(vars()[H][0])<x:
                HA_list[0]+=[round(np.mean(vars()[H][0]),1)]
            else:
                HA_list[0]+=[round((0.3*(vars()[H][0][-1]))+(0.25*(vars()[H][0][-2]))+
                               (0.2*(vars()[H][0][-3]))+(0.15*(vars()[H][0][-4]))+(0.1*(vars()[H][0][-5])),1)]
                
        if len(vars()[H][2])==0:
            HA_list[2]+=[0]
        else:
            if len(vars()[H][2])<x:
                HA_list[2]+=[round(np.mean(vars()[H][2]),1)] #pode dar jeito para aquelas equipas sem alguns jogos
            else:
                HA_list[2]+=[round((0.3*(vars()[H][2][-1]))+(0.25*(vars()[H][2][-2]))+
                               (0.2*(vars()[H][2][-3]))+(0.15*(vars()[H][2][-4]))+(0.1*(vars()[H][2][-5])),1)]
            

        
        if len(vars()[A][1])==0:
            HA_list[1]+=[0]
        else:
            if len(vars()[A][1])<x:
                HA_list[1]+=[round(np.mean(vars()[A][1]),1)]
            else:
                HA_list[1]+=[round((0.3*(vars()[A][1][-1]))+(0.25*(vars()[A][1][-2]))+
                               (0.2*(vars()[A][1][-3]))+(0.15*(vars()[A][1][-4]))+(0.1*(vars()[A][1][-5])),1)]
        
        if len(vars()[A][3])==0:
            HA_list[3]+=[0]
        else:
            if len(vars()[A][3])<x:
                HA_list[3]+=[round(np.mean(vars()[A][3]),1)]
            else:
                HA_list[3]+=[round((0.3*(vars()[A][3][-1]))+(0.25*(vars()[A][3][-2]))+
                               (0.2*(vars()[A][3][-3]))+(0.15*(vars()[A][3][-4]))+(0.1*(vars()[A][3][-5])),1)]
            
            
            
        #trata de acrescentar à lista
        if df.iloc[i]['FTR']=='H':
            vars()[H][0]+=[3] #pontos em casa (0)
            vars()[A][1]+=[0] #pontos fora  (1)
            vars()[H][2]+=[3] #pontos totais (2)
            vars()[A][3]+=[0] #pontos totais (3)
        elif df.iloc[i]['FTR']=='D':
            vars()[H][0]+=[1]
            vars()[A][1]+=[1]
            vars()[H][2]+=[1]
            vars()[A][3]+=[1]
        else:
            vars()[H][0]+=[0]
            vars()[A][1]+=[3]
            vars()[H][2]+=[0]
            vars()[A][3]+=[3]
            
        
        vars()[H][-1]+=1
        vars()[A][-1]+=1
        
    
    HAAH=list(map(lambda x,y:x-y,HA_list[0],HA_list[1]))
    HATot=list(map(lambda x,y:x-y,HA_list[2],HA_list[3]))
    output=pd.DataFrame({'HT_HPoints_'+str(x):HA_list[0],'AT_APoints_'+str(x):HA_list[1],'HA_HAPointsDiff':HAAH,
                        'HT_TotalPoints_5':HA_list[2],'AT_TotalPoints_5':HA_list[3],'HA_TotalPointsDiff':HATot})
                
    return output       
    


# In[26]:


def Cut_Zeros(df,clubs,x):
#este novo cut zeros acrescenta uma coluna com 0/1
#em que 0->não serve, 1->serve
#assim é muito mais fácil
    Colx=[]
    C_list = ['HPass','APass','HS','AS','HST','AST','HCCC','ACCC','FTHG','FTAG']
    for club in clubs:
        vars()[club]=[0] #número de jogos
    for i in range(len(df)):
        HT = df.iloc[i]['HT']
        AT = df.iloc[i]['AT']
        if (vars()[HT][0]<5) or (vars()[AT][0]<5):
            Colx+=[0]
        else:
            Colx+=[1]
            
        if any(pd.isnull(df.iloc[i][C_list])):
            vars()[HT]=[0]
            vars()[AT]=[0]
        else:
            vars()[HT][0]+=1
            vars()[AT][0]+=1
    print(len(Colx),len(df))
    return pd.DataFrame({'Colx':Colx})
        
        
            


# In[27]:




# In[28]:


def join_husky(df,clubs,x,diff=True,read=False):
    if 'FTR' not in df.columns:
        ftr=[]
        for i in range(len(df)):
            if df.iloc[i]['FTHG']>df.iloc[i]['FTAG']:
                ftr+=['H']
            elif df.iloc[i]['FTHG']<df.iloc[i]['FTAG']:
                ftr+=['A']
            else:
                ftr+=['D']
        df['FTR']=ftr
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
    a=Cut_Zeros(df,clubs,x)
    print('done a')
    df = Remove_NaN(df)
    b=HA_points(df,clubs,x,diff=diff)
    print('done b')
    c=shot_quality(df,clubs,x,diff=diff)
    print('done c')
    d=s_st_g_c(df,clubs,x,diff=diff)
    print('done d')
    e=Tackles(df,clubs,x,diff=diff)
    print('done e')
    f=WSC(df,clubs)
    print('done f')
    g=ST_form(df,clubs,x,diff=diff)
    print('done g')
    h=CCC_form(df,clubs,x,diff=diff)
    print('done h')
    i=Pass_form(df,clubs,x,diff=diff)
    print('done i')
    j=Goal_form(df,clubs,x,diff=diff)
    print('done j')
    k=Points_form(df,clubs,x,diff=diff)
    print('done k')
    l=won_notwon(df)
    print('done l')
    try:
        df1=pd.concat([league,date,time,ht,at,a,b,c,d,e,f,g,h,i,j,k,l,oddh,oddd,odda],sort=False,axis=1)
    except:
        df1=pd.concat([league,date,time,ht,at,a,b,c,d,e,f,g,h,i,j,k,l],sort=False,axis=1)
    df1=df1.sort_values(['Date','Time'],ascending=[True,True])
    return df1


# In[29]:


def alpha_concat(files): #faz concat da lista de files e ordena-os já por date e time
    df1=pd.concat(files,sort=False)
    df=df1.sort_values(['Date'], ascending=True)
    return df


# In[30]:


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


# In[31]:


def husky_pos(df,clubs,x,diff=True,read=True):
    df=join_husky(df,clubs,x,diff=diff,read=read)
    df=df.loc[df['Colx']>0]
    return df


# `year_husky` junta num só ficheiro tds as ligas de uma época. 

# In[32]:


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

# In[33]:


def Remove_NaN(df):
    C_list = ['HPass','APass','HS','AS','HST','AST','HCCC','ACCC','FTHG','FTAG']
    for i in range(len(df)):
        if any(pd.isnull(df.iloc[i][C_list])):
            for n in C_list:
                df.at[i,n]=0
    return df
            


# In[34]:


def league_husky(path,f_season,l_season,x,diff=True,read=True):
    os_path='C:\\Users\\joaom\\Documents\\Projetos\\PYTHON\\Apostas\\'+path+'___\\'
    i1=season_index(os_path,f_season)
    i2=season_index(os_path,l_season)
    seasons=os.listdir(os_path)
    rep=[]
    for i in range(i1,i2+1):
        clubs=findall_clubs2_new(os_path+seasons[i][:-5])
        #file = Remove_NaN(pd.read_excel(os_path+seasons[i][:-5]+'.xlsx'))
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

# In[35]:


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

# In[36]:


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

