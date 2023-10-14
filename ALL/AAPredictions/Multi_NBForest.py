import pandas as pd
import numpy as np
import random
import concurrent.futures as cf
import time
import os
import datetime as dt
from functools import reduce
executor=cf.ProcessPoolExecutor(max_workers=50) #50 só pq é para mandar ao Pai

print('A df dada ao build_NBForest não pode ter colunas que não vão ser analisadas (exceção da coluna 0/1)')

class NB_Decision_Node:
#branches é uma lista com os vários NB_Decision_Node
    def __init__(self,question,branches): 
        self.question = question
        self.branches = branches
        self.branches_size = len(branches)
        
class NB_Leaf:
    
    def __init__(self,df):
        self.predictions=depend_counts(df) 
        self.probability=proba(df)
        
class NB_Question:
#values é tambem uma lista com valores
    def __init__(self,column,values):
        self.column = column
        self.values = values
        self.values_size = len(values)
        

class NB_Forest:
    def __init__(self):
        self.trees=[]
        
    def add_tree(self,tree):
        (self.trees)+=[tree]
        
    def size(self):
        return len(self.trees)
    
    def get_tree(self,ind):
        return self.trees[ind]
    
    def merge_forests(self,forest):
        (self.trees)+=(forest.trees)
#-----------------------------------------------------------------------------------

def var_values(df,column): #dá nos uma lista dos valores de uma variável 
    #Nota, cada variável está associada a uma coluna
    return np.unique(df[:,column])

def depend_counts(df):
    #devolve um dicionário com os valores da variável dependente e as vezes q aparecem
    #NOTA, esta função assume q a variável depend está na última coluna da df
    coluna=df[:,-1] #que neste caso é np.array
    varz,counts=np.unique(coluna,return_counts=True)
    if len(counts)==2:
        return {0:counts[0],1:counts[1]} #lista com dois elementos
    else:
        if varz[0]==0:
            return {0:counts[0],1:0}
        else:
            return {0:0,1:counts[0]}
        
def proba(df):
    #prob1=time.perf_counter()
    #calcula a probabilidade dos valores de um dicionário (em percentagem, para evitar float errors)
    #É necessário para as Leafs
    ind=len(df)
    dicti=depend_counts(df)
    new={0:round(100*(dicti[0]/ind),1),1:round(100*(dicti[1]/ind),1)}  # este módulo de3 decision trees está feito para var dep de 0/1 APENAS
    #prob2=time.perf_counter()
    #print(f'proba in {round(prob2-prob1,6)} seconds')
    return new


def NB_partition(df,Q):
    parts = []
    for i in range(Q.values_size):
        if i==0:
            t1 = np.where(df[:,Q.column]>Q.values[i]) #vamos querer o oposto disto
            df1 = np.delete(df,t1,0)  #por isso é q aqui fazemos delete, para tirar o conjunto em cima
            #print(df1)
            parts += [df1]
        else:
            #print(Q.values[i-1],'< ||||  <=',Q.values[i])
            t1 = np.where(np.logical_or(df[:,Q.column]<=Q.values[i-1],df[:,Q.column]>Q.values[i]))
            df1 = np.delete(df,t1,0)
            
            parts += [df1]
            
    t1 = np.where(df[:,Q.column]<=Q.values[i])
    df1 = np.delete(df,t1,0)
    #print(df1)
    parts += [df1]
    return parts



def Get_Question(df,c,x): 
#pega na coluna(c) e df e em quantas divisoes da arvore queremos fazer (x)
# e devolve x "ramos", com o mesmo número de elementos
# o c das colunas é números
# a pergunta
    x_size = round(len(df)/x)
    df_aux = df[df[:,c].argsort()]
    Qs=[]
    for i in range(1,x):
        Qs+=[df_aux[i*x_size][c]]
    return NB_Question(c,Qs)

def Get_ColDiv(n):
    #recebe o nº de el de uma coluna e diz quantas divisões vamos fazer
    if n==1:
        return False
    
    elif 2<=n<=8:
        return 2
    
    elif 9<=n<=15:
        return 3
    
    elif 16<=n<=60:
        return 4
    
    elif 61<=n:
        return 5
    
    #elif 101<=n<=250:
    #    return 8
    
    #elif n>=251:
    #    return 10
    
    else:
        print('counts da coluna',n)
        raise Exception('Valor WTF')

def Get_Col(df,colunas,picked): # devolve uma coluna aleatória
    done = False
    limit = max(int(len(colunas)/2),30)
    count = 0
    while not(done):
        if count >= limit:
            if len(picked)>=((np.size(df,1)-1)*0.6): #60% das colunas já escolidas
                return 'RLeaf'
            else:
                print(len(df))
                print('Wow, muitas colunas com apenas 1 valor\nOu a calhar sempre no picked\nSe calhar algo está mal')
                print('picked: ',sorted(picked))
                print('columns: ',np.size(df,1))
        r = random.randrange(len(colunas))
        COL = colunas[r]
        if len(var_values(df,COL))>1 and (COL not in picked): #se =1, não dá para fazer perguntas como é óbvio
            return COL
        count+=1

def Col_Exists(df,COL,spec,limit_down,limit_up): #Devolve instrução
    #Serve para quando estamos num grau da árvore que já foi analisado
    #Logo já tem uma pergunta guardada
    #spec -> indica se a coluna deverá representar uma divisão que dá para:
    #ainda outro branch('Branch') ou uma Leaf ('Leaf')
    if limit_down >= limit_up:
        raise Exception('Trocaste o down com o up') #tirar isto se o prg funcionar
    
    unique = len(var_values(df,COL))
    if spec == 'Leaf':
        if unique==1: 
            return 0,'RLeaf'  #df vai virar Leaf
        n,new_spec = Get_ColDiv_Adv(df,unique,limit_down,limit_up,mode='Leaf') #devolve o nº de divisões a fazer
        return n,new_spec
    
    elif spec == 'Branch':
        if unique==1:
            return 0,'RLeaf' #df vai virar Leaf
        n,new_spec = Get_ColDiv_Adv(df,unique,limit_down,limit_up,mode='Branch') #devolve o nº de divisões a fazer
        return n,new_spec
        
    else:
        print(spec)
        raise Exception('Unknown spec value')

def Get_ColDiv_Adv(df,n,limit_down,limit_up,mode='Branch'): 
    if limit_down >= limit_up:
        raise Exception('Trocaste o down com o up') #tirar isto se o prg funcionar
    #uma versão avançada do Get_ColDiv
    #agr tem em conta os limites que estabelemos
    n = Get_ColDiv(n)
    done = False
    Leafwarning = ''
    #serve para evitar casos onde é impossível uma suposta Leaf calhar no delta(Leaf)
    #oscilando entre valores deamsiado pequenos e grandes
    while not(done):
        df_n = len(df)//n
        
        if mode=='Branch':
            if df_n>limit_up:
                return n,mode
            elif limit_up<=df_n<=limit_up:
                if n==2:
                    #print('içi1')
                    return n,'Leaf'
                else:
                    n-=1
            else:
                if n==2:
                    return n,'RLeaf'
                else:
                    n-=1
        
        elif mode=='Leaf':
            if limit_up<=df_n<=limit_up:
                #print('içi3')
                return n,mode
            elif df_n>limit_up:
                if n==5 or ('ab' in Leafwarning): #se houber 'ab', anda a saltitar entre este elif e o else num ciclo inf 
                    return n,'Branch'
                else:
                    Leafwarning += 'a'
                    n+=1
            else:
                if n==2:
                    return n,'RLeaf'
                else:
                    Leafwarning += 'b'
                    n-=1
        
        elif mode == 'Simple': #quando ainda não temos pergunta para este grau
            if df_n>limit_up:
                return n,'Branch'
            elif limit_down<=df_n<=limit_up:
                #print('içi2',n)
                return n,'Leaf'
            else:
                if n==2:
                    return n,'RLeaf'
                else:
                    n-=1
        else:
            print(mode,'mode')
            raise Exception('Unknown mode value')

def Col_DNE(df,colunas,picked,limit_down,limit_up):
    if limit_down >= limit_up:
        raise Exception('Trocaste o down com o up') #tirar isto se o prg funcionar
    COL = Get_Col(df,colunas,picked)
    if COL == 'RLeaf':
        return 'Lixo1','Lixo2',COL
    unique = len(var_values(df,COL))
    
    n,new_spec = Get_ColDiv_Adv(df,unique,limit_down,limit_up,mode='Simple')
    return COL,n,new_spec


def Column_Pick(df,colunas,col_list,tree_degree,picked,limit_down,limit_up):
    if limit_down >= limit_up:
        raise Exception('Trocaste o down com o up') #tirar isto se o prg funcionar
    if tree_degree+1 <= len(col_list): #coluna existe
        COL = col_list[tree_degree][0]
        spec = col_list[tree_degree][1]
        
        print(Col_Exists(df,COL,spec,limit_down,limit_up))
        n,new_spec = Col_Exists(df,COL,spec,limit_down,limit_up)

        if new_spec=='RLeaf':
            return 'Lixo',new_spec,col_list
        else:
            return Get_Question(df,COL,n),new_spec,col_list
    else: #coluna não existe
        COL,n,spec=Col_DNE(df,colunas,picked,limit_down,limit_up)
        if spec=='RLeaf':
            return 'Lixo',spec,col_list
        else:
            picked += [COL]
            col_list+=[[COL,spec]]
            return Get_Question(df,COL,n),spec,col_list


def build_NBTree(df,colunas,col_list,tree_degree,picked,limit_down,limit_up,spec):
    print(len(df))
    if spec=='Leaf':
        #print('Leaf',len(df))
        return NB_Leaf(df),picked 
    
    Q,spec,col_list = Column_Pick(df,colunas,col_list,tree_degree,picked,limit_down,limit_up)
    
    if spec=='RLeaf':
        #print('RLeaf',len(df))
        return NB_Leaf(df),picked
    
    tree_degree+=1
    branches = NB_partition(df,Q)
    Branches = []
    Pickz = []
    #print('tree_degree',tree_degree)
    for i in range(len(branches)):
        if len(branches[i])!=0:
            ok,picked1 = build_NBTree(branches[i],colunas,col_list,tree_degree,picked,limit_down,limit_up,spec)
        Branches += [ok]
        Pickz += [picked]
        PICK = Pickz[np.argmax(list(map(lambda x:len(x),Pickz)))]
    return NB_Decision_Node(Q,Branches),PICK



#Funções para diminuir o número de valores das colunas-------------------------------------------------------
def adjust_column_values(df2,mini=5,maxi=9,perguntas=2):
    #ajusta os valores de cada coluna se for para fazer um modelo 
    #usando os dois tipos de pergunta (perguntas=2)
    #mini, maxi são o min e máx possíveis do número de valores de uma coluna
    #comparando com o número de registos (linhas)
    df=np.round(df2,1)
    if perguntas==2:
        Max=round((len(df)*maxi)/100)
        Min=round((len(df)*mini)/100)
        print('Max len: ',Max)
        print('Min len: ',Min)
        tens=[]
        acv_coefs=[]
        for i in range(len(df[0])): #df é uma np.array
            acv_coef='None'
            c_val,ten=check_float(df[:,i])
            unique=np.unique(c_val)
            if len(unique)>Max:
                new,acv_coef=aux_acv(c_val,Max,Min)
                df[:,i]=new
            tens+=[ten]
            acv_coefs+=[acv_coef]
        t_df = pd.DataFrame({'Check_Float':tens,'ACV_Coef':acv_coefs})
        return df,t_df
    elif perguntas==1:
        return df,'None'
    else:
        print('Só existem perguntas 1/2')
        raise('Erro')

def aux_acv(c_val,Max,Min,div=10,st_div=10,last='max'): 
    #div é o número que usamos para a divisão inteira
    #last é se no último passo divemos de reduzir ou aumentar (decidi começar em max só pq sim)
    #st_div são os passos que vamos dando para encontrar o div certo
    div = round(div,1) #caso contrário temos aqueles números que nunca mais acabam
    new_val2=np.array(list(map(lambda x:x//div,c_val)))
    new_val=np.unique(new_val2)
    #print(div,'diiiiiiiiiiiiiiiiiv')
    #print('len: ',len(new_val))
    if len(new_val)>Max:
        if last=='max':
            return aux_acv(c_val,Max,Min,div=div+st_div,st_div=st_div,last='max')
        else:
            return aux_acv(c_val,Max,Min,div=div+st_div,st_div=max(0.1,st_div//2),last='max')
    elif len(new_val)<=Min:
        if last=='min':
            return aux_acv(c_val,Max,Min,div=max(1,div-(max(0.1,st_div//2))),st_div=st_div,last='min')
        else:
            return aux_acv(c_val,Max,Min,div=max(1,div-(max(0.1,st_div//4))),st_div=max(0.1,st_div//2),last='min')
    else:
        return new_val2,div
    
def check_float(c_val,ten=0):
    #serve para tornar colunas com valores decimais em valores inteiros
    tf_val=np.array(list(map(lambda x:(x).is_integer(),c_val)))
    if ten==200:
        print(c_val)
    if all(tf_val):
        return c_val,ten
    else:
        ten+=1
        n_val=np.array(list(map(lambda x:x*10,c_val)))
        return check_float(n_val,ten)



def T(test,T_df): #aplica as transformações do T_df no test
    try:					#Esta parte só está aqui pq é igual ao do Multi_DeForest
        if T_df=='None':    #Assim não temos problemas de importação
            return test		#Com duas T_df diferentes
    except:
        print('Cagou no None')
        for i in range(len(T_df)):
            if T_df.iloc[i]['Check_Float']!=0:
                test[:,i]=np.array(list(map(lambda x:x*(10*(T_df.iloc[i]['Check_Float'])),test[:,i]))) #check_float
            if T_df.iloc[i]['ACV_Coef']!='None':
                test[:,i]=np.array(list(map(lambda x:x//(T_df.iloc[i]['ACV_Coef']),test[:,i]))) #acv
        return test   
#------------------------- Acabaram as Funções para diminuir o número de valores das colunas ----------

def build_NBForest(df,trees,Picked=[],Min=6,Max=8):
    F = NB_Forest()
    the_df=df.values
    the_df,T_df=adjust_column_values(the_df,mini=Min,maxi=Max,perguntas=2)
    Picked=[]
    for t in range(trees):
        t,piky = build_NBTree(df,list(range(len(df_tit.columns)-1)),[],0,[],10,25,None) 
        #10-limit_down/25->limit_up, podemos alterar
        if piky not in Picked: #não queremos árvores iguais
            Picked += [piky]
            F.add_tree(t)
    return F,T_df
