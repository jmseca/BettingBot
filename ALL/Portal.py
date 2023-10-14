import pandas as pd
import numpy as np
import time
import os
import datetime as dt
import unidecode
import pickle
from functools import reduce



def input_string_aux(a): #evitar q fique "'qq coisa'"
    if a[0]=="'" and a[-1]=="'":
        a = a[1:-1]
    elif a[0]=='"' and a[-1]=='"':
        a = a[1:-1]
    return a


def leaguesaux(w,leagues):
    if w in leagues:
        league = leagues[w]
    else:
        print(str(w), 'não está nas leagues')
        league = w
    return league
    
def Portal_leagues(df): #para termos as Leagues todas iguais
    leagues = {'Champions League':'Champions','Championship':'Championship',
              'Europa League':'Europa_League','Ligue 1':'Ligue_1','MLS':'MLS',
              'Premier League':'Premier_League','Premiership':'Premiership',
              'Primeira Liga':'Primeira_Liga','Serie A':'Serie_A','LaLiga':'La_Liga',
              'Bundesliga':'Bundesliga','Eredivisie':'Eredivisie','RFPL':'RFPL'}
    L = list(df['League'])
    df['League'] = list(map(lambda x:leaguesaux(x,leagues),L))
    return df



#def Add_Portal(sky,portal):
#    leagues={
#        'Premier League':'Premier_League','German Bundesliga':'Bundesliga','French Ligue 1':'Ligue_1',
#        'Russia - Premier Liga':'RFPL','Spanish La Liga':'La_Liga','Italian Serie A':'Serie_A'}
#    only_league = list(np.unique(sky['League']))
#    if len(only_league)!=1:
#        print('DF mal Dividida')
#        raise('aa')
#    else:
#        league1 = only_league[0]
#        if league1 not in leagues:
#            print('Liga do Sky:'+str(league1)+' não está no dict')
#            raise('aa')
#        else:
#            league = leagues[league1]
#    sky,portal=update_team_names(sky,portal,league)
#    sky_size=len(sky.index)
#    portal_size=len(portal.index)
#    print('sky',sky_size,'portal',portal_size)
#    #sky_range=list(range(sky_size)) #esta lista vai dar jeito para tornar o programa mais rápido
#    sky = sky.append(portal)
#    return sky
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


def portal_timeaux(time):
    time = time.split(':')
    hours = (int(time[0])*100)+int(time[1])
    return hours

def portal_dateaux(date):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12} #temos de ir atualizando
    date=date.split('  ')
    day,month1= date[0].split(' ')
    year = str(date[1])
    if month1 in months:
        month=months[month1]
    else:
        print('Month missing, portal_dateaux')
        raise('AA')
    Date = dt.datetime.strptime(str(day)+'/'+str(month)+'/'+str(year),'%d/%m/%Y')
    return Date


def portal_date(dt): #dt é uma lista com as datas
    m = list(map(lambda x:x.split(', '),dt))
    dateL = [i[1] for i in m]
    timeL = [i[2] for i in m]
    time = list(map(lambda x:portal_timeaux(x),timeL))
    date = list(map(lambda x:portal_dateaux(x),dateL))
    return time,date

def portal_pl_rfpl(df): #no portal, RFPL e a PL têm o mesmo nome
#esta função resolve o problema 
    for i in range(len(df)):
        if df.iloc[i]['Country']=='Russia' and (df.iloc[i]['League']=='Premier League'):
            df.at[i,'League']='RFPL'
        elif df.iloc[i]['Country']=='Russia' and (df.iloc[i]['League']!='Premier League'):
            raise Exception('Russia mudou nome da liga no Portal')
    return df



def portal_drop(df): #devolve uma df do portal com apenas aquilo q precisamos
    df = portal_pl_rfpl(df)
    warn = list(np.where(df['Warning'].isnull().values==False)[0]) #índices onde temos warning
    df = df.drop(warn,axis=0)
    df = df.drop(['web-scraper-order','web-scraper-start-url','Games','Games-href','Country'],axis=1)
    df = df.reset_index(drop=True)
    teams2 = list(map(lambda x:x.split(' - '),list(df['Teams'])))
    ht = [teams2[i][0] for i in range(len(teams2))]
    at = [teams2[i][1] for i in range(len(teams2))]
    Time,Date = portal_date(list(df['Date']))
    new_df = pd.DataFrame({'League':list(df['League']),
                          'Date':Date,'Time':Time,'HT':ht,'AT':at})
    new_df = Portal_leagues(new_df)
    return new_df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)


def get_int_str(r): #dá os inteiros de uma string, seguidos
    s = ''.join(x for x in r if x.isdigit())
    return int(s)

def save_filterPortal(w):
    oo=os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data')
    if oo!=[]:
        i1 = max(list(map(lambda x:get_int_str(x),oo)))
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data//Portal'+str(i1+1)+'.csv',index=False)            
    else:
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data//Portal0.csv',index=False)

def save_rawPortal(b):
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info')
    if len(dir1)>1:
        dfs = [dir1[i] for i in range(len(dir1)) if ('portal' in dir1[i])]
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//portal'+str(i1+1)+'.csv',index=False)
    else:
        b.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//portal0.csv',index=False)


def Portal_autofilter():
#verifica quais as dfs q estão no filter data, e faz o filter das dfs que ainda não foram filtered
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info')
    dir2 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data')
    dfs = [dir1[i] for i in range(len(dir1)) if ('portal' in dir1[i]) and ('Pre' not in dir1[i])]
    if dir2==[] and dir1==[]:
        raise Exception('Portal has no Raw Data')
    elif dir2==[]:
        for i in range(len(dfs)):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//portal'+str(i)+'.csv')
            Df = portal_drop(dff)
            save_filterPortal(Df)
            print('Done ',i)
    else:    
        i1 = max(list(map(lambda x:get_int_str(x),dfs)))
        i2 = max(list(map(lambda x:get_int_str(x),dir2)))
        
        for i in range(i2+1,i1+1):
            dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//portal'+str(i)+'.csv')
            Df = portal_drop(dff)
            save_filterPortal(Df)
            print('Done ',i)

##########
##########
#Parte do Portal+Sky
##########
##########

def Portal_file_teams_old(w1,w2,league): #w1 -> df Sky |||| w2 -> df portal
    #Vamos tornar os nomes das equipas iguais nas duas dfs
    try:
        op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','rb')
        same = pickle.load(op)
        op.close()
    except:
        print('Não leu ficheiro')
        same = [] # lista com os clubes com o mesmo nome [nome Sky,nome portal]
    # vamos manter o nome do Sky
    try:
        sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
        portal_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    except:
        sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
        portal_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
    i = 0
    portal_teams_copy = portal_teams.copy()
    sky_teams_copy = sky_teams.copy()
    if same==[]:
        same=[]
        restos=[]
        for ii in range(len(sky_teams)):
            nn=0
            found=False
            while nn<len(portal_teams) and not(found):
                if sky_teams[ii]==portal_teams[nn]:
                    same+=[[sky_teams[ii],portal_teams[nn]]]
                    del portal_teams[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[sky_teams[ii]]

        if restos==[]:
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            restos_copy=restos.copy()
            portal_teams_copy=portal_teams.copy()
            same_copy=same.copy()
            t=0
            while portal_teams!=[]:
                print('------')
                print(restos)
                ok=input_string_aux(input(str(portal_teams[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    portal_teams=portal_teams_copy
                    restos=restos_copy
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,portal_teams[t]],[portal_teams[t],ok]]
                    del portal_teams[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(portal_teams):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
    else:
        same_sky = [same[i][0] for i in range(len(same))]
        same_portal = [same[i][1] for i in range(len(same))]
        missing_sky = [sky_teams[i] for i in range(len(sky_teams)) if (sky_teams[i] not in same_sky)]
        missing_portal = [portal_teams[i] for i in range(len(portal_teams)) if (portal_teams[i] not in same_portal)]
        missing_sky_copy = missing_sky.copy()
        missing_portal_copy = missing_portal.copy()
        same_copy=same.copy()
        
        restos=[]
        for ii in range(len(missing_sky)):
            nn=0
            found=False
            while nn<len(missing_portal) and not(found):
                if missing_sky[ii]==missing_portal[nn]:
                    same+=[[missing_sky[ii],missing_portal[nn]]]
                    del missing_portal[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[missing_sky[ii]]

        if restos==[]:
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            t=0
            while (restos!=[]) or (missing_portal!=[]):
                if len(restos) != len(missing_portal):
                    print('We got a problemoooo')
                    raise('aa')
                print(restos)
                ok = input_string_aux(input(str(missing_portal[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    restos=restos_copy.copy()
                    missing_portal=missing_portal_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_portal[t]]]
                    del missing_portal[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(missing_portal):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same


def Portal_file_teams(w1,w2,league): #w1 -> df Sky |||| w2 -> df portal
    #Vamos tornar os nomes das equipas iguais nas duas dfs
    try:
        op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','rb')
        same = pickle.load(op)
        op.close()
    except:
        print('Não leu ficheiro')
        same = [] # lista com os clubes com o mesmo nome [nome Sky,nome portal]
    # vamos manter o nome do Sky
    try:
        sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
        portal_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    except:
        try:
            sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
            portal_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
        except:
            try:
                sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
                portal_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
            except:
                sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
                portal_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    i = 0
    portal_teams_copy = portal_teams.copy()
    sky_teams_copy = sky_teams.copy()
    print('SKYyy',sky_teams)
    print('Under',portal_teams)
    if same==[]:
        same=[]
        restos=[]
        for ii in range(len(sky_teams)):
            nn=0
            found=False
            while nn<len(portal_teams) and not(found):
                if portal_teams[nn]=='Paris SG':
                    print(sky_teams[ii],portal_teams[nn])
                if sky_teams[ii]==portal_teams[nn]:
                    print('yes')
                    same+=[[sky_teams[ii],portal_teams[nn]]]
                    del portal_teams[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[sky_teams[ii]]

        if restos==[]:
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            restos_copy=restos.copy()
            portal_teams_copy=portal_teams.copy()
            same_copy=same.copy()
            t=0
            print('same',same)
            while portal_teams!=[]:
                print('------')
                print(restos)
                ok=input_string_aux(input(str(portal_teams[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    portal_teams=portal_teams_copy
                    restos=restos_copy
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,portal_teams[t]]]
                    del portal_teams[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(portal_teams):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
    else:
        same_sky = [same[i][0] for i in range(len(same))]
        same_portal = [same[i][1] for i in range(len(same))]
        missing_sky = [sky_teams[i] for i in range(len(sky_teams)) if (sky_teams[i] not in same_sky)]
        missing_portal = [portal_teams[i] for i in range(len(portal_teams)) if (portal_teams[i] not in same_portal)]
        missing_sky_copy = missing_sky.copy()
        missing_portal_copy = missing_portal.copy()
        same_copy=same.copy()
        
        restos=[]
        if (len(missing_sky)==0) and (len(missing_portal)>0):
            t=0
            print(sky_teams)
            time.sleep(0.3)
            while missing_portal!=[]:
                ok = input_string_aux(input(str(missing_portal[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in sky_teams) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    missing_portal=missing_portal_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_portal[t]]]
                    del missing_portal[t]
                if t==len(missing_portal):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
                
                
        elif len(missing_sky)==len(missing_portal):
            for ii in range(len(missing_sky)):
                nn=0
                found=False
                while nn<len(missing_portal) and not(found):
                    if missing_sky[ii]==missing_portal[nn]:
                        same+=[[missing_sky[ii],missing_portal[nn]]]
                        del missing_portal[nn]
                        found=True
                    nn+=1

                if not found:
                    restos+=[missing_sky[ii]]
        else:
            print('Sky',missing_sky)
            print('Portal',missing_portal)
            raise Exception('file_teams error. É preciso resolver erro ')
            

        if restos==[]:
            print('What')
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            t=0
            while (restos!=[]) or (missing_portal!=[]):
                if len(restos) != len(missing_portal):
                    print('We got a problemoooo')
                    raise('aa')
                print(restos)
                ok = input_string_aux(input(str(missing_portal[t])+'? (write "passa" if not sure Or "reset" to restart) '))
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    restos=restos_copy.copy()
                    missing_portal=missing_portal_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_portal[t]]]
                    del missing_portal[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(missing_portal):
                    t=0
            op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same


def Portal_ao_teams(df,portal,league):
    #utn para o portal_addodds
    try:
        op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','rb')
        same = pickle.load(op)
        op.close()
    except:
        print('Não leu ficheiro')
        same = [] # lista com os clubes com o mesmo nome [nome Sky,nome portal]
    df_t=list(np.unique(list(np.unique(df['HT']))+list(np.unique(df['AT']))))
    df_p=list(np.unique(list(np.unique(portal['HT']))+list(np.unique(portal['AT']))))
    df_p_copy = df_p.copy()
    df_t_copy = df_t.copy()
    same_copy=same.copy()

    try:
        same_t = [same[i][0] for i in range(len(same))]
        okok = True
        i=0
        print(same_t)
        while okok and (i<len(df_t)):
            print(df_t[i])
            if df_t[i] not in same_t:
                print('OOps')
                okok=False
            i+=1
    except:
        okok = False
    if not(okok):
        t=0
        while (df_t!=[]):
            print(df_t)
            ok = input_string_aux(input(str(df_p[t])+'? (write "passa" if not sure Or "reset" to restart) '))
            if ok!='passa' and (ok not in df_t) and (ok!='reset'):
                print('Erro na palavra')
                continue
            if ok=='passa':
                t+=1
                continue
            if ok=='reset':
                t=0
                df_p=df_p_copy.copy()
                df_t=df_t_copy.copy()
                same=same_copy.copy()
                continue
            else:
                same+=[[ok,df_p[t]]]
                del df_p[t]
                del df_t[np.where(np.array(df_t)==ok)[0][0]]
            if t==len(df_p):
                t=0
        op = open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//PortalTeams_'+league+'.pickle','wb')
        pickle.dump(same,op)
        op.close()
            
    same_sky = [same[i][0] for i in range(len(same))]
    same_portal = [same[i][1] for i in range(len(same))]
    #HOME
    for i in range(len(same_portal)):
        try:
            replaceH=list(np.where(portal['HT']==same_portal[i])[0])
            home='HT'
        except:
            replaceH=list(np.where(portal['HomeTeam']==same_portal[i])[0])
            home='HomeTeam'
        for n in replaceH:
            portal.at[n,home]=same_sky[i]
    #AWAY
    for i in range(len(same_portal)):
        try:
            replaceH=list(np.where(portal['AT']==same_portal[i])[0])
            away='AT'
        except:
            replaceH=list(np.where(portal['AwayTeam']==same_portal[i])[0])
            away='AwayTeam'
        for n in replaceH:
            portal.at[n,away]=same_sky[i]  
    return df,portal

def Portal_addodds(portal,df,league):
    if league not in ['Bundesliga','Ligue_1','La_Liga','Serie_A','Premier_League','Eredivisie','Championship','Premiership']:
        print(['Bundesliga','Ligue_1','La_Liga','Serie_A','Premier_League','Eredivisie','Championship','Premiership'])
        raise Exception('Invalid League: ',str(league))
    df,portal = Portal_ao_teams(df,portal,league)
    
    try:
        df = df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    except:
        df = df.sort_values(['Date'],ascending=[True]).reset_index(drop=True) #under não tem Time
    i=0
    ODDS = True
    if 'ODDH_Aver.' not in list(df.columns):
        oddh=[]
        oddd=[]
        odda=[]
        ODDS = False
    while i<len(df):
        same = list(np.where(np.logical_and(
        np.logical_and(portal['HT']==df.iloc[i]['HT'],portal['AT']==df.iloc[i]['AT']),
        np.array(list(map(lambda x,y:days_diff(x,y),list(portal['Date']),[df.iloc[i]['Date']]*len(list(portal['Date'])))))<=10
        ))[0])
        if len(same)==1:
            if ODDS:
                if pd.isnull(df.iloc[i]['ODDH_Aver.']) or (df.iloc[i]['ODDH_Aver.']=='None'): 
                    df.at[i,'ODDH_Aver.'] = portal.iloc[same[0]]['ODDH']
                    df.at[i,'ODDD_Aver.'] = portal.iloc[same[0]]['ODDD']
                    df.at[i,'ODDA_Aver.'] = portal.iloc[same[0]]['ODDA']
                else:
                    pass
            else:
                oddh+=[portal.iloc[same[0]]['ODDH']]
                oddd+=[portal.iloc[same[0]]['ODDD']]
                odda+=[portal.iloc[same[0]]['ODDA']]
            i+=1 
        elif len(same)==0:
            if ODDS:
                pass
            else:

                oddh+=['None']
                oddd+=['None']
                odda+=['None']
            i+=1   
        else:
            raise Exception('Double Game')
            #!!!!!!!!!!!!!!!!!!!!!        
            #Se precisar do 25 e do BS, mudar este merge, para tentar ter um q não tenha 'None' nessas odds
            #!!!!!!!!!!!!!!!!!!!!!!
    if not(ODDS):
        df['ODDH_Aver.']=oddh
        df['ODDD_Aver.']=oddd
        df['ODDA_Aver.']=odda
    return df

def Portal_utn(sky,portal,league): #update_team_names
# vamos mudar o nome das dfs de portal para o nome das dfs do sky
#assim podemos fazer um merge usando o np.where
    same = Portal_file_teams(sky,portal,league)
    same_sky = [same[i][0] for i in range(len(same))]
    same_portal = [same[i][1] for i in range(len(same))]
    #HOME
    for i in range(len(same_portal)):
        try:
            replaceH=list(np.where(portal['HT']==same_portal[i])[0])
            home='HT'
        except:
            replaceH=list(np.where(portal['HomeTeam']==same_portal[i])[0])
            home='HomeTeam'
        for n in replaceH:
            portal.at[n,home]=same_sky[i]
    #AWAY
    for i in range(len(same_portal)):
        try:
            replaceH=list(np.where(portal['AT']==same_portal[i])[0])
            away='AT'
        except:
            replaceH=list(np.where(portal['AwayTeam']==same_portal[i])[0])
            away='AwayTeam'
        for n in replaceH:
            portal.at[n,away]=same_sky[i]  
    return sky,portal


def Prepare__Df(df,season,league): 
    print('Prepare_Df só funciona com as datas já em formato YYYY-mm-dd, e em ligas "normais"')
    tydate = np.array(list(map(lambda x:type(x),list(df['Date']))))
    tstamp = list(map(lambda x:x==pd._libs.tslibs.timestamps.Timestamp,list(df['Date'])))
    if len(tstamp)==len(df):
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
        print(tstamp)
        print('OOps, temos vários tipos de datas nesta df')
        raise('aa')
    
    # A parte em cima serve só para ver as datas e verificar que podemos fazer o Prepare__Df
    if not stamp: #vamos passar para datetime (o timestamp é basicamente o mesmo do datetime)
        df['Date']=list(map(lambda x:dt.datetime.strptime(x,'%Y-%m-%d'),list(df['Date'])))
    if season==2020: #Corona season
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime(2019,8,4),df['Date']<=dt.datetime(2020,8,3)),df['League']==league))[0])]
    elif season==2021: #After Corona season
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime(2020,8,8),df['Date']<=dt.datetime(2021,8,3)),df['League']==league))[0])]    
    else:
        df1=df.loc[list(np.where(np.logical_and(np.logical_and(df['Date']>=dt.datetime((league-1),8,1),df['Date']<=dt.datetime(league,8,1)),df['League']==league))[0])]
        print('Lembrar de verificar as datas limite')    
    return df1.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)



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