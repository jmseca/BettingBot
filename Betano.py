import pandas as pd
import numpy as np
import time
import os
import datetime as dt
from functools import reduce

#1. Funções do Betano
leagues_betano = {
    'Championship':'Championship', 'LaLiga':'La_Liga',
    'Liga Europa - Jogos':'Liga_Europa','Liga dos Campeões - Jogos':'Champions',
    'MLS':'MLS','Premier League' : 'Premier_League',
    'Premier Liga':'RFPL','Premiership':'Premiership',
    'Primeira Liga':'Primeira_Liga','Série A': 'Serie_A'
}

def Betano_date(x):
    months = {
        'Janeiro':1,'Fevereiro':2,'Março':3,'Abril':4,'Maio':5,'Junho':6,
        'Julho':7,'Agosto':8,'Setembro':9,'Outubro':10,'Novembro':11,'Dezembro':12
    }
    try:
        x = x.split(', ')[1]
        day,month,year,time=x.split(' ')
        #date
        if month not in months:
            print(month)
            month = input('Qual é o mês?   ')
        else:
            month = months[month]
        date = dt.datetime.strptime(str(day)+'/'+str(month)+'/'+str(year),'%d/%m/%Y')
        #time
        h,m=time.split(':')
        H=int(h)*100
        time = H+int(m)
        return date,time
    except:
        return 'None','None'

def Betano_league(x,leagues):
    if x not in leagues:
        print(x)
        return 'None'
    else:
        return leagues[x]
    
def Betano_nan(df): #remove os scrapes falhados
    lig=list(np.where(df['League'].isnull().values)[0])
    rest=list(np.where(np.logical_and(df['Date'].isnull().values,df['HomeTeam'].isnull().values,
                                     df['AwayTeam'].isnull().values))[0])
    dele = list(np.unique(np.array(lig+rest)))
    print(dele)
    df=df.drop(dele,axis=0).reset_index(drop=True)
    return df

def europe_filter(df):
    for i in range(len(df)):
        if (df.iloc[i]['League']=='Liga_Europa') or (df.iloc[i]['League']=='Champions'):
            for c in list(df.columns[8:-2]):
                df.at[i,c]='None'
    return df


def Betano_filter(df,l=leagues_betano):
    df = Betano_nan(df)
    Dates = [df.iloc[i]['Date'] for i in range(len(df))]
    date_time = list(map(Betano_date,Dates))
    
    try:
        sDates = [df.iloc[i]['Current_Date'] for i in range(len(df))]
        sdate_time = list(map(Betano_date,sDates))
    except:
        pass
    
    Leag = [df.iloc[i]['League'] for i in range(len(df))]
    League = list(map(Betano_league,Leag,[l]*len(Leag)))
    Y25=[]
    N25=[]
    YBS=[]
    NBS=[]
    X1=[]
    _12=[]
    X2=[]
    for i in range(len(df)):
        #25
        if df.iloc[i]['Tag25']=='Mais de2.5':
            Y25+=[df.iloc[i]['ODD_25+']]
            N25+=[df.iloc[i]['ODD_25-']]
        elif df.iloc[i]['Tag15']=='Mais de2.5':
            Y25+=[df.iloc[i]['ODD_15+']]
            N25+=[df.iloc[i]['ODD_15-']]
        elif df.iloc[i]['Tag35']=='Mais de2.5':
            Y25+=[df.iloc[i]['ODD_35+']]
            N25+=[df.iloc[i]['ODD_35-']]
        else:
            if (df.iloc[i]['League']=='Liga Europa - Jogos') or (df.iloc[i]['League']=='Liga dos Campeões - Jogos'):
                Y25+=['None']
                N25+=['None']
            else:
                print(df.iloc[i]['League'],i)
                print('problema com 25')
                print('---------------')
                Y25+=['None']
                N25+=['None']
            
        #BS
        if df.iloc[i]['TagBS']=='Ambas Equipas Marcam (Sim/Não)':
            YBS+=[df.iloc[i]['ODD_BthScore_Yes']]
            NBS+=[df.iloc[i]['ODD_BthScore_No']]
        else:
            if (df.iloc[i]['League']=='Liga Europa - Jogos') or (df.iloc[i]['League']=='Liga dos Campeões - Jogos'):
                YBS+=['None']
                NBS+=['None']
            else:
                print(df.iloc[i]['League'],i)
                print('problema com BS')
                print('---------------')
                YBS+=['None']
                NBS+=['None']
            
        #DC
        if df.iloc[i]['Tag1X']=='1X':
            X1+=[df.iloc[i]['ODD_1X']]
        elif df.iloc[i]['Tag12']=='1X':
            X1+=[df.iloc[i]['ODD_12']]
        elif df.iloc[i]['TagX2']=='1X':
            X1+=[df.iloc[i]['ODD_X2']]
        else:
            X1+=['None']
        #--------------------------------------------------   
        if df.iloc[i]['Tag1X']=='12':
            _12+=[df.iloc[i]['ODD_1X']]
        elif df.iloc[i]['Tag12']=='12':
            _12+=[df.iloc[i]['ODD_12']]
        elif df.iloc[i]['TagX2']=='12':
            _12+=[df.iloc[i]['ODD_X2']]
        else:
            _12+=['None']    
        #---------------------------------------------------
        if df.iloc[i]['Tag1X']=='2X':
            X2+=[df.iloc[i]['ODD_1X']]
        elif df.iloc[i]['Tag12']=='2X':
            X2+=[df.iloc[i]['ODD_12']]
        elif df.iloc[i]['TagX2']=='2X':
            X2+=[df.iloc[i]['ODD_X2']]
        else:
            X2+=['None']
            
    ODDH = list(df.iloc[:]['ODDH'])
    ODDD = list(df.iloc[:]['ODDD'])
    ODDA = list(df.iloc[:]['ODDA'])
    Date = [date_time[i][0] for i in range(len(date_time))]
    Time = [date_time[i][1] for i in range(len(date_time))]
    
    try:
        sDate = [sdate_time[i][0] for i in range(len(sdate_time))]
        sTime = [sdate_time[i][1] for i in range(len(sdate_time))]
    except:
        pass
    
    HT = list(map(lambda x:unidecode.unidecode(x),list(df.iloc[:]['HomeTeam'])))
    AT = list(map(lambda x:unidecode.unidecode(x),list(df.iloc[:]['AwayTeam'])))
    
    try:
        df = pd.DataFrame({
            'League':League,'Date':Date,'Time':Time,
            'HT':HT,'AT':AT,'ODDH':ODDH,'ODDD':ODDD,'ODDA':ODDA,
            'ODD_25+':Y25,'ODD_25-':N25,
            'ODD_BthScore_Yes':YBS,'ODD_BthScore_No':NBS,
            'ODD_1X':X1,'ODD_12':_12,'ODD_X2':X2,
            'Scrape_Date':sDate,'Scrape_Time':sTime
        })
    except:
        df = pd.DataFrame({
            'League':League,'Date':Date,'Time':Time,
            'HT':HT,'AT':AT,'ODDH':ODDH,'ODDD':ODDD,'ODDA':ODDA,
            'ODD_25+':Y25,'ODD_25-':N25,
            'ODD_BthScore_Yes':YBS,'ODD_BthScore_No':NBS,
            'ODD_1X':X1,'ODD_12':_12,'ODD_X2':X2
        })
    
    df = europe_filter(df)
    
    return df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)


def mergeB_year(x):
    if isinstance(x,str):
        x=x.split('-')
        return x[0]
    else:
        return x.year
    
def mergeB_month(x): #não vou usar por causa daquele pequeno erro da falhas das datas no último dia do mês
    x=x.split('-')
    return x[1]
    
def merge_Betano(w): #w é uma lista de dfs
#se encontrarmos o mesmo jogo, escolhemos a odd + baixa (da ODDH)
    df = pd.concat(w,sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    i=0
    while i<len(df):
        same = list(np.where(np.logical_and(
        np.logical_and(df['HT']==df.iloc[i]['HT'],df['AT']==df.iloc[i]['AT']),
        np.logical_and(np.array(list(map(lambda x:mergeB_year(x),df['Date'])))==mergeB_year(df.iloc[i]['Date']),
        df['League']==df.iloc[i]['League'])))[0])
        if len(same)==1:
            i+=1
        else:
            ind=np.argmin([df.iloc[i]['ODDH'] for i in same])
            del same[ind]
            df = df.drop(same,axis=0).reset_index(drop=True)
            #!!!!!!!!!!!!!!!!!!!!!        
            #Se precisar do 25 e do BS, mudar este merge, para tentar ter um q não tenha 'None' nessas odds
            #!!!!!!!!!!!!!!!!!!!!!!
    return df


def Betano_timediff(df,i): #damos a df e o índice e devolve a diferença entre scrape time e game time (+/- em horas)
    scrape_date = dt.datetime.strptime(df.iloc[i]['Scrape_Date'],'%Y-%m-%d')
    scrape_time = df.iloc[i]['Scrape_Time']
    date = dt.datetime.strptime(df.iloc[i]['Date'],'%Y-%m-%d')
    time = df.iloc[i]['Time']
    sh,sm = str(scrape_time)[0:2],str(scrape_time)[2:4]
    h,m = str(time)[0:2],str(time)[2:4]
    dt_ok = date + dt.timedelta(hours=int(h),minutes=int(m))
    dt_scrape = scrape_date + dt.timedelta(hours=int(sh),minutes=int(sm))
    final = dt_ok-dt_scrape
    return ((final.days*86400)+(final.seconds))//3600


def Betano_odd(w,odd='ODDH',x=3): #devolve uma df com o top "x" de Odds do evento "odd"
    df = pd.concat(w,sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
    for n in range(1,x+1):
        vars()[odd+'_TOP'+str(n)]=[]
        vars()['Time_'+str(n)]=[]
    HT=[]
    AT=[]
    Lig=[]
    Dt=[]
    Tm=[]
    i=0
    done_is=[]
    while i<len(df):
        if i in done_is:
            i+=1
            continue
        same = list(np.where(np.logical_and(
        np.logical_and(df['HT']==df.iloc[i]['HT'],df['AT']==df.iloc[i]['AT']),
        np.logical_and(np.array(list(map(lambda x:mergeB_year(x),df['Date'])))==mergeB_year(df.iloc[i]['Date']),
        np.array(list(map(lambda x:mergeB_month(x),df['Date'])))==mergeB_month(df.iloc[i]['Date']))))[0])
        if len(same)==1:
            for n in range(1,x+1):
                if n==1:
                    vars()[odd+'_TOP'+str(n)]+=[df.iloc[i]['ODDH']]
                    vars()['Time_'+str(n)]+=[Betano_timediff(df,i)] #diff em horas do game time e scrape time
                else:
                    vars()[odd+'_TOP'+str(n)]+=['None']
                    vars()['Time_'+str(n)]+=['None']
            HT+=[df.iloc[same[0]]['HT']]
            AT+=[df.iloc[same[0]]['AT']]
            Lig+=[df.iloc[same[0]]['League']]
            Dt+=[df.iloc[same[0]]['Date']]
            Tm+=[df.iloc[same[0]]['Time']]
        else:
            oddsH=[df.iloc[s]['ODDH'] for s in same]
            oddsH_=list(map(lambda x:-x,oddsH))
            sorte=np.argsort(oddsH_) #assim fazemos reverse sort
            i2=1
            while (i2<=x):
                if ((i2-1)<len(sorte)):
                    vars()[odd+'_TOP'+str(i2)]+=[oddsH[sorte[i2-1]]]
                    vars()['Time_'+str(i2)]+=[Betano_timediff(df,same[sorte[i2-1]])]
                else:
                    vars()[odd+'_TOP'+str(i2)]+=['None']
                    vars()['Time_'+str(i2)]+=['None']
                i2+=1
            HT+=[df.iloc[same[0]]['HT']]
            AT+=[df.iloc[same[0]]['AT']]
            Lig+=[df.iloc[same[0]]['League']]
            Dt+=[df.iloc[same[0]]['Date']]
            Tm+=[df.iloc[same[0]]['Time']]
                
            
        done_is+=same
        i+=1
    
    odd_df=pd.DataFrame({'League':Lig,'HT':HT,'AT':AT,'Date':Dt,'Time':Tm})
    for n in range(1,x+1):
        odd_df[odd+'_TOP'+str(n)]=vars()[odd+'_TOP'+str(n)]
        odd_df['Time_'+str(n)]=vars()['Time_'+str(n)]
    
    return odd_df


def get_number(x):
    total = 0
    for i in range(len(x)):
        total += x[i]*(10**(len(x)-i-1))
    return total

            
def save_filterBetano(w):
    oo=os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data')
    if oo!=[]:
        i1 = max(list(map(lambda x:get_number([int(s) for s in x if s.isdigit()]),oo)))
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data//Betano'+str(i1+1)+'.csv',index=False)            
    else:
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data//Betano0.csv',index=False)

def save_rawBetano(w):
    oo0=os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//')
    oo = [i for i in oo0 if ('betano' in i) and ('Pre_betano' not in i)]
    if oo!=[]:
        i1 = max(list(map(lambda x:get_number([int(s) for s in x if s.isdigit()]),oo)))
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//betano'+str(i1+1)+'.csv',index=False)            
    else:
        w.to_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//betano0.csv',index=False)


def Betano_autofilter():
#verifica quais as dfs q estão no filter data, e faz o filter das dfs que ainda não foram filtered
    dir1 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds')
    dfs = [dir1[i] for i in range(len(dir1)) if ('betano' in dir1[i]) and ('Pre' not in dir1[i])]
    dir2 = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data')
    last = len(dir2) 
    dfs = dfs[last:]
    for n in range(len(dfs)):
        dff = pd.read_csv('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//'+str(dfs[n]))
        Df = Betano_filter(dff)
        save_filterBetano(Df)




##########
##########
#Parte do Betano+Sky
##########
##########

def Betano_file_teams(w1,w2,league): #w1 -> df Sky |||| w2 -> df betano
    #Vamos tornar os nomes das equipas iguais nas duas dfs
    try:
        op = open('BetanoTeams_'+league+'.pickle','rb')
        same = pickle.load(op)
        op.close()
    except:
        print('Não leu ficheiro')
        same = [] # lista com os clubes com o mesmo nome [nome Sky,nome betano]
    # vamos manter o nome do Sky
    try:
        sky_teams =  list(set(list(np.unique(list(w1['HomeTeam'])))+list(np.unique(list(w1['AwayTeam'])))))
        betano_teams = list(set(list(np.unique(list(w2['HomeTeam'])))+list(np.unique(list(w2['AwayTeam'])))))
    except:
        sky_teams =  list(set(list(np.unique(list(w1['HT'])))+list(np.unique(list(w1['AT'])))))
        betano_teams = list(set(list(np.unique(list(w2['HT'])))+list(np.unique(list(w2['AT'])))))
    i = 0
    betano_teams_copy = betano_teams.copy()
    sky_teams_copy = sky_teams.copy()
    if same==[]:
        same=[]
        restos=[]
        for ii in range(len(sky_teams)):
            nn=0
            found=False
            while nn<len(betano_teams) and not(found):
                if sky_teams[ii]==betano_teams[nn]:
                    same+=[[sky_teams[ii],betano_teams[nn]]]
                    del betano_teams[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[sky_teams[ii]]

        if restos==[]:
            op = open('BetanoTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            restos_copy=restos.copy()
            betano_teams_copy=betano_teams.copy()
            same_copy=same.copy()
            t=0
            while betano_teams!=[]:
                print('------')
                print(restos)
                ok=input(str(betano_teams[t])+'? (write "passa" if not sure Or "reset" to restart) ')
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    betano_teams=betano_teams_copy
                    restos=restos_copy
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,betano_teams[t]],[betano_teams[t],ok]]
                    del betano_teams[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(betano_teams):
                    t=0
            op = open('BetanoTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
    else:
        same_sky = [same[i][0] for i in range(len(same))]
        same_betano = [same[i][1] for i in range(len(same))]
        missing_sky = [sky_teams[i] for i in range(len(sky_teams)) if (sky_teams[i] not in same_sky)]
        missing_betano = [betano_teams[i] for i in range(len(betano_teams)) if (betano_teams[i] not in same_betano)]
        missing_sky_copy = missing_sky.copy()
        missing_betano_copy = missing_betano.copy()
        same_copy=same.copy()
        
        restos=[]
        for ii in range(len(missing_sky)):
            nn=0
            found=False
            while nn<len(missing_betano) and not(found):
                if missing_sky[ii]==missing_betano[nn]:
                    same+=[[missing_sky[ii],missing_betano[nn]]]
                    del missing_betano[nn]
                    found=True
                nn+=1

            if not found:
                restos+=[missing_sky[ii]]

        if restos==[]:
            op = open('BetanoTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same
        else:
            t=0
            while (restos!=[]) or (missing_betano!=[]):
                if len(restos) != len(missing_betano):
                    print('We got a problemoooo')
                    raise('aa')
                print(restos)
                ok = input(str(missing_betano[t])+'? (write "passa" if not sure Or "reset" to restart) ')
                if ok!='passa' and (ok not in restos) and (ok!='reset'):
                    print('Erro na palavra')
                    continue
                if ok=='passa':
                    t+=1
                    continue
                if ok=='reset':
                    t=0
                    restos=restos_copy.copy()
                    missing_betano=missing_betano_copy.copy()
                    same=same_copy.copy()
                    continue
                else:
                    same+=[[ok,missing_betano[t]],[missing_betano[t],ok]]
                    del missing_betano[t]
                    del restos[np.where(np.array(restos)==ok)[0][0]]
                if t==len(missing_betano):
                    t=0
            op = open('BetanoTeams_'+league+'.pickle','wb')
            pickle.dump(same,op)
            op.close()
            return same

def Betano_utn(sky,betano,league): #update_team_names
# vamos mudar o nome das dfs de betano para o nome das dfs do sky
#assim podemos fazer um merge usando o np.where
    same = Betano_file_teams(sky,betano,league)
    same_sky = [same[i][0] for i in range(len(same))]
    same_betano = [same[i][1] for i in range(len(same))]
    #HOME
    for i in range(len(same_betano)):
        try:
            replaceH=list(np.where(betano['HT']==same_betano[i])[0])
            home='HT'
        except:
            replaceH=list(np.where(betano['HomeTeam']==same_betano[i])[0])
            home='HomeTeam'
        for n in replaceH:
            betano.at[n,home]=same_sky[i]
    #AWAY
    for i in range(len(same_betano)):
        try:
            replaceH=list(np.where(betano['AT']==same_betano[i])[0])
            away='AT'
        except:
            replaceH=list(np.where(betano['AwayTeam']==same_betano[i])[0])
            away='AwayTeam'
        for n in replaceH:
            betano.at[n,away]=same_sky[i]  
    return betano



def Betano_addodds(sky,betano):
    if 'ODDH_Betano' not in list(sky.columns):
        sky['ODDH_Betano']=np.nan
        sky['ODDD_Betano']=np.nan
        sky['ODDA_Betano']=np.nan
    for b in range(len(betano)):
        aa = list(np.where(np.logical_and(np.logical_and(sky['HT']==betano.iloc[b]['HT'],sky['AT']==betano.iloc[b]['AT']),
                                          sky['League']==betano.iloc[b]['League']))[0])
        if aa!=[]:
            if len(aa)>1:
                print('Double Game, Betano_Odds')
                raise Exception('Double Game, Betano_Odds')
            else:
                sky.at[aa[0],'ODDH_Betano']=betano.iloc[b]['ODDH']
                sky.at[aa[0],'ODDD_Betano']=betano.iloc[b]['ODDH']
                sky.at[aa[0],'ODDA_Betano']=betano.iloc[b]['ODDH']
    return sky



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