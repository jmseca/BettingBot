import pandas as pd 
import numpy as np 
import time 
import datetime as dt 
import pickle
from dateutil import relativedelta as relativedelta
import os

def remove_Nan_odd(df):
    out=[]
    #print(df)
    for i in range(len(df)):
        if pd.isnull(df.iloc[i]['ODDH_Last1']):
            out += [i]
    print('out',out)
    df = df.reset_index(drop=True)
    #df = df.drop(out,axis=0)
    return df.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)

def rec_or(W,df,column): #Faz or recursivamente de valores de uma coluna de uma df
    if len(W)>2:
        return np.logical_or(df[column]==W[0],rec_or(W[1:],df,column))
    elif len(W)==2:
        return np.logical_or(df[column]==W[0],df[column]==W[1])
    elif len(W)==1:
        return np.array(np.where(df[column]==W[0])[0])
    else:
        raise('a')
    
def rec_and(W,df,column): #Faz and recursivamente de valores de uma coluna de uma df
    if len(W)>2:
        return np.logical_and(df[column]==W[0],rec_and(W[1:],df,column))
    elif len(W)==2:
        return np.logical_and(df[column]==W[0],df[column]==W[1])
    elif len(W)==1:
        return np.array(np.where(df[column]==W[0])[0])
    else:
        raise('a')
    
def rec_nand(W,df,column): #Faz and recursivamente de valores de uma coluna de uma df
    if len(W)>2:
        return np.logical_and(df[column]!=W[0],rec_nand(W[1:],df,column))
    elif len(W)==2:
        return np.logical_and(df[column]!=W[0],df[column]!=W[1])
    elif len(W)==1:
        return np.array(np.where(df[column]!=W[0])[0])
    else:
        raise('a')
    
def rec_nor(W,df,column): #Faz or recursivamente de valores de uma coluna de uma df
    if len(W)>2:
        return np.logical_or(df[column]==W[0],rec_nor(W[1:],df,column))
    elif len(W)==2:
        return np.logical_or(df[column]!=W[0],df[column]!=W[1])
    elif len(W)==1:
        return np.array(np.where(df[column]!=W[0])[0])
    else:
        raise('a')


def get_figures():
    #vai buscar as infos sobre o dinheiro
    done = False
    while not(done):
        print('Get, Create, Ignore Figures?')
        time.sleep(0.2)
        ok = input('------------>')
        if (ok=='Get') or (ok=='Create') or (ok=='Ignore'):
            done = True
        else:
            print('Invalid Key')
    if ok=='Get':
        #try:
        r = os.listdir('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//')
        DF = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF.xlsx')
        return DF
    elif ok=='Create':
        done = False
        while not(done):
            print('First amount of money?')
            time.sleep(0.2)
            ok = input('----------> ')
            try: 
                ok2 = int(ok)
                done = True
            except:
                print('Invalid Key')
        DF = pd.DataFrame({
            'Money':[ok2],'Money9_15':[5000],'Money3':[300000],'Money1_Simple':[40000],'Money3_SO':[2500],
            'Money1_SOSimple':[1500],'Creation_Date':[dt.datetime.now()]
        })
        
        
        with pd.ExcelWriter("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF.xlsx") as writer:
            DF.to_excel(writer, index=None)
            #writer.save()
            writer.close()
        with pd.ExcelWriter("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF_BU.xlsx") as writer2:
            DF.to_excel(writer2, index=None)
            #writer2.save()
            writer2.close()
                
        return DF
    elif ok == 'Ignore':
        return False
    
    else:
        raise Exception('Weird Error')



def series_to_df(bets): #nas bets vamos ter várias series, mas dá mais jeito se estiver tudo em DF
    for i in range(len(bets)):
        for n in range(len(bets[i])):
            if type(bets[i][n])==pd.core.series.Series:
                bets[i][n] = pd.DataFrame(bets[i][n]).T
            elif pd.core.frame.DataFrame!=type(bets[i][n]):
                print(i,n)
                raise Exception('Invalid Data Type')
    return bets

#(Max=2,Days=1,No_Bets=['La_Liga'],No_Multi=['La_Liga'],Day_Limit=20,perc=0.05,Limit_15=False)
def Bet_Brain(Max=2,Days=1,No_Bets=['La_Liga','Ligue_1','Eredivisie'],No_Multi=['La_Liga'],Day_Limit=20,perc=0.05,Limit_15=False):
# vai organizar as apostas todas segundo o modelo escolhido
# atualiza valor apostado de maneira a ir ao encontro com os limites (deste caso da Betano)
# E avisa se estamos a chegar perto dos limites
# Guarda registos de todas as apostas e na semana a seguir atualiza o balanço (ganho/perdido)
#No_Multi -> ligas que não devemos incluir nas apostas múltiplas (pq falham várias vezes, mas têm odds altas)
#Limit_15 -> Se for True não aceita apostas com odds <= 1.5
#Day_Limit -> Limite do saldo que se pode apostar por dia (%)
#No_Bets são as ligas que não queremos usar para apostas
    #try:
    print(Day_Limit,'aaaaaa')
    print(Days,'bbbbbbb')
    df = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//All_Predix.xlsx')
    if df.iloc[0]['Date']<(dt.datetime.now()-dt.timedelta(2)):
        raise Exception ('Is file updated?')
    #except:
    #    raise Exception('No file All_Predix')
    df = df.loc[rec_nand(No_Bets,df,'League')]
    #retira os jogos que não têm odd (ou seja q não dá para apostar)
    df = remove_Nan_odd(df)

    Fig_DF = get_figures()
    try:
        if Fig_DF != False:
            pass
    except:
        Figures_Warning(Fig_DF)
    print(perc)
    Perc=perc
    bets=[]
    d=0
    while d<len(df):
        DdD = [] # tem as apostas todas de um "Days"
        if Days==0:
            same_games = df.loc[np.array(list(np.where(np.logical_and(df.iloc[d]['Date']==df['Date'],(abs(df.iloc[d]['Time']-df['Time'])<3000)))[0]))] 
        else:
            same_games = df.loc[np.array(list(map(lambda x:x.days,list(abs(df.iloc[d]['Date']-df['Date'])))))<Days]
        if len(same_games)==1:
            DdD += [same_games.loc[:][['League','Date','Time','HT','AT','ODDH_Last1']]]
            bets += [DdD]
            d+=1
        else:
            try:
                DM = same_games.loc[rec_nand(No_Multi,same_games,'League')] #jogos q podem ter múltiplas
                DNM = same_games.loc[rec_or(No_Multi,same_games,'League')] #jogos q não podem ter múltiplas
            except:
                DM = same_games.iloc[rec_nand(No_Multi,same_games,'League')] #jogos q podem ter múltiplas
                DNM = same_games.iloc[rec_or(No_Multi,same_games,'League')] #jogos q não podem ter múltiplas
            real_size = len(same_games)
            size = len(DM)
            size_aux = len(DM)
            for i in range(len(DNM)):
                DdD += [DNM.iloc[i][['League','Date','Time','HT','AT','ODDH_Last1']]]
            if DM.empty:
                bets += [DdD]
                d+=real_size
            else:
                if size<=Max:
                    DdD += [DM.loc[:][['League','Date','Time','HT','AT','ODDH_Last1']]]
                    bets += [DdD]
                    d+=real_size
                else:
                    helper = 0
                    while size_aux>Max:
                        #print(helper,':',(Max+helper))
                        DM2 = DM[helper:(Max+helper)]
                        DdD += [DM2.loc[:][['League','Date','Time','HT','AT','ODDH_Last1']]]
                        helper += Max
                        size_aux = size_aux - Max
                    #print(helper)
                    DM2 = DM[helper:]
                    DdD += [DM2.loc[:][['League','Date','Time','HT','AT','ODDH_Last1']]]
                    bets += [DdD]
                    d+=real_size
    #return bets #só para ver dps apagar
    bets = series_to_df(bets)
    #return bets
    EX = Excel_Organizer(bets,Day_Limit,Perc,Limit_15)
    if EX!=[]:
        with pd.ExcelWriter("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets.xlsx") as writer:
            j=0
            for n, df in enumerate(EX):
                if not(df.empty):
                    df.to_excel(writer, sheet_name='Apostas_'+str(j), index=None)
                    j+=1
            writer.save()
    else:
        print('THERE ARE NO PRECTIONS :(')


def Excel_Organizer(bezz2,Day_Limit,Perc,Limit_15): 
    #prepara os jogos para as apostas em Excel
    lmit = Day_Limit
    mz = 100 #não é bem o money, mas assim dá o bet_money em % do Money Total
    maman1=[]
    for i in range(len(bezz2)):
        maman2 = pd.DataFrame({})
        
        if Limit_15:
            oz_list = [round(np.prod(list(fdf['ODDH_Last1'])),2) for fdf in bezz2[i] if round(np.prod(list(fdf['ODDH_Last1'])),2)>1.5]
            size = len(oz_list)
        else:
            size = len(bezz2[i])
            
        mmm = money_game(size,perc=Perc)
        if mmm>lmit:
            mmm = lmit
        print(Perc)
        print(mmm,'1')
        mmm = round(((mmm*mz)/100),2)
        print(mmm,'2')
        for n in range(len(bezz2[i])):
            fdf = bezz2[i][n]
            oz = round(np.prod(list(fdf['ODDH_Last1'])),2)
            if (oz>1.5) or not(Limit_15):
                ok = pd.DataFrame({
                'League':[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],'Date':['Bet_Money','DATE',np.nan,np.nan,np.nan,np.nan],
                    'Time':[round(mmm/size,2),max(fdf['Date']),np.nan,np.nan,np.nan,np.nan],
                'HT':[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],'AT':['Bet_ODD:',np.nan,np.nan,np.nan,np.nan,np.nan],
                    'ODDH_Last1':[oz,np.nan,np.nan,np.nan,np.nan,np.nan],
                    'Won/NotWon':[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                'SO':[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]})
                ok2 = pd.concat([fdf,ok],sort=False)
                maman2 = pd.concat([maman2,ok2]).reset_index(drop=True)
        if not(maman2.empty):
        	maman1+=[maman2]
    return maman1




def money_game(g,perc=0.1): 
#diz quanto (em %) de dinheiro gastamos se apostarmos g apostas sabendo que usamos aquela regra para apostas no mesmo dia
    m = 100
    mo= 100
    for _ in range(g):
        m10 = round(m*perc,2)
        m = m-m10
    return round(100*((mo-m)/mo),2)


def Bet_check():
    #Dps de realizarmos as apostas de um dia, ou já de vários dias
    #Fazemos Bet_check para corrigir as Odds da aposta,montante apostado,ou se a aposta foi mesmo realizada
    #Esta função é para correr (supostamente) dps de efetuar as apostas
    #Não é para verificar se a aposta foi ganha ou não
    done = True
    d=0
    lix = []
    while done:
        try:
            vars()['df'+str(d)] = pd.read_excel("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets.xlsx",d)
            lix += [vars()['df'+str(d)]]
            d+=1
        except:
            done=False #acontece quando já não há folhas no ficheiro Excel
    lix2=[]
    if lix[0].empty:
    	print('There are no Bets')
    	print('Check to see if it is True')
    	df.to_excel("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets2.xlsx",index=False)
    	raise Exception('TheBets is empty')
    for df in lix:
        d=0
        beg=0
        while d<len(df):
            print(d,beg,pd.isnull(df.iloc[d]['League']))
            if d>=1:
                if beg==0 and not(pd.isnull(df.iloc[d]['League'])) and pd.isnull(df.iloc[d-1]['League']):
                    beg = d
            if df.iloc[d]['Date']=='DATE':
                try:
                    multi=len(df[beg:(d+1)])
                except:
                    multi=len(df[beg:])
                print(beg,'beg',df.iloc[beg]['HT'])
                print(' ')
                print(' ')
                if multi>3:
                    print('Aposta Múltipla')
                else:
                    print('Aposta Simples')
                i=beg
                while i<=(d-2):
                    print(df.iloc[i]['HT'],' VS ',df.iloc[i]['AT'],'|| ODD: ',df.iloc[i]['ODDH_Last1'])
                    i+=1
                print('ODD_TOTAL: ',df.iloc[i]['ODDH_Last1'])
                done1=True
                time.sleep(0.3)
                while done1:
                    try:
                        ok1 = int(input('Aposta realizada? Sim(1) Não(0)'))
                        if (ok1==1) or (ok1==0):
                            done1=False
                        else:
                            print('Invalid Key')
                    except:
                        print('Invalid Key')
                        brk = input('Break? Sim(1) Não(0)')
                        if brk=='1':
                            raise Exception('Brooooooooke')
                        
                if ok1==1:
                    done2 = True
                    while done2:
                        try:
                            ok2 = float(input('Atualização da ODD ---> '))
                            print(ok2,type(ok2))
                            time.sleep(0.2)
                            check2 = int(input('Tem a certeza? Sim(1) Não(0)'))
                            if check2==1:
                                done2=False
                        except:
                            print('Invalid Key')
                    df.at[(d-1),'ODDH_Last1']=ok2
                    
                    done4 = True
                    while done4:
                        ok4 = input('Tem jogo SODDS? Sim(1) Não(0) ')
                        if ok4=='0':
                            df.at[d,'SO']=0
                            done4=False
                        elif ok4=='1':
                            df.at[d,'SO']=1
                            done4=False
                        else:
                            print('Invalid Key')
                    
                    
                    done3 = True
                    while done3:
                        print(df.iloc[d-1]['Date'],'  ',df.iloc[d-1]['Time'])
                        time.sleep(0.2)
                        try:
                            ok3 = int(input('Percentagem da aposta foi respeitada? Sim(1) Não(0)'))
                            if ok3==1 or ok3==0:
                                done3=False
                            else:
                                print('Invalid Key')
                        except:
                            print('Invalid Key')
                    if ok3==0:
                        done31 =True
                        while done31:
                            try:
                                ok31=float(input('Qual foi a percentagem da aposta?'))
                                print(ok31,type(ok31))
                                time.sleep(0.2)
                                check31 = int(input('Tem a certeza? Sim(1) Não(0)'))
                                if check31==1:
                                    done31=False
                            except:
                                print('Invalid Key')
                        df.at[(d-1),'Time']=ok31
                    lix2 += [df] #!!!!!!!!!!!!!!!!!!!
                else:
                    df.at[(d-1),'ODDH_Last1']=np.nan
                    print(df.iloc[(d-1)]['ODDH_Last1'])
                    df.at[(d-1),'ODDH_Last1']=0
                d+=1
                beg=0
                
            else:
                d+=1
        #lix2 += [df]
    with pd.ExcelWriter("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets2.xlsx") as writer:
        j=0
        for n, df in enumerate(lix2):
            if not(df.empty):
                df.to_excel(writer, sheet_name='Apostas_'+str(j), index=None)
                j+=1
        writer.save()



def Update_Figures():
    Fig_DF = get_figures()
    try:
        if Fig_DF == False:
            raise Exception('Ignore is not allowed')
    except:
        pass
    lix = []
    done=True
    d=0
    while done:
        try:
            vars()['df'+str(d)] = pd.read_excel("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets2.xlsx",d)
            lix += [vars()['df'+str(d)]]
            d+=1
        except:
            done=False #acontece quando já não há folhas no ficheiro Excel
    if lix[0].empty:
        print('There are no Bets Finished')
        print('Check to see if this is True')
        #df.to_excel("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets2.xlsx",index=False)
        raise Exception('TheBets2 is empty')
    lix3 = [] #para o TheBets2
    lix2 = [] #para analisar
    for df in lix:
        dAtE,i = max([[df.iloc[i]['Date'],i] for i in range(len(df)) if dt.datetime==type(df.iloc[i]['Date'])])
        tImE = df.iloc[i]['Time']
        print(dAtE,tImE)
        if len(str(tImE))==4:
            h,m=int(str(tImE)[:2]),int(str(tImE)[2:])
        elif len(str(tImE))==3:
            h,m=int(str(tImE)[:1]),int(str(tImE)[1:])
        elif len(str(tImE))==2:
            h,m=0,int(tImE)
        else:
            print(tImE)
            raise Exception('WTF time data')
            
        dAtE = dAtE + dt.timedelta(hours=h+2,minutes=m) #+3 pq assim sabemos que o jogo já acabou
        print(dAtE)
        #print(df)
        if dAtE >= dt.datetime.now():
            lix3 += [df]
        else:
            lix2 += [df]
    Money = Fig_DF.iloc[-1]['Money']
    Money2 = Fig_DF.iloc[-1]['Money']
    fig_list=[]
    print(len(lix2),'lix2')
    for df in lix2:
        #print(len(lix2))
        print('A')
        print('A')
        print('A')
        print('A')
        print('A')
        fig_list2 = [0,0,0,0,0,0,0]
        d=0
        beg=0
        while d<len(df):
            print(d,beg,pd.isnull(df.iloc[d]['League']))
            if d>=1:
                if beg==0 and not(pd.isnull(df.iloc[d]['League'])) and pd.isnull(df.iloc[d-1]['League']):
                    beg = d
            if df.iloc[d]['Date']=='DATE':
                try:
                    multi=len(df[beg:(d+1)])
                except:
                    multi=len(df[beg:])
                print(beg,'beg',df.iloc[beg]['HT'])
                print(' ')
                print(' ')
                if multi>3:
                    Multi = True
                else:
                    Multi = False
                SO = 1==df.iloc[d]['SO'] #se há jogo com SuperODDS
                
                #podemos depois tentar substituir esta parte para ser automático
                i=beg
                perc = df.iloc[d-1]['Time'] #%de money para a aposta
                odd = df.iloc[d-1]['ODDH_Last1'] #odd da aposta
                if odd==0:
                    beg=0
                    d+=1
                else:
                    while i<=(d-2):
                        print(df.iloc[i]['HT'],' VS ',df.iloc[i]['AT'],'|| ODD: ',df.iloc[d-1]['ODDH_Last1'])
                        i+=1
                    done=True
                    while done:
                        try:
                            okok = int(input('Aposta Ganha? Sim(1) Não(0) '))
                            if okok==1 or okok==0:
                                done = False
                            else:
                                print('Invalid Key')
                        except:
                            print('Invalid Key')
                ###############################################################################
                   
                    bet_money = round((perc*Money)/100,2)
                    print(Money)
                    #Validar o bet_money
                    bm = True
                    while bm:
                        print(bet_money,' foi o €€ apostado? Sim(1) Não(0)')
                        bm2 = eval(input('-----> ')) 
                        if bm2 not in [0,1]:
                            print('Invalid Key')
                        else:
                            if bm2 == 1:
                                bm = False
                            else:
                                while bm:
                                    print('Então quanto €€ foi?')
                                    moz = eval(input('----> '))
                                    print('Tem a certeza?,',moz,type(moz))
                                    moz2 = eval(input('Sim(1) Não(0) '))
                                    if moz2 not in [0,1]:
                                        print('Invalid Key')
                                    else:
                                        if moz2 == 1:
                                            bet_money = moz
                                            bm = False
                    #--------------------------------------------------
                    Money2 = Money2 - bet_money
                    if okok==1: #Aposta ganha
                        gain = round(bet_money * odd,2)
                        Money2 = Money2 + gain
                    #fig_list2[0]=Money
                    fig_list2[1] += bet_money if (odd<=1.5) else 0
                    fig_list2[2] += bet_money
                    fig_list2[3] += bet_money if not(Multi) else 0
                    fig_list2[4] += bet_money if SO else 0
                    fig_list2[5] += bet_money if (SO and not(Multi)) else 0

                    beg=0
                    d+=1
            else:
                d+=1
        dAtE2,i2 = max([[df.iloc[i]['Date'],i] for i in range(len(df)) if dt.datetime==type(df.iloc[i]['Date'])])
        tImE = df.iloc[i2]['Time']
        if len(str(tImE))==4:
            h2,m2=int(str(tImE)[:2]),int(str(tImE)[2:])
        elif len(str(tImE))==3:
            h2,m2=int(str(tImE)[:1]),int(str(tImE)[1:])
        elif len(str(tImE))==2:
            h2,m2=0,int(tImE)
        else:
            print(tImE)
            raise Exception('WTF time data')
            
        dAtE2 = dAtE2 + dt.timedelta(hours=h2,minutes=m2) #+3 pq assim sabemos que o jogo já acabou        
        fig_list2[0] = Money2
        fig_list2[6] = dAtE2
        fig_list += [fig_list2]
        
    print(fig_list)
    raise
    for lis in fig_list:
        frame = pd.DataFrame({
            'Money':[lis[0]],'Money9_15':[lis[1]],'Money3':[lis[2]],'Money1_Simple':[lis[3]],'Money3_SO':[lis[4]],
            'Money1_SOSimple':[lis[5]],'Creation_Date':[lis[6]]
        })
        Fig_DF = pd.concat([Fig_DF,frame],sort=False)
    os.remove('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF_BU.xlsx')
    os.rename('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF.xlsx',
    'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF_BU.xlsx')
    print(type(Fig_DF))
    time.sleep(1)
    Fig_DF=Fig_DF.sort_values(['Creation_Date'],ascending=[True]).reset_index(drop=True)
    print(Fig_DF['Creation_Date'])
    Fig_DF.to_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Figures_Storage//Fig_DF.xlsx',index=False)
    
    
    
    try:
        with pd.ExcelWriter("C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//TheBets2.xlsx") as writer:
            j=0
            for n, df in enumerate(lix3):
                if not(df.empty):
                    df.to_excel(writer, sheet_name='Apostas_'+str(j), index=None)
                    j+=1
            writer.save()
        writer.close()
    except:
        pass


def Figures_Warning(fdf): #trata das Fig_DF
    date = dt.datetime.now()
    
    #get rid off monthly (1) limits
    aaa = np.array(list(map(lambda x,y:abs(relativedelta.relativedelta(x,y)).months,[date]*len(fdf),list(fdf['Creation_Date']))))
    m1 = list(np.where(aaa>=1)[0])
    M1_C = [c for c in list(fdf.columns) if 'Money1' in c]
    for i in m1:
        if i==0:
            continue
        for c in M1_C:
            fdf.at[i,c]=0
            
    #get rid off monthly (3) limits
    m3 = list(np.where(aaa>=3)[0])
    M3_C = [c for c in list(fdf.columns) if 'Money3' in c]
    for i in m3:
        if i==0:
            continue
        for c in M3_C:
            fdf.at[i,c]=0
            
    #get rid off monthly (9) limits
    m9 = list(np.where(aaa>=9)[0])
    M9_C = [c for c in list(fdf.columns) if 'Money9' in c]
    for i in m9:
        if i==0:
            continue
        for c in M9_C:
            fdf.at[i,c]=0
            
    Col = [c for c in list(fdf.columns) if ('Money' in c) and (len(c)>5)]
    for c in Col:
        c_sum=sum(list(fdf[1:][c]))
        print(round(fdf.iloc[0][c]-c_sum,2),'€  to limit: ',c)
        if round(fdf.iloc[0][c]-c_sum,2)<=round(fdf.iloc[0]['Money']*0.4,2):
            print(str(c),'ATENÇÃO AOS LIMITEEEEES!!!!!!!!!!')
        print('')
        
        