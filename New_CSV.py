# -*- coding: utf-8 -*-
"""
Created on Fri May 29 19:14:27 2020

@author: joaom
"""
print('No final da época 19/20, como houve exceções temos de criar funções '
      'excecionais para obter os jogos de cada ano')

import datetime as dt
import pandas as pd
import numpy as np
import random
import os
import openpyxl

pd.set_option('display.max_rows',750)
pd.set_option('display.max_columns',1000)


#dada uma string s, clear_ apaga dos os espaços ao lado
#Ex: ' Premier League' --> 'Premier League'
def clear_(s):
    done=False
    i=0
    while i<len(s) and not(done):
        if s[i]!=' ':
            done=True
        else:
#           k=i
            i+=1
        
    done=False
    n=-1
    while n>=(-len(s)) and not(done):
        if s[n]!=' ':
            done=True
        else:
            #k=-n
            n-=1
    if n==-1:
        return s[i:]
    else:
        return s[i:(n+1)]
    
    
def indx(lista,v):
    i=0
    found=False
    while i<len(lista) and not(found):
        if v==lista[i]:
            found=True
        else:
            i+=1
    return i

def split(stri):
    stri=stri.split(' ')
    new=[]
    for i in stri:
        if '-' in i:
            i=i.split('-')
            for n in i:
                new+=[n]
        else:
            new+=[i]
    new2=[]
    for nn in new:
        if "'" in nn:
            nn=nn.split("'")
            for n2 in nn:
                new2+=[n2]
        else:
            new2+=[nn]
    new3=[]
    for m in new2:
        if '.' in m:
            m=m.split('.')
            for n3 in m:
                new3+=[n3]
        else:
            new3+=[m]
    return new3



def helper(t1,t2):
    t1=t1.replace('FC','')
    t2=t2.replace('FC','')
    t1=t1.lower()
    t2=t2.lower()
    t1=split(t1)
    t2=split(t2)
    found=0 #conta qnts nome têm em comum as duas equipas
    for i in range(len(t1)):
        n=0
        while n<len(t2):
            if t1[i]==t2[n]:
                found+=1
            n+=1
    return found

def helper2(t1,t2):
    #vê quantas letras as duas equipas têm em comum
    # caso o helper não consiga identificar nenhuma equipa igual com o seu método
    #Há casos (por exemplo na Bundesliga) em que o nome das equipas está diferente 
    #neste, não precisamos de fazer split
    t1=t1.replace('FC','')
    t2=t2.replace('FC','') 
    t1=t1.lower()
    t2=t2.lower()
    t1=t1.replace(' ','')
    t2=t2.replace(' ','') #como vamos ver as letras, não precisamos dos espaços
    #que contam para o tamanho da palavra
    t1_dix={}
    t2_dix={}
    for n in t1:
        if n not in t1_dix:
            t1_dix[n]=0
        t1_dix[n]+=1
    for m in t2:
        if m not in t2_dix:
            t2_dix[m]=0
        t2_dix[m]+=1
    counter=0
    for nn in t1_dix:
        if nn in t2_dix:
            #devolve o mínimo (uma pode ter 2 n's e outra apenas 1, e nesse caso só um n é correspondido)
            counter+=min([t1_dix[nn],t2_dix[nn]])
    t1L=len(t1)
    t2L=len(t2)
    #devolve a percentagem de letras correspondentes da palavra maior
    #podemos ter os nomes 'abc', 'abce' e , 'obwartuc'
    #a última tem todas as letras da 1a, mas a 2a é mais parecida com a 1a
    #pq a sua percentagem de letras correspondentes é maior
    return round(100*(counter/max(t1L,t2L)),2)
        
            
def file_teams(file1,file2):
    teams1=[]
    i=0
    while i<len(file1):
        team=file1.iloc[i]['HT']
        if team not in teams1:
            teams1+=[team]
        i+=1
    teams2=[]
    n=0
    while n<len(file2):
        try:
            team=file2.iloc[n]['HT']
        except:   
            team=file2.iloc[n]['HomeTeam'] #file2 diz respeito aos dados antigos em que usava 'HomeTeam' em vez de 'HT'
        if team not in teams2:
            teams2+=[team]
        n+=1
    print(teams1)
    print('--------')
    print(teams2)
    mix=[]
    restos=[]
    for ii in range(len(teams1)):
        nn=0
        found=False
        while nn<len(teams2) and not(found):
            if teams1[ii]==teams2[nn]:
                mix+=[[teams1[ii],teams2[nn]]]
                del teams2[nn]
                found=True
            nn+=1
        
        if not found:
            restos+=[teams1[ii]]
            
    if restos==[]:
        return mix
    else:
        restos_copy=restos.copy()
        teams2_copy=teams2.copy()
        mix_copy=mix.copy()
        t=0
        while teams2!=[]:
            print('------')
            print(restos)
            ok=input(str(teams2[t])+'? (write "passa" if not sure Or "reset" to restart) ')
            if ok!='passa' and (ok not in restos) and (ok!='reset'):
                print('Erro na palavra')
                continue
            if ok=='passa':
                t+=1
                continue
            if ok=='reset':
                t=0
                teams2=teams2_copy.copy()
                restos=restos_copy.copy()
                mix=mix_copy.copy()
                continue
            else:
                mix+=[[ok,teams2[t]],[teams2[t],ok]]
                del teams2[t]
                del restos[np.where(np.array(restos)==ok)[0][0]]
            if t==len(teams2):
                t=0
        return mix


def file_teams_old(file1,file2):
    #extra=False #necessário no caso de "tratamento especial"
    teams1=[]
    i=0
    while i<len(file1):
        team=file1.iloc[i]['HT']
        if team not in teams1:
            teams1+=[team]
        i+=1
    
    teams2=[]
    n=0
    while n<len(file2): 
        try:
            team=file2.iloc[n]['HT']
        except:   
            team=file2.iloc[n]['HomeTeam'] #file2 diz respeito aos dados antigos em que usava 'HomeTeam' em vez de 'HT'
        if team not in teams2:
            teams2+=[team]
        n+=1
    print(teams1)
    print('----------')
    print(teams2)
    mix=[]
    restos=[]
    for ii in range(len(teams1)):
        nn=0
        found=False
        while nn<len(teams2) and not(found):
            if teams1[ii]==teams2[nn]:
                mix+=[[teams1[ii],teams2[nn]]]
                del teams2[nn]
                found=True
            nn+=1
        
        if not found:
            restos+=[teams1[ii]]
            
    if restos==[]:
        return mix
    else:
        if len(restos)==1:
            mix+=[[restos[0],teams2[0]],[teams2[0],restos[0]]]
            return mix
        else:
            #inic=len(restos) #vai dar jeito
            add=[]
            for m in range(len(restos)):
                count=[]
                mm=0
                helper_count=1
                while mm<len(teams2):
                    #print(restos[m],'|',teams2[mm])
                    
                    #print(helper_count)
                    if restos[m]=='Terek Grozny':
                        count=[[restos[m],'FK Akhmat'],['FK Akhmat',restos[m]]]
                    else:
                        if helper(restos[m],teams2[mm])>=helper_count:
                            count+=[[restos[m],teams2[mm]],[teams2[mm],restos[m]]]
                            helper_count=helper(restos[m],teams2[mm])
                    mm+=1
                #print(count)
                if len(count)==2:
                    add+=count
                    #del restos[indx(restos,count[0][0])] #como o restos não está em while, podemos 
                    #chegar a out of index
                    del teams2[indx(teams2,count[0][1])] 
                    #if len(add)==(2*(inic-1)):
                    #    mix+=add
                    #    mix+=[[restos[0],teams2[0]],[teams2[0],restos[0]]]
                    #    return mix
                #elif count==[]:
                else:
                    #extra=True
                    print(restos[m])
                    print('--Precisou de tratamento especial--')
                    mm=0
                    helper_count=1
                    while mm<len(teams2):
                        print(restos[m],'|',teams2[mm])
                        print(helper2(restos[m],teams2[mm]))
                        if helper2(restos[m],teams2[mm])>=helper_count:
                            count=[[restos[m],teams2[mm]],[teams2[mm],restos[m]]]
                            helper_count=helper2(restos[m],teams2[mm])
                        mm+=1
                    if len(count)==2:
                        add+=count
                    else:
                        print(count)
                        print('restos',restos,
                            'teams2',teams2)
                        raise('Fdeu')
                #else:
                #    print(count)
                #    print('restos',restos,
                #        'teams2',teams2)
                #    raise('Fdeu')
            mix+=add
            print(mix)
            return mix
                    
            
            
    



def same_team2(t_u,t_s,dix):
    found=False
    i=0
    #print(dix,'dix')
    #print('under',t_u,'sky',t_s)
    while i<len(dix) and not(found):
        #print(t_u==dix[i][0])
        #print(t_u,'|',dix[i][0])
        if t_u==dix[i][0]:
            found=True
        else:
            i+=1
    #print('i',i)
    return t_s==dix[i][1]




#verifica se t1 e t2 são a mesma equipa
#preciso disto, pq às vezes a mesma equipa tem nome diferente
#como 'Norwich' e 'Norwich City'
#def same_team(t1,t2):
#    t1=clear_(t1)
#    t2=clear_(t2)
#    if t1==t2:
#        return True
#    else:
#        t1_list=t1.split(' ')
#        t2_list=t2.split(' ')
#        if len(t1_list)==len(t2_list):
#            return False
#        else:
#            t1_len=len(t1_list)
#            t2_len=len(t2_list)
#            if t1_len<t2_len:
#                t2_list1=t2_list[:t1_len]
#                t2_list2=t2_list[t1_len:]
#                #print(t1_list,t2_list1)
#                if t1_list==t2_list1:
#                    return True                 
#                else:
#                    #print('1')
#                    return False
#                
#            else:
#                t1_list1=t1_list[:t2_len]
#                t1_list2=t1_list[t2_len:]
#                if t2_list==t1_list1:
#                    return True                 
#                else:
#                    return False
# agr estamos a usar same_teams2, não estamos a precisar do same_teams
                
                
#esta função assume que o 1o argumento vem do under e o 2o do sky
#assim é fácil, mas fica bastante específico (é lidar)
def same_league(u,s):
    u=clear_(u)
    s=clear_(s)
    if u==s:
        return True
    else:
        if u=='EPL':
            return s=='Premier League'
        elif u=='RFPL':
            return s=='Russia - Premier Liga'
        elif u=='La liga':
            return s=='Spanish La Liga'
        elif u=='Serie A':
            return s=='Italian Serie A'
        elif u=='Bundesliga':
            return s=='German Bundesliga'
        elif u=='Ligue 1':
            return s=='French Ligue 1'
        else:
            raise('non-identified League, same_league')
            
            
            
            
#verifica se uma df 
#tem todos os valores NaN
#dá jeito para a próxima função
def all_nan(df):
    found=False
    i=1
    while i<=len(df.index) and not(found):
        if not(all(pd.isnull(df.iloc[-i][:]))):
            found=True
            k=i
        i+=1
    if found:
        if k==1:
            return df
    
    return df[:(1-k)]


#prepara uma folha de Under ou Sky para depois fazer Merge
#tal como no Add_ALPHA o "season" é o ano em que acaba a season
#atenção, escrever bem o nome da liga (para as folhas under) 
#under==True : Trata de uma folha under
#under==False : Trata de uma folha sky
def prepare__df(df,season,league,under=True):
    if under:
        print('1',len(df.index))
        df=df.loc[((df["League"]==league))]
        w=[]
        print('2',len(df.index))
        for i in range(len(df.index)):
            w+=[df.iloc[i]['Date']]
        w2=[]
        for n in w: 
            w2+=[UnderStats_Date(n)]
        df=df.drop(['Date'],axis=1)    
        df['Date']=w2   
        df=df.sort_values(['Date'],ascending=True)
        df=df.reset_index(drop=True)
        #last_year=year.df.iloc[-1]['Date']
        found_i=False
        found_f=False
        nn=0
        print(len(df.index))
        while nn <len(df.index) and not(found_i and found_f):
            data=df.iloc[nn]['Date']
            if data.year==(season-1) and data.month>=8 and not(found_i):
                i=nn
                found_i=True
            if data.year==(season) and data.month>=8 and not(found_f):
                f=nn
                found_f=True
            nn+=1
        if not(found_f) and found_i:
            df=df[i:]
        elif found_f and found_i:
            df=df[i:f]
        else:
            raise('WTF!! prepare__df')
        df=df.reset_index(drop=True)
        return df
        
    else:
        print('1',len(df.index))
        df=df.loc[((df["League"]==' '+league))]
        print('2',len(df.index))
        df=df.reset_index(drop=True)
        w=[]
        for i in range(len(df.index)):
            w+=[df.iloc[i]['Date']]
        w2=[]
        w22=[]
        for n in w: 
            #print(SkySports_Date(n)[0].year)
            w2+=[SkySports_Date(n)[0]]
            w22+=[SkySports_Date(n)[1]]
        df=df.drop(['Date'],axis=1)    
        df['Date']=w2 
        df['Time']=w22
        df=df.sort_values(['Date','Time'],ascending=[True,True])
        df=df.reset_index(drop=True)
        print('3',len(df.index))
        #last_year=year.df.iloc[-1]['Date']
        found_i=False
        found_f=False
        nn=0
        while nn <len(df.index) and not(found_i and found_f):
            data=df.iloc[nn]['Date']
            #print(data.year,data.month)
            if data.year==(season-1) and data.month>=8 and not(found_i):
                #print('yellow')
                i=nn
                found_i=True
            if data.year==(season) and data.month>=8 and not(found_f):
                #print('oki oki')
                f=nn
                found_f=True
            nn+=1
        if not(found_f) and found_i:
            df=df[i:]
        elif found_f and found_i:
            df=df[i:f]
        else:
            raise('WTF!! prepare__df')
        df=df.reset_index(drop=True)
        df=all_nan(df)
        return df
    
#calendário russo é diferente    
def prepare__df_Rus(df,season,league,under=True):
    if under:
        print('1',len(df.index))
        df=df.loc[((df["League"]==league))]
        w=[]
        print('2',len(df.index))
        for i in range(len(df.index)):
            w+=[df.iloc[i]['Date']]
        w2=[]
        for n in w: 
            w2+=[UnderStats_Date(n)]
        df=df.drop(['Date'],axis=1)    
        df['Date']=w2   
        df=df.sort_values(['Date'],ascending=True)
        df=df.reset_index(drop=True)
        #last_year=year.df.iloc[-1]['Date']
        found_i=False
        found_f=False
        nn=0
        print(len(df.index))
        while nn <len(df.index) and not(found_i and found_f):
            data=df.iloc[nn]['Date']
            if data.year==(season-1) and data.month>=7 and not(found_i):
                i=nn
                found_i=True
            if data.year==(season) and data.month>=7 and not(found_f):
                f=nn
                found_f=True
            nn+=1
        if not(found_f) and found_i:
            df=df[i:]
        elif found_f and found_i:
            df=df[i:f]
        else:
            raise('WTF!! prepare__df')
        df=df.reset_index(drop=True)
        return df
        
    else:
        print('1',len(df.index))
        df=df.loc[((df["League"]==' '+league))]
        print('2',len(df.index))
        df=df.reset_index(drop=True)
        w=[]
        for i in range(len(df.index)):
            w+=[df.iloc[i]['Date']]
        w2=[]
        w22=[]
        for n in w: 
            #print(SkySports_Date(n)[0].year)
            w2+=[SkySports_Date(n)[0]]
            w22+=[SkySports_Date(n)[1]]
        df=df.drop(['Date'],axis=1)    
        df['Date']=w2 
        df['Time']=w22
        df=df.sort_values(['Date','Time'],ascending=[True,True])
        df=df.reset_index(drop=True)
        print('3',len(df.index))
        #last_year=year.df.iloc[-1]['Date']
        found_i=False
        found_f=False
        nn=0
        while nn <len(df.index) and not(found_i and found_f):
            data=df.iloc[nn]['Date']
            #print(data.year,data.month)
            if data.year==(season-1) and data.month>=7 and not(found_i):
                #print('yellow')
                i=nn
                found_i=True
            if data.year==(season) and data.month>=7 and not(found_f):
                #print('oki oki')
                f=nn
                found_f=True
            nn+=1
        if not(found_f) and found_i:
            df=df[i:]
        elif found_f and found_i:
            df=df[i:f]
        else:
            raise('WTF!! prepare__df')
        df=df.reset_index(drop=True)
        df=all_nan(df)
        return df
    
#trasforma a data do skysports em datetime
#acho que também podíamos pôr as horas em datetime
#Mas por agora,vamos tentar à NASA
Sky_Months_Date={'January':'01','February':'02','March':'03','April':'04','May':'05',
            'June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
def SkySports_Date(sd):
    if type(sd)==pd._libs.tslibs.timestamps.Timestamp or type(sd)==dt.datetime:
        return sd,'NOTIME'
    else:
        sd=sd.split(',')
        time=sd[0]
        date=sd[1]
        #time
        if time[-2:]=='pm':
            time=time[:-2]
            time=time.split(':')
            if int(time[0])==12:
                H=(int(time[0])*100)
            else:
                H=(int(time[0])*100)+1200
            M=int(time[1])
            timez=H+M
        elif time[-2:]=='am':
            time=time[:-2]
            time=time.split(':')
            H=(int(time[0])*100)
            M=int(time[1])
            timez=H+M
        else:
            print('WTF, SkySports_Date-Time')
            return 'Erro'

        #date
        date=date.split(' ')
        D=date[2][:-2]
        M=Sky_Months_Date[date[3]]
        Y=date[4][:-1]
        data=D+'/'+M+'/'+Y
        dataz=dt.datetime.strptime(data,"%d/%m/%Y")

        return dataz, timez
    

#o mesmo que o SkySports_Date, mas sem time, pq não há time 
Under_Months_Date={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                       'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12',} 
def UnderStats_Date(ud):
    ud=ud.split(' ')
    D=ud[1]
    M=Under_Months_Date[ud[0]]
    Y=ud[2]
    data=D+'/'+M+'/'+Y
    dataz=dt.datetime.strptime(data,"%d/%m/%Y")
    return dataz


#verifica se é o mesmo jogo
#g1 e g2 são os índices de cada jogo
#under e sky são as folhas do skysport e uderstats

#precisa de pandas como pd 
def check_same_game(under,sky,g1,g2,dix):
    #print('under',g1,'sky',g2)
    #print('under',type(under.iloc[g1]['Date'])==pd._libs.tslibs.timestamps.Timestamp,'sky',type(sky.iloc[g2]['Date'])==pd._libs.tslibs.timestamps.Timestamp)
    if not(type(under.iloc[g1]['Date'])==pd._libs.tslibs.timestamps.Timestamp) and (type(sky.iloc[g2]['Date'])==pd._libs.tslibs.timestamps.Timestamp):
        #check1=(UnderStats_Date(under.iloc[g1]['Date']).year==SkySports_Date(sky.iloc[g2]['Date'])[0].year and (UnderStats_Date(under.iloc[g1]['Date']).month==SkySports_Date(sky.iloc[g2]['Date']).month))
        check1=((SkySports_Date(sky.iloc[g2]['Date'])[0]-dt.timedelta(2))<=UnderStats_Date(under.iloc[g1]['Date'])<=(SkySports_Date(sky.iloc[g2]['Date'])[0]+dt.timedelta(2)))
    elif type(under.iloc[g1]['Date'])==pd._libs.tslibs.timestamps.Timestamp and not(type(sky.iloc[g2]['Date'])==pd._libs.tslibs.timestamps.Timestamp):
        #check1=(((under.iloc[g1]['Date'].year)==(SkySports_Date(sky.iloc[g2]['Date'])[0]).year) and ((under.iloc[g1]['Date']).month==SkySports_Date(sky.iloc[g2]['Date'])[0].month))
        check1=((SkySports_Date(sky.iloc[g2]['Date'])[0]-dt.timedelta(2))<=under.iloc[g1]['Date']<=(SkySports_Date(sky.iloc[g2]['Date'])[0]+dt.timedelta(2)))
    elif type(sky.iloc[g2]['Date'])==pd._libs.tslibs.timestamps.Timestamp and not(type(under.iloc[g1]['Date'])==pd._libs.tslibs.timestamps.Timestamp):
        #check1=((UnderStats_Date(under.iloc[g1]['Date']).year==(sky.iloc[g2]['Date'].year)) and (UnderStats_Date(under.iloc[g1]['Date']).month==(sky.iloc[g2]['Date'].month)))
        check1=((sky.iloc[g2]['Date']-dt.timedelta(2))<=UnderStats_Date(under.iloc[g1]['Date'])<=(sky.iloc[g2]['Date']+dt.timedelta(2)))
    else:
        #check1=((under.iloc[g1]['Date'].year==sky.iloc[g2]['Date'].year) and (under.iloc[g1]['Date'].month==sky.iloc[g2]['Date'].month))
        check1=((sky.iloc[g2]['Date']-dt.timedelta(2))<=under.iloc[g1]['Date']<=(sky.iloc[g2]['Date']+dt.timedelta(2)))
    try:
        check2=same_team2(under.iloc[g1]['HT'],sky.iloc[g2]['HT'],dix)
    except:
        check2=same_team2(under.iloc[g1]['HT'],sky.iloc[g2]['HomeTeam'],dix) #sky é um ficheiro antigo no attach_odds

    try:
        check3=same_team2(under.iloc[g1]['AT'],sky.iloc[g2]['AT'],dix)
    except:
        check3=same_team2(under.iloc[g1]['AT'],sky.iloc[g2]['AwayTeam'],dix)
    try:
        check4=same_league(under.iloc[g1]['League'],sky.iloc[g2]['League'])
    except:
        #print('Old does not have League')
        check4=True #o ficheiro antigo não tem parâmetro 'League'
    if check1 and check2 and check3 and check4:
        #print('under',g1,'sky',g2)
        #if under.iloc[g1]['HS']!=sky.iloc[g2]['HS'] or under.iloc[g1]['AS']!=(sky.iloc[g2]['AS']):
        #    print('BIG_WTF!!!!!!','g1',g1,' | g2',g2)
        #    print('HOME',under.iloc[g1]['HT'],'AWAY',under.iloc[g1]['AT'])
        return True
    else:
        return False
    
    
def Merge_Sky_Under(sky,under):
    sky_size=len(sky.index)
    under_size=len(under.index)
    print('sky',sky_size,'under',under_size)
    #sky_range=list(range(sky_size)) #esta lista vai dar jeito para tornar o programa mais rápido
    no_find=[] #lista dos jogos não encontrados
    pre_df=[]
    dix=file_teams(sky,under) #lista com as equipas iguais para o check_game_same
    for u in range(under_size):
        print(u, 'of ',under_size)
        s=0
        found=False
        while s<sky_size and not(found):
            if check_same_game(under,sky,u,s,dix):
                #if under.iloc[u]['UnderStatsID'] in [5454, 5459, 5416, 5424, 5443, 5400, 5355, 5370, 5316, 5338, 5268, 5194]:
                #    print('HT',under.iloc[u]['HT'],'| AT',under.iloc[u]['AT'])
                #    print(sky.iloc[s][:])
                #    print('--------------')
                if is_there_nan(sky,s):
                    pass
                    #print('1')
                else:
                    #print('2')
                    datassa=SkySports_Date(sky.iloc[s]['Date'])
                    if type(sky.iloc[s]['Date'])==pd._libs.tslibs.timestamps.Timestamp:
                        data__=sky.iloc[s]['Date']
                        time__=sky.iloc[s]['Time']
                    else:
                        data__=datassa[0]
                        time__=datassa[1]
                    #print('s',s)
                    pre_df+=[[
                        clear_(sky.iloc[s]['League']), data__, 
                        time__, sky.iloc[s]['Attendance'],
                        sky.iloc[s]['HT'], sky.iloc[s]['AT'],
                        ['H' if under.iloc[u]['FTHG']>under.iloc[u]['FTAG'] else 'D' if under.iloc[u]['FTHG']==under.iloc[u]['FTAG'] else 'A'][0] ,
                        under.iloc[u]['FTHG'], 
                        under.iloc[u]['FTAG'], under.iloc[u]['HxG'], under.iloc[u]['AxG'], 
                        under.iloc[u]['HxPTS'], under.iloc[u]['AxPTS'], 
                        sky.iloc[s]['HP'], sky.iloc[s]['AP'], 
                        sky.iloc[s]['HS'], sky.iloc[s]['AS'], sky.iloc[s]['HST'], 
                        sky.iloc[s]['AST'], sky.iloc[s]['HSOT'], sky.iloc[s]['ASOT'], 
                        sky.iloc[s]['HBS'], sky.iloc[s]['ABS'],
                        sky.iloc[s]['HCCC'], sky.iloc[s]['ACCC'], sky.iloc[s]['HPass'], 
                        sky.iloc[s]['APass'], under.iloc[u]['HDEEP'], under.iloc[u]['ADEEP'], 
                        under.iloc[u]['HPPDA'], under.iloc[u]['APPDA'], 
                        sky.iloc[s]['HTack'], sky.iloc[s]['ATack'], 
                        sky.iloc[s]['HAD'], sky.iloc[s]['AAD'],
                        sky.iloc[s]['HCorn'], sky.iloc[s]['ACorn'], sky.iloc[s]['HOff'], 
                        sky.iloc[s]['AOff'], sky.iloc[s]['HSaves'], sky.iloc[s]['ASaves'], 
                        sky.iloc[s]['HF'], sky.iloc[s]['AF'], sky.iloc[s]['HY'], 
                        sky.iloc[s]['AY'], sky.iloc[s]['HR'], sky.iloc[s]['AR']
                    ]]
                    found=True
                    #if len(sky_range)>=5: #acho q podia ser mais pequeno, mas por agora fica assim
                    #    sky_range=sky_range[:s]+sky_range[(s+1):]
                    #    found=True
                        #vamos encortando a lista, para demorar menos tempo a procurar
                #else:
            s+=1
                
        if s==sky_size and not(found):
            no_find+=[under.iloc[u]['UnderStatsID']]
    qw=[] 
    print('last here we go')
    for nn in range(len(pre_df)):
        #print('nn',nn)
        dta=pd.DataFrame({
            'League':pre_df[nn][0],'Date':pre_df[nn][1],'Time':pre_df[nn][2],'Attendance':pre_df[nn][3],
            'HT':pre_df[nn][4],'AT':pre_df[nn][5],'FTR':pre_df[nn][6],'FTHG':pre_df[nn][7],'FTAG':pre_df[nn][8],
            'HxG':pre_df[nn][9],'AxG':pre_df[nn][10],'HxPTS':pre_df[nn][11],'AxPTS':pre_df[nn][12],
            'HP':pre_df[nn][13],'AP':pre_df[nn][14],'HS':pre_df[nn][15],'AS':pre_df[nn][16],
            'HST':pre_df[nn][17],'AST':pre_df[nn][18],'HSOT':pre_df[nn][19],'ASOT':pre_df[nn][20],
            'HBS':pre_df[nn][21],'ABS':pre_df[nn][22],'HCCC':pre_df[nn][23],'ACCC':pre_df[nn][24],
            'HPass':pre_df[nn][25],'APass':pre_df[nn][26],'HDEEP':pre_df[nn][27],'ADEEP':pre_df[nn][28],
            'HPPDA':pre_df[nn][29],'APPDA':pre_df[nn][30],'HTack':pre_df[nn][31],'ATack':pre_df[nn][32],
            'HAD':pre_df[nn][33],'AAD':pre_df[nn][34],'HCorn':pre_df[nn][35],'ACorn':pre_df[nn][36],
            'HOff':pre_df[nn][37],'AOff':pre_df[nn][38],'HSaves':pre_df[nn][39],'ASaves':pre_df[nn][40],
            'HF':pre_df[nn][41],'AF':pre_df[nn][42],'HY':pre_df[nn][43],'AY':pre_df[nn][44],
            'HR':pre_df[nn][45],'AR':pre_df[nn][46]
        },index=[0])
        qw+=[dta]
        #print('aha',len(qw))
    one=pd.concat(qw,sort=False)
    print('original_size: sky',sky_size,'| under',under_size)
    print('no_find',no_find)
    print('file_size',len(one.index))
    return one, no_find


def is_there_nan(df,n,row=None):
    #se existe pelo menos um Nan
    lista=[]
    if row!=None:
        for i in range(len(row.columns)):
            lista+=[pd.isnull(row.iloc[0][i])]
        return any(lista)
    else:
        for i in range(len(df.columns)):
            #print(df.iloc[n][i])
            #print(pd.isnull(df.iloc[n][i]))
            if df.columns[i]=='Attendance': #é específico mas é necessário
                lista+=[False]
            else:
                lista+=[pd.isnull(df.iloc[n][i])]
        #print(lista)
        return any(lista)
    

def save_files(path,w,names): 
    print('Não esquecer do "//" no final path')
    print('w e names têm de estar dentro de uma lista')
    #guarda os ficheiros em w com os nomes em names
    for n, df in enumerate(w):
        df=df.sort_values(['Date','Time'], ascending=[True,True])
        with pd.ExcelWriter(path+names[n]+".xlsx") as writer:
            df.to_excel(writer, names[n], index=None)
        writer.save()
        
        
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
    
    
def add_odds(league,season='all',excel=True):
    old_path='C:\\Users\\joaom\\Documents\\Projetos\\PYTHON\\Apostas\\'+league+'___\\'
    new_path='C:\\Users\\joaom\\Documents\\Projetos\\PYTHON\\Apostas\\New'+league+'___\\'
    if season=='all':
        new_years=os.listdir(new_path)
        #print('new_years',new_years)
        old_years=os.listdir(old_path)
        #print('old_years',old_years)
        year=new_years[0]
        new_y=2000+int(year[-7:-5])
        #print('new_y',new_y)
        old_ind=new_y-2002
        dfs=[]
        names=[]
        for i in range(len(new_years)):
            print(len(new_years))
            print('iiiiiiiiiii',i)
            new_df2=all_datetime((old_path+old_years[i+old_ind])[:-5],write=False)
            print((old_path+old_years[i+old_ind])[:-5],'old')
            print((new_path+new_years[i])[:-5],'new')
            df=attach_odds((new_path+new_years[i])[:-5],new_df2,excel)
            names+=['ODD'+(new_years[i])[:-5]]
            print('ODD'+(new_years[i])[:-5])
            dfs+=[df]
        save_files(new_path,dfs,names)
    else:
        new_years=os.listdir(new_path)
        #print('new_years',new_years)
        old_years=os.listdir(old_path)
        #print('old_years',old_years)
        dfs=[]
        names=[]
        new_ind=season-2015
        old_ind=season-2002
        #for i in range(len(new_years)):
        new_df2=all_datetime((old_path+old_years[old_ind])[:-5],write=False)
        print((old_path+old_years[old_ind])[:-5],'old')
        print((new_path+new_years[new_ind])[:-5],'new')
        df=attach_odds((new_path+new_years[new_ind])[:-5],new_df2,excel)
        names+=['ODD'+(new_years[new_ind])[:-5]]
        print('ODD'+(new_years[new_ind])[:-5])
        dfs+=[df]
        save_files(new_path,dfs,names)
        
def attach_odds(file1,file2,excel=True,read_2=False):
    print('1o arg é o NewFile')
    if excel:
        pd1=pd.read_excel(file1+'.xlsx')
        if read_2:
            pd2=pd.read_excel(file2+'.xlsx')
        else:
            pd2=file2
    else:
        pd1=pd.read_csv(file1+'.csv')
        if read_2:
            pd2=pd.read_csv(file2+'.csv')
        else:
            pd2=file2
    
    dix=file_teams(pd1,pd2)
    oddH=[]
    oddD=[]
    oddA=[]
    for f1 in range(len(pd1.index)):
        if f1%50==0:
            print(f1)
        f2=0
        found=False
        while f2<len(pd2.index) and not(found):
            if check_same_game(pd1,pd2,f1,f2,dix):
                found=True
                oddH+=[pd2.iloc[f2]['ODDH_Aver.']]
                oddD+=[pd2.iloc[f2]['ODDD_Aver.']]
                oddA+=[pd2.iloc[f2]['ODDA_Aver.']]
            else:
                f2+=1
    
    pd1['ODDH_Aver.']=oddH
    pd1['ODDD_Aver.']=oddD
    pd1['ODDA_Aver.']=oddA
        
    return pd1
    