import datetime as dt
import pandas as pd
import numpy as np
import random
import os
import openpyxl

from Betano import *
from Portal import *
from Sky_Under import *
import Add_HUSKY as H1
#------------------------- E que comece o código
#Get the dfs

#Betano
downloads = 'C://Users//joaom//Downloads//'
desktop = 'C://Users//joaom//Desktop//WScrapy2//Sky//'

print('Make Predictions?')
is_predictions = int(input('0(No) / 1(Yes) :  '))
if is_predictions not in [0,1]:
	raise Exception('Argument not valid')

B = list(map(lambda x: 'betano' in x,list(os.listdir(downloads))))
if sum(B)!=1: #True==1 || False==0
    raise Exception('Erro na extração do Betano, Temos '+str(sum(B))+' ocorrências')
else:
    Bet_ind=np.where(B)[0][0]
    betano = pd.read_csv(downloads+os.listdir(Bet_ind))

#Portal
P = list(map(lambda x: 'oddsportal' in x,list(os.listdir(downloads))))
if sum(P)!=1: #True==1 || False==0
    raise Exception('Erro na extração do Portal, Temos '+str(sum(P))+' ocorrências')
else:
    Portal_ind=np.where(P)[0][0]
    portal = pd.read_csv(downloads+os.listdir(Portal_ind))


#Under
U = list(map(lambda x: 'understats' in x,list(os.listdir(downloads))))
if sum(U)!=1: #True==1 || False==0
    raise Exception('Erro na extração do Under, Temos '+str(sum(U))+' ocorrências')
else:
    Under_ind=np.where(U)[0][0]
    under = pd.read_csv(downloads+os.listdir(Under_ind))


#Sky
S1 = list(map(lambda x: 'skysports' in x,list(os.listdir(downloads))))
if sum(S1)!=1:
	S2 = list(map(lambda x: 'skygames' in x,list(os.listdir(desktop))))
	if sum(S2)!=1:
        raise Exception('Erro na extração do Sky, Ocorrências: '+str(sum(S1))+' (Downloads) || '+str(sum(S2))+' (Desktop)')
    else:
    	Sky_ind=np.where(S2)[0][0]
        sky = pd.read_csv(desktop+os.listdir(Sky_ind))
else:
	Sky_ind=np.where(S1)[0][0]
    sky = pd.read_csv(downloads+os.listdir(Sky_ind))


#Filtering the dataaaaaa
#Betano
Bdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//BetanoOdds//Filtered_Data//' 
save_rawBetano(betano)
betano0 = Betano_filter(betano)
save_filterBetano(betano0)
betano_dfs = list(map(lambda x:pd.read_csv(Bdir+x),list(os.listdir(Bdir))))
betano1 = merge_Betano(betano_dfs)


#Portal
Pdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Portal_Info//Filtered_Data//' #dps se calhar também podemos fazer merge
save_rawPortal(portal)
portal0 = portal_drop(portal)
save_filterPortal(portal0)


#Sky
Sdir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Sky_Info//Filtered_Data//'  #dps se calhar também podemos fazer merge
save_rawSky(sky)
try:
	sky0=Sky_Download_drop(sky)
except:
	sky0=Sky_Desktop_drop(sky)
save_filterSky(sky0)
sky_dfs = list(map(lambda x:pd.read_csv(Sdir+x),list(os.listdir(Sdir))))
sky1 = merge_SU(sky_dfs)


#Under
Udir = 'C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//Under_Info//Filtered_Data//'  #dps se calhar também podemos fazer merge
save_rawUnder(under)
under0 = Under_Download_drop(under)
save_filterUnder(under0)
under_dfs = list(map(lambda x:pd.read_csv(Udir+x),list(os.listdir(Udir))))
under1 = merge_SU(under_dfs)



#IT´s TIME !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
leagues=['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A']
#Fazer depois o código para os Russos!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

not_add = pd.DataFrame({}) #vai ajudar a dizer qnd é q temos de fazer scrape
for l in leagues:
	season = int(input('Which season?:   '))
	if len(str(season))!=4:
		raise Exception('Season '+str(season)+' não é válida')

	sky2 = Prepare__Df(sky1,season,l)
	under2 = Prepare__Df(under1,season,l)
	portal2 = Prepare__Df(portal0,season,l)
	betano2 =Prepare__Df(betano1,season,l)

	husky = Merge_Sky_Under(sky2,under2)

	portal3 = Portal_utn(sky2,portal2,l)
	betano3 = Betano_utn(sky2,betano2,l)


	portal_add,portal_not_add,portal_len = PortalAdd_Sky(portal3)

	not_add = pd.concat([not_add,portal_not_add],sort=False)

	husky0 = pd.concat([husky,portal_add],sort=False).sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)

	if husky0.tail(portal_len) != portal_add:
		raise Exception('Portal_Add está mal na Liga: '+str(l)) 

	husky1 = Betano_addodds(husky0,betano3)

	old_husky = get_old_df(l,season)

	PreHusky = OldNew_Merge(old_husky,husky1)

	if is_predictions==1:

		All_Predix = pd.DataFrame({})

		if l == 'Ligue_1': #o modelo e os valores limite estão errados
            modelx = 'Husky4_DFPL1_P1.pickle'
            TL = 60
            FL = 60
            clubs = H1.findall_clubs2_new(PreHusky,read=False)
            Husky0 = H1.join_husky(PreHusky,clubs,5,diff=False)
	    
        Husky = Husky0.tail(portal_len)
		rd0=open(modelx,'rb')
		F=pickle.load(rd0)
		lixo_Train=pickle.load(rd0)
		lixo_Test=pickle.load(rd0)
		T_df=pickle.load(rd0)
		rd0.close()
		big__ = Big_dix(Husky,F,T_df,var=1,tree_list=[TL],forest_list=[FL],optimize=False)
		Predix = go_get(big__,mode=2,lista=['Tree_Forest','TL'+str(TL),'FL'+str(FL),'Predicted'])
		Predix = Predix.drop(['Index','Tree Score %','Tree_var%'+str(TL),'ForestPredix_'+str(FL),'ForestReal_'+str(FL),'Won/NotWon'],axis=1)
		# os valores dos thresholds dependem de modelo para mkdelo e cuidado q eles estão no drop clumns
		All_Predix = pd.concat([All_Predix,Predix],sort=False)
    League_Pref = {
    'Premier_League':'PL','La_Liga':'LL','Ligue_1':'L','Serie_A':'SA','Bundesliga':'Bund'
    }
	PreHusky.to_excel('C://Users//joaom//Documents//Projetos//PYTHON//Apostas//AAPredictions//ADF//New'+str(League_Pref[l])+str(str(season-1)[2:])+'_'+str(str(season)[2:])+'.xlsx'




# FIM
if is_predictions==1:
	All_Predix = All_Predix.sort_values(['Date','Time'],ascending=[True,True]).reset_index(drop=True)
	All_Predix.to_excel('All_Predix.xlsx')
