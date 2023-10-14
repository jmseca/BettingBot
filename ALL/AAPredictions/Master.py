import datetime as dt
import pandas as pd
import numpy as np
import random
import os
import openpyxl
from dateutil import relativedelta as relativedelta

from Bet_Brain import *
from Betano import *
from Portal import *
from Sky_Under import *

#se der erro pode ser por estes dois
from big_dix import *
from Multi_DeForest_Husky_C import *

import Add_HUSKY as H1
import Add_HUSKY6 as H6
import Add_SKY as S1

#FUNÇÕES -|_|_|_|_|_|__|_|_|_|__|_|_|__|_|__|_|_|_|__|_|_|


def Not_Add(na,short=False):
    #print(na[['Date','Time']])
    #Muito Importante!!!!!!!!!
    #Pega no not_add e devolve o not add, mas com as horas do último jogo das duas equipas
    #(Ou seja), diz a que horas podemos fazer scrape para conseguir prever
    season = int(input('Which season?:   '))
    if len(str(season))!=4:
        raise Exception('Season '+str(season)+' não é válida')
        
    leagues = list(np.unique(na['League']))
    League_Pref = {
    'Premier_League':'PL','La_Liga':'LL','Ligue_1':'L','Serie_A':'SA','Bundesliga':'Bund','Eredivisie':'Ered',
        'Premiership':'Scott'
    }
    Not_ADD = []
    for l in leagues:
        na2 = na.loc[na['League']==l]
        file=pd.read_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//ADF//'+str(l)+'//New'+str(League_Pref[l])+str(str(season-1)[2:])+'_'+str(str(season)[2:])+'.xlsx')
        add_d=[]
        add_t=[]
        for i in range(len(na2)):
            same=list(np.where(np.logical_and(na2.iloc[i]['HT']==file['HT'],na2.iloc[i]['AT']==file['AT']))[0])
            if len(same)!=1:
                raise Exception('WTF Error')
                
            
            file2 = file[:(same[0])]
            n=-1
            date1,date2=0,0
            done=False
            doneD1 = True
            doneD2 = True
            while n>=(-len(file2)) and not(done):
                if ((file2.iloc[n]['HT']==na2.iloc[i]['HT']) or (file2.iloc[n]['AT']==na2.iloc[i]['HT'])) and doneD1:
                    doneD1=False
                    date1 = [file2.iloc[n]['Date'],file2.iloc[n]['Time']+300] #passadas 2h o jogo já deve ter acabado
                if ((file2.iloc[n]['AT']==na2.iloc[i]['AT']) or (file2.iloc[n]['HT']==na2.iloc[i]['AT'])) and doneD2:
                    doneD2 = False
                    date2 = [file2.iloc[n]['Date'],file2.iloc[n]['Time']+300] #passadas 2h o jogo já deve ter acabado
                if (date1!=0) and (date2!=0):
                    done = True
                n=n-1
            #print(date1,date2)
            if not(done):
                raise Exception('Game Not Found')
            if date2[0]>date1[0]:
                add_d += [date2[0]]
                add_t += [date2[1]]
            elif date2[0]==date1[0]:
                if date2[1]>=date1[1]:
                    add_d += [date2[0]]
                    add_t += [date2[1]]
                else:
                    add_d += [date1[0]]
                    add_t += [date1[1]]
            else:
                add_d += [date1[0]]
                add_t += [date1[1]]
            
                
        na2['Ready_ScrapeDate']=add_d
        na2['Ready_ScrapeTime']=add_t
        Not_ADD += [na2]
        
    Not_ADD = pd.concat(Not_ADD,sort=False)
    Not_ADD = Not_ADD.sort_values(['Ready_ScrapeDate','Ready_ScrapeTime'],ascending=[True,True]).reset_index(drop=True)
    if short:
         return Not_ADD[['League','Ready_ScrapeDate','Ready_ScrapeTime']]          
    else:
        return Not_ADD


def Predix_League(PreHusky,l,portal_len):
    Bdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data//' 
    if l == 'Ligue_1': #o modelo e os valores limite estão errados
        modelx = 'Husky_DFL1_P2_F2.pickle'
        TL = 70
        FL = 24
        clubs = H1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        print(Predix)
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
    elif l == 'Serie_A':
        modelx = 'Husky6_DFSA1_P2_S_F2.pickle'
        TL = 57
        FL = 46
        clubs = H6.findall_clubs2_new(PreHusky,read=False)
        Husky0 = H6.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
                        
                        
    elif l == 'Premier_League':
        modelx = 'Husky_DFPL1_P2_S_F2.pickle'
        TL = 76
        FL = 41
        clubs = H1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
                        
                        
    elif l == 'Bundesliga':
        modelx = 'Husky_DFBund1_P1_F2.pickle'
        TL = 92
        FL = 7
        clubs = H1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
                        
                        
    elif l == 'La_Liga':
        modelx = 'Husky_DFLL1_P2_S_F2.pickle'
        TL = 95
        FL = 6
        clubs = H1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
                        
                        
    elif l == 'Eredivisie':
        modelx = 'Sky_DFEred1_P2_S_F2.pickle'
        TL = 64
        FL = 16
        clubs = S1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = S1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
                        
                        
    elif l == 'Premiership':
        modelx = 'Sky_DFScott1_P2_S_F2.pickle'
        TL = 56
        FL = 31
        clubs = S1.findall_clubs2_new(PreHusky,read=False)
        Husky0 = S1.join_husky(PreHusky,clubs,5,diff=False)
        Husky = Husky0.tail(portal_len)
        rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
        F=pickle.load(rd0)
        lixo_Train=pickle.load(rd0)
        lixo_Test=pickle.load(rd0)
        T_df=pickle.load(rd0)
        rd0.close()
        #print(Husky.columns)
        big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
        Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
        #return Predix
        Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
        betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
        lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
        Predix=Odds_Top(Predix,Betano_TopOdds)
    else:
        print(l)
        raise Exception('Check League names')
    
    return Predix





time.sleep(0.5)
#------------------------- E que comece o código
check_method = True
print('')
while check_method:
    print('Master(0) ou Bet_check(1) ou Update_Figures(2) ou Bet_Brain(3)?')
    cmok = int(input('------------->  '))
    if cmok in [0,1,2,3]:
        check_method=False

if cmok==0:

    downloads = 'C://Users//joaom//Downloads//'
    desktop = 'C://Users//joaom//Desktop//WScrapy2//Sky//'
    print('')
    print('Which Leagues?')
    print('(all -> All the Leagues || done -> No more Leagues)')
    leag_done=True
    leagues = []
    leagues1=['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A','Eredivisie','Premiership']
    while leag_done:
        if sum([i in leagues1 for i in leagues ])==len(leagues1):
            leag_done=False
        else:
            print(leagues1)
            time.sleep(0.2)
            leagues_aux = input_string_aux(input('--------->'))
            if (leagues_aux in leagues) or ((leagues_aux not in ['all','done']) and (leagues_aux not in leagues1)):
                print('Argument not valid')
            else:
                if leagues_aux=='done':
                    leag_done=False
                elif leagues_aux=='all':
                    leagues = leagues1
                elif leagues_aux in leagues1:
                    leagues += [leagues_aux]
                else:
                    raise Exception('Uknown error')

    print(leagues,'L')
    print('')
    print('Make Predictions?')
    is_predictions = int(input('0(No) / 1(Yes) :  '))
    if is_predictions not in [0,1]:
        raise Exception('Argument not valid')

    print('')
    read_done=True
    while read_done:
        Read = input('Ler novos ficheiros? Sim(1) Não(0) ')
        if Read not in ['0','1']:
            print('Invalid Key')
        else:
            read_done=False
    print('')           
    excel_closed = True
    while excel_closed:
        print('Antes de começar, por favor fechar todos os ficheiros Excel')
        confirm = int(input('Estão fechados? Sim(1) Não(0) '))
        if confirm==1:
            excel_closed=False

    if Read=='1':
        B = list(map(lambda x: 'betano' in x,list(os.listdir(downloads))))
        if sum(B)!=1: #True==1 || False==0
            raise Exception('Erro na extração do Betano, Temos '+str(sum(B))+' ocorrências')
        else:
            Bet_ind=np.where(B)[0][0]
            betano = pd.read_csv(downloads+os.listdir(downloads)[Bet_ind])
        save_rawBetano(betano)
        Betano_autofilter()

        #Portal
        #P = list(map(lambda x: 'oddsportal' in x,list(os.listdir(downloads))))
        #if sum(P)!=1: #True==1 || False==0
        #    raise Exception('Erro na extração do Portal, Temos '+str(sum(P))+' ocorrências')
        #else:
        #    Portal_ind=np.where(P)[0][0]
        #    portal = pd.read_csv(downloads+os.listdir(downloads)[Portal_ind])
        #save_rawPortal(portal)
        #Portal_autofilter()

        #Sky Future Games
        print('Going to skyF')
        SKF1 = list(map(lambda x: ('skygamesf' in x),list(os.listdir(desktop))))
        if sum(SKF1)!=1:
            raise Exception('Erro na extração do Sky, Ocorrências: '+str(sum(SK1))+' (Downloads) || '+str(sum(S2))+' (Desktop)')
        else:
            SkyF_ind=np.where(SKF1)[0][0]
            sky_f = pd.read_csv(desktop+os.listdir(desktop)[SkyF_ind])
        save_rawSkyF(sky_f)
        SkyF_autofilter()
        print('skyF Done1')

        #Under
        U = list(map(lambda x: 'understats' in x,list(os.listdir(downloads))))
        if sum(U)!=1: #True==1 || False==0
            raise Exception('Erro na extração do Under, Temos '+str(sum(U))+' ocorrências')
        else:
            Under_ind=np.where(U)[0][0]
            under = pd.read_csv(downloads+os.listdir(downloads)[Under_ind])
        save_rawUnder(under)
        Under_autofilter()


        #Sky
        SK1 = list(map(lambda x: 'skysports' in x,list(os.listdir(downloads))))
        if sum(SK1)!=1:
            S2 = list(map(lambda x: ('skygames' in x) and ('f' not in x),list(os.listdir(desktop))))
            if sum(S2)!=1:
                raise Exception('Erro na extração do Sky, Ocorrências: '+str(sum(SK1))+' (Downloads) || '+str(sum(S2))+' (Desktop)')
            else:
                Sky_ind=np.where(S2)[0][0]
                sky = pd.read_csv(desktop+os.listdir(desktop)[Sky_ind])
        else:
            Sky_ind=np.where(SK1)[0][0]
            sky = pd.read_csv(downloads+os.listdir(downloads)[Sky_ind])
        save_rawSky(sky)
        Sky_autofilter()
            

    #Filtering the dataaaaaa
    #Betano
    Bdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data//' 
    Bdir2 = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Merged_Data//' 
    b1 = time.perf_counter()
    if Read=='0':
        if 'Master_DF_Betano.csv' in os.listdir(Bdir2):
            betano1 = pd.read_csv(Bdir2 + 'Master_DF_Betano.csv')
        else:
            betano_dfs = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
            betano_dfs = pd.concat(betano_dfs,sort=False)
            betano1 = Merge_Betano(betano_dfs)
            betano1.to_csv(Bdir2+'Master_DF_Betano.csv')
    else:
        betano_dfs = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
        betano_dfs = pd.concat(betano_dfs,sort=False)
        betano1 = Merge_Betano(betano_dfs)
        betano1.to_csv(Bdir2+'Master_DF_Betano.csv')
        
    b2 = time.perf_counter()
    print(f'Betano in {round(b2-b1,2)} seconds')



    #Pdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data//' #dps se calhar também podemos fazer merge
    #portal_dfs = os.listdir(Pdir)
    #print('Portal'+str(max(list(map(lambda x:get_int_str(x),portal_dfs))))+'.csv')
    #portal0 = pd.read_csv(Pdir+'Portal'+str(max(list(map(lambda x:get_int_str(x),portal_dfs))))+'.csv')
    print('SkyF2 upcoming')
    SFdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//SkyF_Info//Filtered_Data//'
    skyf_dfs = os.listdir(SFdir)
    sky_f_0 = pd.read_csv(SFdir+'SkyF'+str(max(list(map(lambda x:get_int_str(x),skyf_dfs))))+'.csv')
    print('SkyF2 done')



    #Sky
    print('Skyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    Sdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data//'  #dps se calhar também podemos fazer merge
    Sdir2 = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Merged_Data//'
    s1 = time.perf_counter()
    if Read=='0':
        if 'Master_DF_Sky.csv' in os.listdir(Sdir2):
            sky1 = pd.read_csv(Sdir2 + 'Master_DF_Sky.csv')
        else:
            sky_dfs = list(map(lambda x:pd.read_csv(Sdir+x),list(os.listdir(Sdir))))
            sky_dfs = pd.concat(sky_dfs,sort=False)
            sky1 = merge_SU(sky_dfs)
            sky1.to_csv(Sdir2+'Master_DF_Sky.csv')
    else:
        sky_dfs = list(map(lambda x:pd.read_csv(Sdir+x),list(os.listdir(Sdir))))
        sky_dfs = pd.concat(sky_dfs,sort=False)
        sky1 = merge_SU(sky_dfs)
        sky1.to_csv(Sdir2+'Master_DF_Sky.csv')
    s2 = time.perf_counter()
    print(f'Sky in {round(s2-s1,2)} seconds')

    #Under
    print('Undeeeeeeeeeeeer')
    Udir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data//'  #dps se calhar também podemos fazer merge
    Udir2 = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Merged_Data//'
    u1 = time.perf_counter()
    if Read=='0':
        if 'Master_DF_Under.csv' in os.listdir(Udir2):
            under1 = pd.read_csv(Udir2 + 'Master_DF_Under.csv')
        else:
            under_dfs = list(map(lambda x:pd.read_csv(Udir+x),list(os.listdir(Udir))))
            under_dfs = pd.concat(under_dfs,sort=False)
            under1 = merge_SU(under_dfs)
            under1.to_csv(Udir2+'Master_DF_Under.csv')
    else:
        under_dfs = list(map(lambda x:pd.read_csv(Udir+x),list(os.listdir(Udir))))
        under_dfs = pd.concat(under_dfs,sort=False)
        under1 = merge_SU(under_dfs)
        under1.to_csv(Udir2+'Master_DF_Under.csv')
    u2 = time.perf_counter()
    print(f'Under in {round(u2-u1,2)} seconds')



    #IT´s TIME !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #leagues=leagues1
    #Fazer depois o código para os Russos!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    not_add = pd.DataFrame({}) #vai ajudar a dizer qnd é q temos de fazer scrape
    All_Predix = pd.DataFrame({})
    for l in leagues:
        #season = int(input('Which season?:   '))
        #if len(str(season))!=4:
        #    raise Exception('Season '+str(season)+' não é válida')
        season = 2021 #alterar isto ao longo dos anos

        if l in ['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A']:
            print('League:  ',l)
            sky2 = Prepare__Df(sky1,season,l)
            under2 = Prepare__Df(under1,season,l)
            #portal2 = Prepare__Df(portal0,season,l)
            skyf2 = Prepare__Df(sky_f_0,season,l)
            betano2 =Prepare__Df(betano1,season,l)
            husky,lixo0 = Merge_Sky_Under(sky2,under2)

            #lixo1,portal3 = Portal_utn(sky2,portal2,l)
            lixo2,betano3 = Betano_utn(sky2,betano2,l)


            #portal_add,final_add,portal_not_add,portal_len = PortalAdd_Sky2(portal3,husky)
            portal_add,final_add,portal_not_add,portal_len = PortalAdd_Sky2(skyf2,husky)

            not_add = pd.concat([not_add,portal_not_add],sort=False)
            husky0 = pd.concat([husky,portal_add],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
            PreHusky= Betano_addodds(husky0,betano3)
            
            PreFile = pd.concat([husky,final_add],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
            File = Betano_addodds(PreFile,betano3)
        elif l in ['Eredivisie','Premiership']:
            print('League:  ',l)
            sky2 = Prepare__Df(sky1,season,l)
            
            #portal2 = Prepare__Df(portal0,season,l)
            skyf2 = Prepare__Df(sky_f_0,season,l)

            betano2 =Prepare__Df(betano1,season,l)            
            #lixo1,portal3 = Portal_utn(sky2,portal2,l)
            lixo2,betano3 = Betano_utn(sky2,betano2,l)

            #portal_add,final_add,portal_not_add,portal_len = PortalAdd_Sky2(portal3,husky)
            portal_add,final_add,portal_not_add,portal_len = PortalAdd_Sky2(skyf2,sky2)

            not_add = pd.concat([not_add,portal_not_add],sort=False)
            sky3 = pd.concat([sky2,portal_add],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
            
            PreHusky= Betano_addodds(sky3,betano3)
            PreFile = pd.concat([sky2,final_add],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
            File = Betano_addodds(PreFile,betano3)
        if is_predictions==1:
            if not(portal_add.empty):
                Predix = Predix_League(PreHusky,l,portal_len)
                #print(Predix)
                All_Predix = pd.concat([All_Predix,Predix],sort=False)
            #if l == 'Ligue_1': #o modelo e os valores limite estão errados
            #    modelx = 'Husky_DFLL1_P2.pickle'
            #    TL = 60
            #    FL = 60
            #    clubs = H1.findall_clubs2_new(PreHusky,read=False)
            #    Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
            #    Husky = Husky0.tail(portal_len)
            #    rd0=open('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//ZModelos//'+modelx,'rb')
            #    F=pickle.load(rd0)
            #    lixo_Train=pickle.load(rd0)
            #    lixo_Test=pickle.load(rd0)
            #    T_df=pickle.load(rd0)
            #    rd0.close()
            #    print(Husky.columns)
            #    big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
            #    Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
            #    Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL)+'%','ForestReal_'+str(FL)+'%','Won/NotWon'],axis=1)
            #    betano_dfs2 = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
            #    Betano_TopOdds = Betano_oddtime(betano_dfs2,odd='ODDH',x=5,sort=True,league=l)
            #    lixo2,Betano_TopOdds = Betano_utn(sky2,Betano_TopOdds,l)
            #    Predix=Odds_Top(Predix,Betano_TopOdds)
            
            
            # os valores dos thresholds dependem de modelo para mkdelo e cuidado q eles estão no drop clumns
        League_Pref = {
        'Premier_League':'PL','La_Liga':'LL','Ligue_1':'L','Serie_A':'SA','Bundesliga':'Bund','Eredivisie':'Ered',
            'Premiership':'Scott'
        }
        File.to_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//ADF//'+str(l)+'//New'+str(League_Pref[l])+str(str(season-1)[2:])+'_'+str(str(season)[2:])+'.xlsx',index=False)



    # FIM
    if is_predictions==1:
        All_Predix = All_Predix.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
        All_Predix.to_excel('All_Predix.xlsx',index=False)
        bb_check=True
        while bb_check:
            print('Quer mudar os parâmetros de Bet_Brain?')
            bbok = int(input('Sim(1) Não(0) '))
            if bbok==0:
                bb_check=False
            elif bbok==1:
                print('Mudar os parâmetros no ficheiro')
                print('E dps escolher a opção 3')
                raise Exception('Changing Bet_Brain')
            else:
                print('Invalid Key')
    
        Bet_Brain()
        
    print(Not_Add(not_add,short=False))

elif cmok==1:
    Bet_check()

elif cmok==2:
    Update_Figures()

elif cmok==3:
    Bet_Brain()

else:
    raise Exception('Erro no cmok')


    