# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 17:23:19 2020

@author: joaom
"""

#Big_Dixxxxxxx
import numpy as np
import time
import datetime as dt
import pandas as pd
import pickle

print('big_dix tem funções para analisar os modelos')

class big_dix:
     
    def __init__(self,**kwargs):
        dix={}
        for k,w in kwargs.items():
            dix[str(k)]=w
        self.size=len(dix)
        self.dix=dix
        
    def add_keys(self,**kwargs):
        for k,w in kwargs.items():
            self.dix[k]=w
            
    def add_keys_2(self,w1,w2):
        #w1 é uma lista com as keys e w2 uma lista com os valores correspondentes
        assert len(w1)==len(w2)
        for i in range(len(w1)):
            self.dix[w1[i]]=w2[i]
            
    def remove_keys(self,*args):
        for a in args:
            try:
                del self.dix[a]
            except:
                pass
            
    def keys(self):
        return list(self.dix.keys())
            
def go_get(dixx,count=0,mode=1,lista=None):
    if mode==1:
        if count==0:
            print(type(dixx))
        print(dixx.keys())
        new=input("Choose One of The Above: ")
        if new not in dixx.keys():
            print('ERRO na palavra!!!')
            return go_get(dixx,count,mode=1)
        dixx=dixx.dix[new]
        if type(dixx)==big_dix:
            count+=1
            return go_get(dixx,count,mode=1)
        else:
            return dixx
    else:
        while lista!=[]:
            dixx=dixx.dix[lista[0]]
            lista=lista[1:]
        return dixx



def money(df,money,modem='Home'):
    for i in range(len(df)):
        bet_money=0.1*money
        money-=bet_money
        if df.iloc[i]['Won/NotWon']==1:
            if modem=='Home':
                add = bet_money * df.iloc[i]['ODDH_Aver.']
                money+=add
            elif modem=='Away':
                add = bet_money * df.iloc[i]['ODDA_Aver.']
                money+=add
            elif modem=='Draw':
                add = bet_money * df.iloc[i]['ODDD_Aver.']
                money+=add
            else:
                raise('aaaa')
    return money


def get_return_money(repos,top=5,modem='Home'):
    moneyz=100
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    profit=[]
    for i in range(len(method)):
        tree,foret = method[i].split('_')
        listaz = ['Tree_Forest',tree,foret,'Predicted']
        df = go_get(repos,mode=2,lista=listaz)
        cash = round((100*(money(df,moneyz,modem=modem)/moneyz))-100,2)
        profit+=[[tree+'_'+foret,cash]]
    topz=[]
    for t in range(top):
        only_cash = np.array([profit[i][1] for i in range(len(profit))])
        ind_max=np.argmax(only_cash)
        topz+=[[profit[ind_max][0],profit[ind_max][1]]]
        del profit[ind_max]
    return topz



def weekly_profit(repos,w=4,odd=1): #w é o número de semanas 
    old_df = go_get(repos,mode=2,lista=['Tree_Forest','TL50','FL50','ALL']).sort_values(['Date'],ascending=['True']).reset_index(drop=True)
    date0 = old_df.iloc[0]['Date']
    date=date0
    date_ = old_df.iloc[-1]['Date']
    n = 1
    BIG = pd.DataFrame({})
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    method_cash = [100]*len(method)
    count=0
    end=False
    while not(end):
        if count==1:
            pre_date = date
            pos_date = date_
            end = True
        else:
            pre_date = date + (dt.timedelta(weeks=(w*(n-1))))
            pos_date = date + (dt.timedelta(weeks=(w*n)))
        if pos_date>=date_:
            count=1
        ok2 = pd.DataFrame({})
        for i in range(len(method)):
            tree,foret = method[i].split('_')
            listaz = ['Tree_Forest',tree,foret,'Predicted']
            df = go_get(repos,mode=2,lista=listaz)
            df = df.loc[df['ODDH_Aver.']>odd]
            if count==0:
                df = df.loc[np.logical_and(df['Date']<pos_date,df['Date']>=pre_date)]
            elif (count==1) or (end):
                df = df.loc[np.logical_and(df['Date']<=pos_date,df['Date']>=pre_date)]
            cash = round(money(df,method_cash[i],modem='Home'),2)
            if n==1 and not(end):
                ok1 = pd.DataFrame({'Method':[tree+'_'+foret],'Week '+str(w*n):[round(cash/method_cash[i],2)]})
            elif n>1 and not(end):
                ok1 = pd.DataFrame({'Week '+str(w*n):[round(cash/method_cash[i],2)]})
            else: 
                ok1 = pd.DataFrame({'Total':[round(cash/method_cash[i],2)]})
            ok2 = pd.concat([ok2,ok1],sort=False,axis=0)
            method_cash[i]=cash
        BIG = pd.concat([BIG,ok2],sort=False,axis=1)
        n+=1
    return BIG.reset_index(drop=True)


def model_std(repos,odd=1): #devolve a maior sequência d 0s e 1s, e a std de 0s e 1s
    STD = pd.DataFrame({})
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    for i in range(len(method)):
        if i%1000==0:
            print(method[i],'model_std')
        tree,foret = method[i].split('_')
        listaz = ['Tree_Forest',tree,foret,'Predicted']
        df = go_get(repos,mode=2,lista=listaz)
        df = df.loc[df['ODDH_Aver.']>odd]
        wnw = list(df['Won/NotWon'])
        lista_1 = []
        lista_0 = []
        current = 0
        ODDS=[]
        for n in range(len(wnw)):
            ODDS+=[df.iloc[n]['ODDH_Aver.']]
            if n==0:
                if wnw[n]==0:
                    lista_0+=[1]
                    current=0
                else:
                    lista_1+=[1]
                    current=1
            else:
                if current==0:
                    if wnw[n]==0:
                        lista_0[-1]+=1
                    else:
                        current=1
                        lista_1+=[1]
                elif current==1:
                    if wnw[n]==0:
                        current=0
                        lista_0+=[1]
                    else:
                        lista_1[-1]+=1
        if len(ODDS)>0:
            ODD_12 = round((sum(np.array(ODDS)>1.2)/len(ODDS))*100,2) #Percentagem de ODDS >= 1.2
            ODD_15 = round((sum(np.array(ODDS)>1.5)/len(ODDS))*100,2) #Percentagem de ODDS >= 1.5
            ODD_2 = round((sum(np.array(ODDS)>2)/len(ODDS))*100,2) #Percentagem de ODDS >= 2
        else:
            ODD_12 = 0
            ODD_15 = 0
            ODD_2 = 0
        
        
        Games_Lost = sum(lista_0)
        Max0 = max(lista_0)
        Max1 = max(lista_1)
        aver0 = np.mean(lista_0)
        aver1 = np.mean(lista_1)
        std0 = round(sum(list(map(lambda x:abs(x),list(map(lambda x:x-aver0,lista_0))))))
        std1 = round(sum(list(map(lambda x:abs(x),list(map(lambda x:x-aver1,lista_1))))))
        ok1 = pd.DataFrame({'Method2':[tree+'_'+foret],'Size':[len(wnw)],'Games_Lost(0)':[Games_Lost],'Max0':[Max0],'Max1':[Max1],
                            'Aver_0':[round(aver0,1)],'Aver_1':[round(aver1,1)],
                            #'Count_0':[len(lista_0)],'Count_1':[len(lista_1)],
                           'STD_0':[std0],'STD_1':[std1],'ODD_12':[ODD_12],'ODD_15':[ODD_15],'ODD_2':[ODD_2]})
        STD = pd.concat([STD,ok1],axis=0,sort=False)
    return STD

def money_boss(repos,odd=1):
#diz quanto gastamos em apostas com Odd inferior a 1.5
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    u15_cash = [0]*len(method)
    method_cash = [100]*len(method)
    for i in range(len(method)):
        tree,foret = method[i].split('_')
        listaz = ['Tree_Forest',tree,foret,'Predicted']
        df = go_get(repos,mode=2,lista=listaz)
        df = df.loc[df['ODDH_Aver.']>odd]
        wnw = list(df['Won/NotWon'])
        for n in range(len(df)):
            bet_money = 0.1*method_cash[i]
            method_cash[i]-=bet_money
            if df.iloc[n]['ODDH_Aver.']>=1.5:
                u15_cash[i]+=bet_money
            if df.iloc[n]['Won/NotWon']==1:
                add = bet_money * df.iloc[n]['ODDH_Aver.']
                method_cash[i]+=add
    ok1 = pd.DataFrame({'Method':method,'Money_U15':list(map(lambda x:round(x/100,2),u15_cash))})
    return ok1


def Analyse_Model(repos,w=4,odd=1):
    ODD = odd
    df1 = weekly_profit(repos,w=w,odd=ODD).reset_index(drop=True)
    df2 = model_std(repos,odd=ODD).reset_index(drop=True)
    df3 = money_boss(repos,odd=ODD)
    DF = pd.concat([df1,df2,df3],axis=1,sort=False)
    return DF.sort_values(['Total'],ascending=[False]).reset_index(drop=True)


#A próxima secção "Top", serve para analisar os melhores modelos, dependendo das odds
#decidi criar novas funções para as antigas não ficarem com demasiados parâmetros confusos


def weekly_Top(repos,AM_df,top=20,w=4,odd=1): #w é o número de semanas 
    Mthd = list(AM_df.iloc[:top]['Method'])
    old_df = go_get(repos,mode=2,lista=['Tree_Forest','TL50','FL50','ALL']).sort_values(['Date'],ascending=['True']).reset_index(drop=True)
    date0 = old_df.iloc[0]['Date']
    date=date0
    date_ = old_df.iloc[-1]['Date']
    n = 1
    BIG = pd.DataFrame({})
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    method_cash = [100]*len(method)
    count=0
    end=False
    while not(end):
        if count==1:
            pre_date = date
            pos_date = date_
            end = True
        else:
            pre_date = date + (dt.timedelta(weeks=(w*(n-1))))
            pos_date = date + (dt.timedelta(weeks=(w*n)))
        if pos_date>=date_:
            count=1
        ok2 = pd.DataFrame({})
        for i in range(len(method)):
            if method[i] not in Mthd:
                continue
            tree,foret = method[i].split('_')
            listaz = ['Tree_Forest',tree,foret,'Predicted']
            df = go_get(repos,mode=2,lista=listaz)
            df = df.loc[df['ODDH_Aver.']>odd]
            if count==0:
                df = df.loc[np.logical_and(df['Date']<pos_date,df['Date']>=pre_date)]
            elif (count==1) or (end):
                df = df.loc[np.logical_and(df['Date']<=pos_date,df['Date']>=pre_date)]
            cash = round(money(df,method_cash[i],modem='Home'),2)
            if n==1 and not(end):
                ok1 = pd.DataFrame({'Method':[tree+'_'+foret],'Week '+str(w*n):[round(cash/method_cash[i],2)]})
            elif n>1 and not(end):
                ok1 = pd.DataFrame({'Week '+str(w*n):[round(cash/method_cash[i],2)]})
            else: 
                ok1 = pd.DataFrame({'Total':[round(cash/method_cash[i],2)]})
            ok2 = pd.concat([ok2,ok1],sort=False,axis=0)
            method_cash[i]=cash
        BIG = pd.concat([BIG,ok2],sort=False,axis=1)
        n+=1
    return BIG.reset_index(drop=True)


def model_Top(repos,AM_df,top=20,odd=1): #devolve a maior sequência d 0s e 1s, e a std de 0s e 1s
    Mthd = list(AM_df.iloc[:top]['Method'])
    STD = pd.DataFrame({})
    DF = go_get(repos,mode=2,lista=['OverAll'])
    method = list(DF['Method'])
    for i in range(len(method)):
        if method[i] not in Mthd:
            continue
        tree,foret = method[i].split('_')
        listaz = ['Tree_Forest',tree,foret,'Predicted']
        df = go_get(repos,mode=2,lista=listaz)
        df = df.loc[df['ODDH_Aver.']>odd]
        wnw = list(df['Won/NotWon'])
        lista_1 = [0]
        lista_0 = [0]
        current = 0
        for n in range(len(wnw)):
            if n==0:
                if wnw[n]==0:
                    lista_0[-1]+=1
                    current=0
                else:
                    lista_1[-1]+=1
                    current=1
            else:
                if current==0:
                    if wnw[n]==0:
                        lista_0[-1]+=1
                    else:
                        current=1
                        lista_1+=[1]
                elif current==1:
                    if wnw[n]==0:
                        current=0
                        lista_0+=[1]
                    else:
                        lista_1[-1]+=1
        
        Max0 = max(lista_0)
        Max1 = max(lista_1)
        aver0 = np.mean(lista_0)
        aver1 = np.mean(lista_1)
        std0 = round(sum(list(map(lambda x:abs(x),list(map(lambda x:x-aver0,lista_0))))))
        std1 = round(sum(list(map(lambda x:abs(x),list(map(lambda x:x-aver1,lista_1))))))
        ok1 = pd.DataFrame({'Method2':[tree+'_'+foret],'Max0':[Max0],'Max1':[Max1],
                            'Aver_0':[round(aver0,1)],'Aver_1':[round(aver1,1)],
                            #'Count_0':[len(lista_0)],'Count_1':[len(lista_1)],
                           'STD_0':[std0],'STD_1':[std1]})
        STD = pd.concat([STD,ok1],axis=0,sort=False)
    return STD


def Analyse_Top(repos,AM_df,top=20,w=4): 
    #analisa mais a fundo o TOP "top" de modelos com melhor prestação no Analyse_Models
    AT = big_dix()
    li=[]
    print('Currently analysing odds: [1.2,1.5,2]')
    print('Change code to add more odds')
    for O in [1.2,1.5,2]:
        df1 = weekly_Top(repos,AM_df,top=top,odd=O,w=w).reset_index(drop=True)
        df2 = model_Top(repos,AM_df,top=top,odd=O).reset_index(drop=True)
        DF = pd.concat([df1,df2],axis=1,sort=False).sort_values(['Total'],ascending=[False]).reset_index(drop=True)
        li+=[DF]
    AT.add_keys_2(['ODD_12','ODD_15','ODD_2'],li)
    return AT
       

#Cenas para enocntrar o Test2 (pq na época 2020 usei um Test1 mas dps houve mais jogos q vou usar para o Test2)
def days_diff(x,y): #absoluto do número de dias de diferença entre duas datas
    if isinstance(x,str):
        if '-' in x:
            x=dt.datetime.strptime(x,'%Y-%m-%d')
        else:
            print(x)
            raise Exception('Weird Date string')
    if isinstance(y,str):
        if '-' in y:
            y=dt.datetime.strptime(y,'%Y-%m-%d')
        else:
            print(y)
            raise Exception('Weird Date string')
    diff = abs((x-y).days)
    return diff


def Give_Test2(league,model): #dá aquela df nova para testar os modelos
    if league not in ['PL','L','LL','Bund','SA']:
        raise Exception('League must be in [PL, L, LL, Bund, SA]')
    try:
        if model==1:
            DF = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Husky_'+str(league)+'.xlsx')
        else:
            DF = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Husky'+str(model)+'_'+str(league)+'.xlsx')
    except:
        raise Exception('Husky'+str(model)+'_'+str(league), 'não existe no dir das Apostas')
    
    try:
        if model==1:
            Test1 = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Husky'+str(league)+'_Test.xlsx')
        else:
            Test1 = pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//Husky'+str(model)+str(league)+'_Test.xlsx')
    except:
        raise Exception('Husky'+str(model)+str(league)+'_Test.xlsx', 'não existe no dir das Apostas')
        
    same = np.where(np.logical_and(np.logical_and(Test1.iloc[-1]['HT']==DF['HT'],Test1.iloc[-1]['AT']==DF['AT']),
                                  np.array(list(map(lambda x,y:days_diff(x,y),list(DF['Date']),[Test1.iloc[-1]['Date']]*len(list(DF['Date'])))))<=10))
    same = same[0][0]
    return DF[same+1:].reset_index(drop=True).sort_values(['Date','Time'],ascending=[True,True]) 



def Aux_All1(AM_df,count=0,columns=None,all=1):
    #Dá os modelos que só deram profit nas "Week"
    if count==0:
        C=list(AM_df.columns)
        C = [x for x in C if 'Week' in x]
        return AM_df.loc[Aux_All1(AM_df,count=1,columns=C)].sort_values(['Total'],ascending=[False]).reset_index(drop=True)
    else:
        if len(columns)==1:
            return AM_df[columns[0]]>=all
        elif len(columns)==2:
            return np.logical_and(AM_df[columns[0]]>=all,AM_df[columns[1]]>=all)
        else:
            p1 = columns[int(len(columns)/2):]
            p2 = columns[:int(len(columns)/2)]
            return np.logical_and(Aux_All1(AM_df,count=1,columns=p1),Aux_All1(AM_df,count=1,columns=p2))



def bet_multiple(df,Max=3,Days=0,Prints=False,Multiple_Only=False,Perc=0.1):
#esta função só serve para calcular o profit de uma estratégia com apostas múltiplas
#Uma estratégia q dá bastante jeito para fugir ao controlo de apostas da Betano
#Difere do bet_with_time, pq podemos fazer apostas múltiplas com vários jogos (não só apenas 2)
#Max -> Número máximo de jogos por aposta múltipla
#Days -> intervalo de dias que os jogos das apostas múltiplas podem ter sabendo que:
# Days=0 (jogos apenas no mesmo dia com a regra das 3h) // Days=1 (jogos no mesmo dia) // e assim por diante
# Prints -> faz print das apostas múltiplas
# Multiple_Only -> Só fazemos apostas múltiplas, nada de apostas simples 
# COm Multiple_Only dps não vamos poder ver quanto dinheiro iríamos gastar em apostas simples/combinadas
    money = 100
    perc = Perc
    d=0 
    while d<len(df):
        if Days==0:
            same_games = df.loc[np.logical_and(df.iloc[d]['Date']==df['Date'],(abs(df.iloc[d]['Time']-df['Time'])<3000))] 
        else:
            same_games = df.loc[np.array(list(map(lambda x:x.days,list(abs(df.iloc[d]['Date']-df['Date'])))))<Days]
        if len(same_games)==1:
            if Multiple_Only: #assim só regista apostas múltiplas
                d+=1
                continue
            oddz = df.iloc[d]['ODDH_Aver.']
            bet_money = round(money*perc,2)
            money = money - bet_money
            if df.iloc[d]['Won/NotWon']==1:
                money = money + (bet_money*oddz)
            d+=1
        else:
            size = len(same_games)
            size_aux = len(same_games) #vai dar jeito
            if size<=Max:
                oddz = round(np.prod(list(same_games['ODDH_Aver.'])),2)
                bet_money = round(money*perc,2)
                money = money - bet_money
                if Prints:
                    print('-----------------------------------')
                    for i in range(len(same_games)):
                        print(same_games.iloc[i]['HT'],'Vs',same_games.iloc[i]['AT'],'  ODD: ',same_games.iloc[i]['ODDH_Aver.'])
                    if all(list(same_games['Won/NotWon'])):
                        print('Final Odd: ',round(np.prod(list(same_games['ODDH_Aver.'])),2),' Won!!!!!!!!!!!! :D')
                    else:
                        print('Final Odd: ',round(np.prod(list(same_games['ODDH_Aver.'])),2),' Lost :(')
                    print('-----------------------------------')
                if all(list(same_games['Won/NotWon'])):
                    money = money + (bet_money*oddz)
                d+=size
            else:
                helper = 0
                while size_aux>Max:
                    oddz = round(np.prod(list(same_games[helper:(Max+helper)]['ODDH_Aver.'])),2)
                    bet_money = round(money*perc,2)
                    money = money - bet_money
                    if Prints:
                        print('-----------------------------------')
                        for i in range(len(same_games[helper:(Max+helper)])):
                            print(same_games[helper:(Max+helper)].iloc[i]['HT'],'Vs',same_games[helper:(Max+helper)].iloc[i]['AT'],'  ODD: ',same_games[helper:(Max+helper)].iloc[i]['ODDH_Aver.'])
                        if all(list(same_games[helper:(Max+helper)]['Won/NotWon'])):
                            print('Final Odd: ',round(np.prod(list(same_games[helper:(Max+helper)]['ODDH_Aver.'])),2),' Won!!!!!!!!!!!! :D')
                        else:
                            print('Final Odd: ',round(np.prod(list(same_games[helper:(Max+helper)]['ODDH_Aver.'])),2),' Lost :(')
                        print('-----------------------------------')
                    if all(list(same_games[helper:(Max+helper)]['Won/NotWon'])):
                        money = money + (bet_money*oddz)
                    helper += Max
                    size_aux = size_aux - Max
                oddz = round(np.prod(list(same_games[helper:]['ODDH_Aver.'])),2)
                bet_money = round(money*perc,2)
                money = money - bet_money
                if Prints:
                    print('-----------------------------------')
                    for i in range(len(same_games[helper:])):
                        print(same_games[helper:].iloc[i]['HT'],'Vs',same_games[helper:].iloc[i]['AT'],'  ODD: ',same_games[helper:].iloc[i]['ODDH_Aver.'])
                    if all(list(same_games[helper:]['Won/NotWon'])):
                        print('Final Odd: ',round(np.prod(list(same_games[helper:]['ODDH_Aver.'])),2),' Won!!!!!!!!!!!! :D')
                    else:
                        print('Final Odd: ',round(np.prod(list(same_games[helper:]['ODDH_Aver.'])),2),' Lost :(')
                    print('-----------------------------------')
                if all(list(same_games[helper:]['Won/NotWon'])):
                    money = money + (bet_money*oddz)
                d+=size
    return round(money/100,2)



