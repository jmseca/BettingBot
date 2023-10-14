print('No final da época 19/20, como houve exceções temos de criar funções '
      'excecionais para obter os jogos de cada ano')

import datetime as dt
import time
import pandas as pd
import numpy as np
import random
import os
import openpyxl
import pickle
import unidecode

pd.set_option('display.max_rows',750)
pd.set_option('display.max_columns',1000)



def input_string_aux(a): #evitar q fique "'qq coisa'"
    if a[0]=="'" and a[-1]=="'":
        a = a[1:-1]
    elif a[0]=='"' and a[-1]=='"':
        a = a[1:-1]
    return a


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




        
            
def file_teams(w1,w2,league): #w1 -> df Sky |||| w2 -> df Under
    #Vamos tornar os nomes das equipas iguais nas duas dfs
    try:
        op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','rb')
        same = pickle.load(op)
        op.close()
    except:
        print('Não leu ficheiro')
        same = [] # lista com os clubes com o mesmo nome [nome Sky,nome Under]
    # vamos manter o nome do Sky
    try:
        sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
        under_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    except:
        try:
            sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
            under_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
        except:
            try:
                sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
                under_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
            except:
                sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
                under_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    i = 0
    under_teams_copy = under_teams.copy()
    sky_teams_copy = sky_teams.copy()
    if same==[]:
        same=[]
        restos=[]
        for ii in range(len(sky_teams)):
            nn=0
            found=False
            while nn<len(under_teams) and not(found):
                if sky_teams[ii]==under_teams[nn]:
                    same+=[[sky_teams[ii],under_teams[nn]]]
                    del under_teams[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[sky_teams[ii]]

        if restos==[]:
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            restos_copy=restos.copy()
            under_teams_copy=under_teams.copy()
            same_copy=same.copy()
            t=0
            while under_teams!=[]:
                print('------')
                print(restos)
                ok=input_string_aux(input(str(under_teams[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    under_teams=under_teams_copy
                    restos=restos_copy
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,under_teams[t]]]
                    del under_teams[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(under_teams):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
    else:
        same_sky = [same[i][0] for i in range(len(same))]
        same_under = [same[i][1] for i in range(len(same))]
        missing_sky = [sky_teams[i] for i in range(len(sky_teams)) if (sky_teams[i] not in same_sky)]
        missing_under = [under_teams[i] for i in range(len(under_teams)) if (under_teams[i] not in same_under)]
        missing_sky_copy = missing_sky.copy()
        missing_under_copy = missing_under.copy()
        same_copy=same.copy()
        
        restos=[]
        if (len(missing_sky)==0) and (len(missing_under)>0):
            t=0
            print(sky_teams)
            time.sleep(0.3)
            while missing_under!=[]:
                ok = input_string_aux(input(str(missing_under[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in sky_teams) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    missing_under=missing_under_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_under[t]]]
                    del missing_under[t]
                if t==len(missing_under):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
                
                
        elif len(missing_sky)==len(missing_under):
            for ii in range(len(missing_sky)):
                nn=0
                found=False
                while nn<len(missing_under) and not(found):
                    if missing_sky[ii]==missing_under[nn]:
                        same+=[[missing_sky[ii],missing_under[nn]]]
                        del missing_under[nn]
                        found=True
                    nn+=1

                if not found:
                    restos+=[missing_sky[ii]]
        else:
            raise Exception('file_teams error. É preciso resolver erro ')
            

        if restos==[]:
            print('What')
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            t=0
            while (restos!=[]) or (missing_under!=[]):
                if len(restos) != len(missing_under):
                    print('We got a problemoooo')
                    raise('aa')
                print(restos)
                ok = input_string_aux(input(str(missing_under[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    restos=restos_copy.copy()
                    missing_under=missing_under_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_under[t]]]
                    del missing_under[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(missing_under):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Teams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same

def update_team_names(sky,under,league):
# vamos mudar o nome das dfs de under para o nome das dfs do sky
#assim podemos fazer um merge usando o np.where
    same = file_teams(sky,under,league)
    same_sky = [same[i][0] for i in range(len(same))]
    same_under = [same[i][1] for i in range(len(same))]
    #HOME
    for i in range(len(same_under)):
        
        try:
            replaceH=list(np.where(under['HT']==same_under[i])[0])
            home='HT'
        except:
            replaceH=list(np.where(under['HomeTeam']==same_under[i])[0])
            home='HomeTeam'
        
        for n in replaceH:
            under.at[n,home]=same_sky[i]
    #AWAY
    for i in range(len(same_under)):
        try:
            replaceH=list(np.where(under['AT']==same_under[i])[0])
            away='AT'
        except:
            replaceH=list(np.where(under['AwayTeam']==same_under[i])[0])
            away='AwayTeam'
        for n in replaceH:
            under.at[n,away]=same_sky[i]  
    return sky,under




def Prepare__Df(df,season,league): 
    df = df.dropna(axis=0,how='all') #retira as linhas cujos valores são todos NaN
    if 'FTHG' in df.columns:
        remove2=[]
        for i in range(len(df)):
            if (pd.isnull(df.iloc[i]['FTHG'])) and (pd.isnull(df.iloc[i]['FTAG'])):
                remove2+=[i]
        df = df.drop(remove2,axis=0)
    df = df.reset_index(drop=True)

    print('Prepare_Df só funciona com as datas já em formato YYYY-mm-dd, e em ligas "normais"')
    tydate = np.array(list(map(lambda x:type(x),list(df['Date']))))
    tstamp = list(map(lambda x:type(x)==pd._libs.tslibs.timestamps.Timestamp,list(df['Date'])))
    if sum(tstamp)==len(df):
        stamp = True
    
    elif len(np.where(tydate==str)[0])==len(df):
        ok = np.array(list(map(lambda x:(x[4]=='-') and (x[7]=='-'),list(df['Date']))))
        if not (ok.all()):
            print('Man, as datas não estão bem')
            ok2 = list(np.where(list(ok)==False)[0])
            print(str(ok2),'São os índices maus' )
            raise('aa')
        stamp = False
    else:
        print(list(map(lambda x:type(x),list(df['Date']))))
        raise Exception('OOps, temos vários tipos de datas nesta df')
    # A parte em cima serve só para ver as datas e verificar que podemos fazer o Prepare__Df
    if not stamp: #vamos passar para datetime (o timestamp é basicamente o mesmo do datetime)
        df['Date']=list(map(lambda x:dt.datetime.strptime(x,'%Y-%m-%d'),list(df['Date'])))
    
    if season==2021: #After Corona season
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime(2020,8,8),df['Date']<=dt.datetime(2021,8,3)),df['League']==league))[0])]
    elif season==2020: #Corona season
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime(2019,8,4),df['Date']<=dt.datetime(2020,8,3)),df['League']==league))[0])]    
    else:
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime((season-1),8,1),df['Date']<=dt.datetime(season,8,1)),df['League']==league))[0])]
        print('Lembrar de verificar as datas limite') 

    if league=='Premiership':
        if season==2021:
            df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime(2020,7,31),df['Date']<=dt.datetime(2021,8,3)),df['League']==league))[0])] 
    
    try:  
        return df1.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    except: #Under não tem Time
        return df1.sort_values(['Date'],ascending=[True]).reset_index(drop=True)
            
            
            
            
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




    
#trasforma a data do skysports em datetime
#acho que também podíamos pôr as horas em datetime
#Mas por agora,vamos tentar à NASA

def SkySports_Date(sd1):
    Sky_Months_Date={'January':'01','February':'02','March':'03','April':'04','May':'05',
            'June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
    if type(sd1)==pd._libs.tslibs.timestamps.Timestamp or type(sd1)==dt.datetime:
        return sd1,'NOTIME'
    else:
        sd=sd1.split(',')
        try:
            time=sd[0]
            date=sd[1]
        except:
            print(sd1)
            print(type(sd1))
            raise Exception('Erro')
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

def UnderStats_Date(ud):
    Under_Months_Date={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                       'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12',} 
    ud=ud.split(' ')
    D=ud[1]
    M=Under_Months_Date[ud[0]]
    Y=ud[2]
    data=D+'/'+M+'/'+Y
    dataz=dt.datetime.strptime(data,"%d/%m/%Y")
    return dataz


def leaguesaux(w,leagues):
    if w in leagues:
        league = leagues[w]
    else:
        print(str(w), 'não está nas leagues')
        league = w
    return league

def Sky_leagues(df): #para termos as Leagues todas iguais
    leagues={
        ' Premier League':'Premier_League',' German Bundesliga':'Bundesliga',' French Ligue 1':'Ligue_1',
        ' Russia - Premier Liga':'RFPL',' Spanish La Liga':'La_Liga',' Italian Serie A':'Serie_A',
        ' Sky Bet Championship':'Championship',' Dutch Eredivisie':'Eredivisie',' Scottish Premiership':'Premiership'}
    L = list(df['League'])
    df['League'] = list(map(lambda x:leaguesaux(x,leagues),L))
    return df
    
    
def Merge_Sky_Under(sky,under):
    leagues=[
        'Premier_League','Bundesliga','Ligue_1',
        'RFPL','La_Liga','Serie_A']
    if len(np.unique(under['League']))==1:
        league = under.iloc[0]['League']
    else:
        if len(np.unique(under['League']))>1:
            raise Exception('DF, mal dividida')
        else:
            raise Exception('Falta a Liga: '+str(under.iloc[0]['League']))
    sky,under=update_team_names(sky,under,league)
    sky_size=len(sky.index)
    under_size=len(under.index)
    print('sky',sky_size,'under',under_size)
    #sky_range=list(range(sky_size)) #esta lista vai dar jeito para tornar o programa mais rápido
    no_find=[] #lista dos jogos não encontrados
    pre_df=[]
    for u in range(under_size):
        print(u, 'of ',under_size)
        
        sg = list(np.where(np.logical_and(sky['HT']==under.iloc[u]['HT'],sky['AT']==under.iloc[u]['AT']))[0])
        if len(sg)>1:
            raise Exception('Whaaaatt?, double game')
        if sg!=[]:
            s=sg[0]
            if is_there_nan(sky,s):
                continue
            else:
                #print('2')
                datassa=SkySports_Date(sky.iloc[s]['Date'])
                if type(sky.iloc[s]['Date'])==pd._libs.tslibs.timestamps.Timestamp:
                    data__=sky.iloc[s]['Date']
                    time__=sky.iloc[s]['Time']
                else:
                    data__=datassa[0]
                    time__=datassa[1]
                print('s',s)
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
        else:
            no_find+=[[under.iloc[u]['HT'],' Vs ',under.iloc[u]['AT']]]
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
    if len(no_find)!=0:
        print(no_find)
        raise Exception('Games Not Found')
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


def to_add_Sky_Under(old_df,new_df):
#adiciona os novos dados ao ficheiro já existente (old_df)
    old_teams = list(map(lambda x,y:x+'-'+y,list(old_df['HT']),list(old_df['AT'])))
    new_teams = list(map(lambda x,y:x+'-'+y,list(new_df['HT']),list(new_df['AT'])))
    to_add = new_df.loc[np.where(np.isin(new_teams,old_teams,invert=True))]
    old_df = pd.concat([old_df,to_add],sort=False)
    return old_df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)


def Sky_Download_drop(df): #prepara uma df do Sky a partir do web Scraper
    df = df.drop(['web-scraper-order','web-scraper-start-url','Games','Games-href'],axis=1)
    df['League'] = list(map(lambda x:x.split('.')[-2],list(df['League'])))
    dtime = list(map(lambda x:SkySports_Date(x),list(df['Date'])))
    time = [i[1] for i in dtime]
    date = [i[0] for i in dtime]
    df['Date'] = date
    df['Time'] = time
    colunas = list(df.columns.values)
    df = df[colunas[0:2]+[colunas[-1]]+colunas[2:(len(colunas)-1)]]
    return Sky_leagues(df)

def PortalAdd_Sky(df):
#divide o to_add, nos jogos mesmo para adicionar e os outros
    dix = {}
    remove=[]
    for i in range(len(df)):
        if (df.iloc[i]['AT'] in dix) or (df.iloc[i]['HT'] in dix):
            remove+=[i]
        if df.iloc[i]['HT'] not in dix:
            dix[df.iloc[i]['HT']]=0
        if df.iloc[i]['AT'] not in dix:
            dix[df.iloc[i]['AT']]=0
    df_add = df.drop(remove,axis=0)
    df_notadd = df.loc[remove]
    #df_notadd, são os jogos que ainda não conseguimos prever (dá jeito para saber qnd temos de fzr scrape outra vez)
    return df_add,df_notadd,len(df_add) 

def Sky_Desktop_drop(df): 
    df = Sky_leagues(df)
    dtime = list(map(lambda x:SkySports_Date(x),list(df['Date'])))
    time = [i[1] for i in dtime]
    date = [i[0] for i in dtime]
    df['Date'] = date
    df['Time'] = time
    colunas = list(df.columns.values)
    df = df[colunas[0:2]+[colunas[-1]]+colunas[2:(len(colunas)-1)]]
    return df

#Save Files Functions -----------------------------------------------------------------------
def get_int_str(r): #dá os inteiros de uma string, seguidos
    s = ''.join(x for x in r if x.isdigit())
    return int(s)

def save_filterSky(w):
    oo=os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data')
    if oo!=[]:
        i1 = max(list(map(lambda x:get_int_str(x),oo)))
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data//SkyGames'+str(i1+1)+'.csv',index=False)            
    else:
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data//SkyGames0.csv',index=False)

def save_rawSky(b):
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info')
    if dir1!=[]:
        dfs = [dir1[i] for i in range(len(dir1)) if ('skygames' in dir1[i])]
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//skygames'+str(i1+1)+'.csv',index=False)
    else:
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//skygames0.csv',index=False)


def save_filterUnder(w):
    oo=os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data')
    if oo!=[]:
        i1 = max(list(map(lambda x:get_int_str(x),oo)))
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data//Under'+str(i1+1)+'.csv',index=False)            
    else:
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data//Under0.csv',index=False)

def save_rawUnder(b):
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info')
    if len(dir1)>1:
        dfs = [dir1[i] for i in range(len(dir1)) if ('under' in dir1[i])]
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//under'+str(i1+1)+'.csv',index=False)
    else:
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//under0.csv',index=False)
#----------------------------------------------------------------------------------------------



def Sky_autofilter():
#verifica quais as dfs q estão no filter data, e faz o filter das dfs que ainda não foram filtered
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info')
    dir2 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data')
    dfs = [dir1[i] for i in range(len(dir1)) if ('skygames' in dir1[i]) and ('Pre' not in dir1[i])]
    if dir2==[] and dir1==[]:
        raise Exception('Sky has no Raw Data')
    elif dir2==[]:
        for i in range(len(dfs)):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//skygames'+str(i)+'.csv')
            try:
                Df=Sky_Download_drop(dff)
            except:
                Df=Sky_Desktop_drop(dff)
            save_filterSky(Df)
            print('Done ',i)
    else:    
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        i2 = max(list(map(lambda x:get_int_str(x),dir2)))
        
        for i in range(i2+1,i1+1):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//skygames'+str(i)+'.csv')
            try:
                Df=Sky_Download_drop(dff)
            except:
                Df=Sky_Desktop_drop(dff)
            save_filterSky(Df)
            print('Done ',i)


def Under_autofilter():
#verifica quais as dfs q estão no filter data, e faz o filter das dfs que ainda não foram filtered
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info')
    dir2 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data')
    dfs = [dir1[i] for i in range(len(dir1)) if ('under' in dir1[i]) and ('Pre' not in dir1[i])]
    if dir2==[] and dir1==[]:
        raise Exception('Under has no Raw Data')
    elif dir2==[]:
        for i in range(len(dfs)):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//under'+str(i)+'.csv')
            Df=Under_Download_drop(dff)
            save_filterUnder(Df)
            print('Done ',i)
    else:    
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        i2 = max(list(map(lambda x:get_int_str(x),dir2)))
        
        for i in range(i2+1,i1+1):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//under'+str(i)+'.csv')
            Df=Under_Download_drop(dff)
            save_filterUnder(Df)
            print('Done ',i)

def Under_leagues(df): #para termos as Leagues todas iguais
    leagues={
        'EPL':'Premier_League','Bundesliga':'Bundesliga','Ligue 1':'Ligue_1',
        'RFPL':'RFPL','La liga':'La_Liga','Serie A':'Serie_A'}
    L = list(df['League'])
    df['League'] = list(map(lambda x:leaguesaux(x,leagues),L))
    return df

def Under_Download_drop(df):
    df = Under_leagues(df)
    df = df.drop(['web-scraper-order','web-scraper-start-url','Games','Games-href'],axis=1)
    df = df.rename(columns={'HomeTeam':'HT','AwayTeam':'AT','HGoals':'FTHG','AGoals':'FTAG'})
    df['Date'] = list(map(lambda x:UnderStats_Date(x),list(df['Date'])))
    return df

def Under_Desktop_drop(df):
    df = Under_leagues(df)
    df['Date'] = list(map(lambda x:UnderStats_Date(x),list(df['Date'])))
    df = df.rename(columns={'HomeTeam':'HT','AwayTeam':'AT','HGoals':'FTHG','AGoals':'FTAG'})
    return df



def get_old_df(league,season):
#vai buscar o ficheiro com os jogos já guardados de uma season específica
    dfs = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//ADF//'+league+'//')
    dfs2 = np.array(list(map(lambda x:x[-7:-5],dfs)))
    try:
        ahah = list(np.where(dfs2==season[2:])[0])
        ind = ahah[0]
        if len(ahah)>1:
            raise Exception('Double DF da League: '+league+' (nas "bases de dados")')

    except:
        #se ainda não houver df desta liga desta season, devolve-se uma df vazia
        return pd.DataFrame({})
    return pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//ADF//'+league+'//'+dfs[ind])


def OldNew_Merge(old_df,new_df):
#Faz o merge da df antiga e da nova e verifica se a informação foi bem "scrapada"
    if old_df.empty:
        return new_df
    old_df = old_df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    date_old = old_df.iloc[-1]['Date']
    date_new = new_df.iloc[0]['Date']
    if date_new > date_old:
        DF = pd.concat([old_df,new_df],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
        return DF
    else:
        same = list(np.where(np.logical_and(old_df['HT']==new_df.iloc[0]['HT'],old_df['AT']==new_df.iloc[0]['AT']))[0])
        if len(same)!=1:
            raise Exception('Double Game')
        else:
            ind = same[0]
            if (old_df.iloc[ind-1]['FTR'] not in ['H','D','A']) and (ind>0): #assim se for 0 não dá -1 e isso era chato
                raise Exception('Bad Scrape, Games missing')
            old_df_add = old_df[:ind]
            DF = pd.concat([old_df_add,new_df],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
            return Df



def days_diff(x,y): #absoluto do número de dias de diferença entre duas datas
    if isinstance(x,str):
        if '-' in x:
            try:
                x=dt.datetime.strptime(x,'%Y-%m-%d')
            except:
                try:
                    x = x.split(' ')[0]
                    x=dt.datetime.strptime(x,'%Y-%m-%d')
                except:
                    print(x)
                    raise Exception('Erro days_diff')
        else:
            print(x)
            raise Exception('Weird Date string')
    if isinstance(y,str):
        if '-' in y:
            try:
                y=dt.datetime.strptime(y,'%Y-%m-%d')
            except:
                try:
                    y = y.split(' ')[0]
                    y=dt.datetime.strptime(y,'%Y-%m-%d')
                except:
                    print(y)
                    raise Exception('Erro days_diff')
        else:
            print(y)
            raise Exception('Weird Date string')
    diff = abs((x-y).days)
    return diff


def merge_SU(df): #faz o merge do Sky (S) e do Under (U)
    #df = pd.concat(w,sort=False)
    df = df.dropna(axis=0,how='all') #retira as linhas cujos valores são todos NaN
    try:
        df = df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    except:
        df = df.sort_values(['Date'],ascending=[True]).reset_index(drop=True) #under não tem Time

    i=0
    while i<len(df):
        same = list(np.where(np.logical_and(
        np.logical_and(df['HT']==df.iloc[i]['HT'],df['AT']==df.iloc[i]['AT']),
        np.logical_and(np.array(list(map(lambda x,y:days_diff(x,y),list(df['Date']),[df.iloc[i]['Date']]*len(list(df['Date'])))))<=10,
        df['League']==df.iloc[i]['League'])))[0])
        if len(same)==1:
            i+=1
        else:
            del same[0]
            df = df.drop(same,axis=0).reset_index(drop=True)
            #!!!!!!!!!!!!!!!!!!!!!        
            #Se precisar do 25 e do BS, mudar este merge, para tentar ter um q não tenha 'None' nessas odds
            #!!!!!!!!!!!!!!!!!!!!!!
    return df



def Predix_Odds(predix,boods): #junta ao ficheiro predix, as odds do Betano_odds
    #Está no Sky_Under
    to_add=pd.DataFrame({})
    dixy=pd.DataFrame({})
    x = boods.columns[-1][-1]
    for p in range(len(predix)):
        same = list(np.where(np.logical_and(
        np.logical_and(boods['HT']==predix.iloc[p]['HT'],boods['AT']==predix.iloc[p]['AT']),
        np.logical_and(np.array(list(map(lambda x,y:days_diff(x,y),list(boods['Date']),[predix.iloc[p]['Date']]*len(list(boods['Date'])))))<=10,
        boods['League']==predix.iloc[p]['League'])))[0])
        if same==[]:
            print(predix.iloc[p]['HT'],' Vs ',predix.iloc[p]['AT'], ' - No ODDS')
            for i in range(1,x+1):
                if i==1:
                    dix = {'ODDH_TOP1':['None'],'Time_1':['None']}
                else:
                    dix.update({'ODDH_TOP'+str(i):['None'],'Time_'+str(i):['None']})
        elif len(same)>1:
            raise Exception('Double Game, Predix_Odds')
        else:
            ss = same[0]
            for i in range(1,x+1):
                if i==1:
                    dix = {'ODDH_TOP1':[predix.iloc[ss]['ODDH_TOP1']],'Time_1':[predix.iloc[ss]['Time_1']]}
                else:
                    dix.update({'ODDH_TOP'+str(i):[predix.iloc[ss]['ODDH_TOP'+str(i)]],'Time_'+str(i):[predix.iloc[ss]['Time_'+str(i)]]})
        dixy = pd.concat([dixy,dix],axis=0,sort=False)           
    predix = pd.concat([predix,dixy],axis=1,sort=False)
    return predix


# SkyFGAMES----------------------------------------
def sfg_warning(df):
    #trata dos warnings do SkyFgames do GameCheck
    remove_sfg=[]
    for i in range(len(df)):
        if pd.isnull(df.iloc[i]['GameCheck']):
            pass
        elif df.iloc[i]['GameCheck']=='Postponed : Fixture Clash':
            remove_sfg+=[i]
        else:
            raise Exception('GameCheck wtf value')
    df = df.drop(remove_sfg,axis=0)
    return df.reset_index(drop=True)

def SkyFG_Desktop_drop(df): 
    df = Sky_leagues(df)
    df = sfg_warning(df)
    dtime = list(map(lambda x:SkySports_Date(x),list(df['Date'])))
    time = [i[1] for i in dtime]
    date = [i[0] for i in dtime]
    df['Date'] = date
    df['Time'] = time
    colunas = list(df.columns.values)
    df = df[colunas[0:2]+[colunas[-1]]+colunas[2:(len(colunas)-1)]]
    return df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)