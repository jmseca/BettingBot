# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 12:33:04 2020

@author: joaom
"""

import pandas as pd
import numpy as np
import random
import concurrent.futures as cf
import time
import os
from functools import reduce
executor=cf.ProcessPoolExecutor(max_workers=15)

print('Este módulo usa pandas.Dataframe')
print('E está feito para apenas prever variáveis categóricas 0/1')
print(' ')
print('No DeForest, escolhemos as colunas a analisar por árvore')
print('Ao contrário do Random_Forest, onde fazíamos random')


def var_values(df,column): #dá nos uma lista dos valores de uma variável 
    #Nota, cada variável está associada a uma coluna
    return np.unique(df[:,column])

def is_numeric(x): #diz se x é número ou não
    return (isinstance(x,int)) or (isinstance(x,float)) or (isinstance(x,np.int64)) or (isinstance(x,np.float64))

#NOTAAA: Parece q os números do pandas estão em numpy.int64  ou numpy.float64


def string_column(df,column):
    #True se coluna constituída por strings
    q=var_values(df,column)
    l=len(q)
    i=0
    found=False
    while i<l and not(found):
        if not(isinstance(q[i],str)):
            found=True
        i+=1
    return not(found)
    

def is_categorical(df,column): 
    #diz se uma coluna numérica é categórica (sim/não, 0/1) (True)
    #ou se é variável contínua (False)
    if not(string_column(df,column)):
        return len(var_values(df,column))==2
    else:
        print('Esta coluna é de str, não mede esta função')
        return 'Esta coluna é de str, não mede esta função'
    
    
       
def not_categorical_values(arr,column):
    #arr=df.values
    #ncv1=time.perf_counter()
    #dá as médias dos valores adjacentes para fazer as perguntas
    v1=np.unique(np.round(arr[:,column],4)) #np.unique já põe os valores por ordem
    values=[]
    for i in range(len(v1)-1):
        values+=[round(((v1[i]+v1[i+1])/2),4)]
    #ncv2=time.perf_counter()
    #print(f'not_categorical_values in {round(ncv2-ncv1,6)} seconds')
    return values  
 
    
    
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
    #[0] número de vezes do 0
    #[1] número de vezes do 1

class Question:
    
    def __init__(self,column,value1,value2=None,tipo=0):
        self.column=column
        self.value1=value1
        self.value2=value2
        self.tipo=tipo
        
    def match(self,example):
        #verifica se o example dá True ou False à pergunta
        #example é uma linha/amostra em pd.DataFrame
        val=example.iloc[0][self.column] #como é uma linha, queremos 0
        if is_numeric(val):
            if self.tipo==0:
                return val >= self.value1
            else:
                return self.value1<= val <= self.value2
        else:
            return val==self.value1
#as perguntas tipo 1 podem dar muitoooooooo jeito
        

def partition(df2,Q): 
    if Q.tipo==0:
        #timeP=time.perf_counter()
        t1=np.where(df2[:,Q.column]>=Q.value1)
        false=np.delete(df2,t1,0)
        f1=np.where(df2[:,Q.column]<Q.value1)
        true=np.delete(df2,f1,0)
        
        #timeP2=time.perf_counter()
        #print(f'Fast Partition in {round(timeP2-timeP,6)} seconds')
        return true,false
    elif Q.tipo==1:
        t1=np.where(np.logical_and(Q.value2>=df2[:,Q.column],df2[:,Q.column]>=Q.value1))
        false=np.delete(df2,t1,0)
        f1=np.where(np.logical_or(Q.value2<df2[:,Q.column],df2[:,Q.column]<Q.value1))
        true=np.delete(df2,f1,0)
        return true,false

    else:
        print('erro na partition')
        raise('Erro')


def gini(df):
    impurity=1
    counts=depend_counts(df)
    for depend in counts:
        impurity-=((counts[depend]/len(df))**2)
    return impurity

def info_gain(true,false,current_impurity):
    #info1=time.perf_counter()
    #true/false são as df q resultam de fazer uma pergunta (definida previamente)
    #current_impurity é o gini da df sem ser dividida por uma pergunta
    p=(len(true)/(len(true)+len(false)))
    info_gain=current_impurity - ((p*gini(true))+((1-p)*gini(false)))
    #print('GAIN',info_gain,'len(true)',len(true),'len(false)',len(false))
    #info2=time.perf_counter()
    #print(f'info_gain in {round(info2-info1,6)} seconds')
    return info_gain



# # #  # # # #  # # Função auxiliar das perguntas tipo 1 (oh shit here we go again) ####
def ohshit_aux(df,column):
    #dá o mínimo do tamanho dos intervalos que podemos fazer com as perguntas tipo1
    #antes o modelo fazia muitas vezes perguntas a um só valor de uma variável,
    #o que é muito mau para a relação bias/variance
    #(acho eu) se depois os resultados não forem benéficos é só voltar ao normal
    val=len(var_values(df,column))
    #diff=[3] #não interessa a quantidade de valores de uma variável, vou definir que o mínimo no máximo é 3
    diff=(2+(val//8)) #vou definir a regra em grupos de 7
    return diff

##  #  #  #  #  #   # #  #  # #  #  # #  # # #  # # ##     #    #  # #  # # #  # # # #



def best_column_question(df,column,perguntas=1): #de uma coluna devolve a melhor pergunta e o seu info_gain
    #print('Starting best_column_question')
    #startquestion=time.perf_counter()
    current_impurity=gini(df)
    best_gain=0
    best_question=None
    
    if string_column(df,column):
        #print('gone to string')
        values = var_values(df,column)
        for val in values:
            q=Question(column,val)
            t,f =partition(df,q)
            #se a pergunta não divide os dados fazemos SKIP
            if len(t) == 0 or len(f) == 0:
                continue
            gain = info_gain(t,f,current_impurity)
            if gain >= best_gain:
                best_gain, best_question = gain, q
    else:
        if is_categorical(df,column):
            #print('gone to categorical')
            values = var_values(df,column) 
            assert len(values)==2
            value = (values[0]+values[1])/2
            q=Question(column,value,tipo=0)
            t,f =partition(df,q)
            gain = info_gain(t,f,current_impurity)
            if gain >= best_gain:
                best_gain, best_question = gain, q
        else:
            #print('oh shit, here we go again, best_question')
            values=not_categorical_values(df,column)
            #print('values size: ',len(values))
            #print(values,'oh shit values')
            for i in range(perguntas): #Faz ciclo dos tipos de perguntas (1 ou 2)
                if i==0: #para perguntas tipo 0
                    for val in values:
                        q=Question(column,val,tipo=0)
                        t,f =partition(df,q)
                        #se a pergunta não divide os dados fazemos SKIP
                        if len(t) == 0 or len(f) == 0:
                            continue
                        gain = info_gain(t,f,current_impurity)
                        if gain >= best_gain:
                            best_gain, best_question = gain, q
                            
                else: #para perguntas tipo 1
                    if len(values)<=4: #demasiado pequeno
                        pass
                    else:
                        mini=ohshit_aux(df,column)
                        #print('len_colum',len(values)+2)# se não me engano var_values=values+2 (em termos de size)
                        #print(mini,'-----MA MINIIIIII-----')
                        for i1 in range(len(values)-mini): #se i1 for para lá de values[-2], não rende (ver caderno)
                            for i2 in range(i1+mini,len(values)): #isto do mini é novo, cuidado com erros
                                #print('i1',i1,'i2',i2,mini<=(i2-i1),'Just checking')
                                q=Question(column,values[i1],values[i2],tipo=1)
                                t,f =partition(df,q)
                                #se a pergunta não divide os dados fazemos SKIP
                                if len(t) == 0 or len(f) == 0:
                                    continue
                                gain = info_gain(t,f,current_impurity)
                                if gain >= best_gain:
                                    best_gain, best_question = gain, q
    #print(best_question.value1,best_question.value2,best_question.tipo,'Da coluna:',df.columns[best_question.column],'Com gain:',best_gain)
    #finishquestion=time.perf_counter()
    #asas=len(var_values(df,column))
    #if asas>=60:
    #    print(f'Best_column_question in {round(finishquestion-startquestion,6)} seconds','| column: ',column,'len: ',asas)
    #print('Ending best_column_question')
    return best_question,best_gain

# #  #  Função que faz o MultiProcessing das várias perguntas das várias col #

def multi_columns(df,ind,perguntas=2):
    #time_mc1=time.perf_counter()
    #ind é a lista com as colunas 
    gq=list(executor.map(best_column_question,[df]*len(ind),ind,[perguntas]*len(ind)))
    #gq é uma lista de listas com perguntas e gains
    gq_gain=[gq[i][1] for i in range(len(gq))]
    max_gain=max(gq_gain)
    ab=0
    done=False
    while ab<len(gq) and not done:
        if gq[ab][1]==max_gain:
            done=True
        else:
            ab+=1
    #print('Ending multi_columns')
    #time_mc2=time.perf_counter()
    #print(f'multi_columns in {round(time_mc2-time_mc1,6)} seconds')
    return gq[ab][0],gq[ab][1]

#  #  #   #   #   #  # Função Best_Node (também serve para as Random Forests)
def best_node_MULTI(df,colunas,count,forest=False,perguntas=2): #melhor pergunta de todas as colunas
    #print('Starting best_node_MULTI')
    #time1=time.perf_counter()
    best_question=None
    best_gain=0
    if not(forest): #se não quisermos usar esta função para o modelo Random Forests
        columns=len(df.columns)-1
        #print(columns-1,'columns, best_node')
        for i in range(columns-1): #a última coluna é a var. dep. por isso não queremos saber a sua pergunta (xD)
            #print(i,'column,best_node')
            if len(var_values(df,i))==1:
                #print('opa, afinal tava mal --------------------')
                continue
            q, gain=best_column_question(df,i)
            if gain >= best_gain:
                best_gain, best_question = gain, q
        #print(best_question.column,best_question.value1,best_question.value2,best_question.tipo)
        return best_question, best_gain
    
    else: # se quisermos usar esta função para o modelo DeForest
        best_question, best_gain=multi_columns(df,colunas,perguntas=perguntas)
        #time2=time.perf_counter()
        #print(f'best_node_MULTI in {round(time2-time1,6)} seconds')
        return best_question, best_gain
        
            

##  #  #  #   #  #   #   #  #   #   #   #   #   #   #   #   #   #   #  #  # 

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


class Leaf:
    
    def __init__(self,df):
        self.predictions=depend_counts(df)
        self.probability=proba(df)
        
        
    #Leaf é um dicionário com as var. dep e as vezes q aparecem
    
class Decision_Node:
    def __init__(self,question,true_branch,false_branch):
        self.question=question
        self.true_branch=true_branch
        self.false_branch=false_branch



def def_counterlimit(df,high_limite=20,low_limite=4,percentage=2):
    #normalmente podemos definir nós o limit(de ramos da árvore), maaaaas o número de amostras varia bastante
    #se não houver limite, é normal as árvores acabarem com folhas com 1 amostra o que é mau para bias/variance
    #assim com esta função, define-se o limit com base no tamanho da DataFrame
    #percentage:
    #diz a percentagem dos dados que queremos em cada folha
    #limite:
    #se houver MUITOOOOOOS dados, com a percentage que temos pode resultar em folhas com 100 amostras o que é um bocado
    #assim estabelecemos um limite(high_limite), que é mais importante que a percentage
    #low_limite serve para as amostras com poucos dados
    size=len(df.index)
    leaf_size=int((size*percentage)/100)
    if leaf_size>high_limite:
        ind=round(size/high_limite)
        limit=round(np.log2(ind))
    elif leaf_size<low_limite:
        ind=round(size/low_limite)
        limit=round(np.log2(ind))
    else:
        ind=round(size/leaf_size)
        limit=round(np.log2(ind))

    return limit




def build_tree(df,colunas,limit=None,forest=False,count=0,perguntas=2): #colunas é por nome, não é índice
    #função recursiva que faz árvore (very nice)
    #limit: 2^limit (2**limit) é o número de leafs máximas que queremos
    #limit=None, significa que não tem número máximo e constrói a árvore sem limites
    #count é um 'counter' necessário para fazer funcionar o limit
    #mas como a função é recursiva, ele tem de ser carregado de recursão em recursão
    #como argumento. Não modificar o count qnd chamamos a função é 0 e sempre será
    #print('Building Tree')
    if count==limit:
        return Leaf(df)
    ###########################
    #ATENÇÃO!!!!!!!!!- Muito específico
    #Foi apenas para um modelo
    if len(df)<50: 
        return Leaf(df)
    # # # # # # # Fim do específico
    q,gain=best_node_MULTI(df,colunas,count,forest,perguntas=perguntas) 
    if gain == 0:
        return Leaf(df)
    t, f =partition(df, q)
    #print('!!!!! Len T:',len(t.index),'Len F:',len(f.index),'!!!!!!!')
    count+=1
    #if len(t)<50:
    #    true_branch=t
    #else:
    true_branch=build_tree(t,colunas,limit=limit,forest=forest,count=count,perguntas=perguntas)
    #if len(f)<50:
    #    false_branch=f
    #else:
    false_branch=build_tree(f,colunas,limit=limit,forest=forest,count=count,perguntas=perguntas)
    return Decision_Node(q,true_branch,false_branch)


def classify_row(df,node,probability=True):
    #sevre para chegarmos as folhas
    #só serve para uma linha/amostra de dados serve 
    if isinstance(node,Leaf):
        if probability:
            return node.probability
        else:
            return node.predictions
    if node.question.match(df):
        return classify_row(df,node.true_branch,probability)
    else:
        return classify_row(df,node.false_branch,probability)
    
def test_tree(df,tree,var=1,limite=60):
    #testa uma árvore, sabendo que a var só é considerada 1 se probabilidade>=limite
    #devolve uma lista com os valores q previu

    limit=len(df.index)
    predicted=[] #valores previstos vão estar em lista
    for i in range(limit):
        row=pd.DataFrame(df.iloc[i,:]).T
        d_proba=classify_row(row,tree)
        if d_proba[var]>=60:
            predicted+=[var]
        else:
            predicted+=[1-var] #se var=0,1 e se var=1,0
    return predicted

#  #   #  #  #  #  #  #  # #  # FUNÇÕES PARA A CONFUSION MATRIX
#m é a confusion matrix, ind é o indíce da variável que queremos testar
#ind começa em 0
def sensitivity(m,ind):
    if not(len(m)==len(m[0])):
        return 'Erro! A matriz tem ser ser quadrada'
    print('O índice começa em 0')
    x=m[ind][ind]
    n=0
    q=[]
    while n<len(m):
        if n==ind:
            n+=1
        else:
            q+=[m[n][ind]]
            n+=1
    y=sum(q)
    return round((x/(x+y))*100,2)

def specificity(m,ind):
    if not(len(m)==len(m[0])):
        return 'Erro! A matriz tem ser ser quadrada'
    print('O índice começa em 0')
    n=0
    q=[]
    while n<len(m):
        if n==ind:
            n+=1
        else:
            q+=[m[ind][n]]
            n+=1
    x=sum(q)
    f=[]
    i=0
    while i<len(m):
        c=0
        if i==ind:
            i+=1
        else:
            while c<len(m):
                if c==ind:
                    c+=1
                else:
                    f+=[m[i][c]]
                    c+=1
            i+=1
    y=sum(f)
    #print(q,f)  #verifica se os valores q estamos a escolher são os certos
    return round((y/(x+y))*100,2)

#A percentagem de previsões corretas feitas pelo modelo
#i é a linha da confusion matrix (o outcome que queremos ver a percentagem de previsões corretas)
def pred_percent(m,i):
    #print(m)
    if not(len(m)==len(m[0])):
        return 'Erro! A matriz tem ser ser quadrada'
    #print('O índice começa em 0')
    x=m[i][i]
    soma=sum(m[i])
    if soma==0:
        return 'Não previu nada para esta variável'
    else:
        return round((x/soma)*100,2)

## # # # # #  #  #  #   #   #  #   #   #  #  #  #  #  #  #  #  # #
 
def cmat_tree(df,tree,var=1,limite=60):
    y_real=list(df.iloc[:,-1]) #lembrar q a variável dep tem de estar na última coluna
    y_predicted=test_tree(df,tree,var,limite)
    cmat=np.array([[0,0],[0,0]])
    for i in range(len(y_real)):
        if y_real[i]==1 and y_predicted[i]==1:
            cmat[0][0]+=1
        elif y_real[i]==1 and y_predicted[i]==0:
            cmat[1][0]+=1
        elif y_real[i]==0 and y_predicted[i]==1:
            cmat[0][1]+=1
        elif y_real[i]==0 and y_predicted[i]==0:
            cmat[1][1]+=1
        else:
            print('Erro na cmat_tree')
            return 'Erro na cmat_tree'
    return cmat, pred_percent(cmat,1-var)
#Porquê '1-var'?
#lembrar q o 2o parametro do pred_percent indica a posição da variável na matriz
#como 1 está na posição 0 e 0 está na posição 1
#a posição é gerada corretamente em função da variável (0/1) 


#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################
#######################################################################

class Forest:
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
    
    
def random_df(df): #cria a tal Bootstrapped dataset 
    size=len(df.index)
    done=False
    new_df=pd.DataFrame()
    i=0
    while i<=(size+2) and not done: #size+2 é só pq sim
        ind=random.randrange(size)
        ds=pd.DataFrame(df.iloc[ind,:]).T
        new_df=pd.concat([new_df,ds],sort=False)
        if len(new_df.index)==size:
            done=True
    return new_df.reset_index(drop=True)

#Funções para diminuir o número de valores das colunas para usar as perguntas 2-------------------------------------------------------
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
    if all(tf_val):
        return c_val,ten
    else:
        ten+=1
        n_val=np.array(list(map(lambda x:x*10,c_val)))
        return check_float(n_val,ten)

#------------------------- Acabaram as Funções para diminuir o número de valores das colunas para usar as perguntas 2---------------------

def name_index(df,column): #transforma o nome das colunas nos índices correspondentes
    columnz=df.columns
    ind=[]
    for w,i in enumerate(columnz):
        if i==column:
            return w


def T(test,T_df): #aplica as transformações do T_df no test
    try:
        if T_df=='None':
            return test
    except:
        print('Cagou no None')
        for i in range(len(T_df)):
            if T_df.iloc[i]['Check_Float']!=0:
                test[:,i]=np.array(list(map(lambda x:x*(10*(T_df.iloc[i]['Check_Float'])),test[:,i]))) #check_float
            if T_df.iloc[i]['ACV_Coef']!='None':
                test[:,i]=np.array(list(map(lambda x:x//(T_df.iloc[i]['ACV_Coef']),test[:,i]))) #acv
        return test   
        

def build_forest(df,lista,none_limit=False,my_limit=4,forest=True,bootstrap=False,Min=6,Max=8,perguntas=2,count=0):
    #none_limit e count servem para a função build_tree
    #bootstrap diz se cada vez que fazemos uma árvore fazemos random da dataframe ou não (T/F)
    #none_limit é responsável pelo limit da função build_tree
    #Se T: Não há limite de ramos nas árvores
    #Se F: Há limite, calculado pela função def_counterlimit()
    #NOTA: Esta função tem mais parâmetros dos que aqueles que aparecem aqui, mas os mudar é preciso ir à definição da função
    F=Forest()
    print('criou floresta')
    if none_limit:
        limit=None
    else:
        if not(my_limit):
            limit=def_counterlimit(df)
        else:
            limit=my_limit


    lista_ind=[]
    for i in range(len(lista)):
        ok=list(map(name_index,[df]*len(lista[i]),[lista[i][n] for n in range(len(lista[i]))]))
        lista_ind+=[ok]
    print('len(lista_ind)',len(lista_ind))
    the_df=df.values
    the_df,T_df=adjust_column_values(the_df,mini=Min,maxi=Max,perguntas=perguntas) #comentar isto se usarmos apenas perguntas tipo=0
    for m in range(len(lista_ind)):
        colunas=lista_ind[m]
        if m<2: #dps apago, é só para ver se funciona
            print(colunas,'colunas (dps apagar o print)')
        if None in colunas:
            print(colunas, 'tree: ',m)
        if bootstrap:
            print('tree',m)
            new_df=random_df(df)
            new_tree= build_tree(new_df,colunas,limit=limit,forest=forest,count=count,perguntas=perguntas)
            F.add_tree(new_tree)
        else:
            print('tree',m)
            start1=time.perf_counter()
            new_tree= build_tree(the_df,colunas,limit=limit,forest=forest,count=count)
            F.add_tree(new_tree)
            finish1=time.perf_counter()
            print(f'Tree in {round(finish1-start1,2)} segundos')
            print('||')
            print('||')
            print('Forest Size = ',F.size())
            print('||')
            print('||')

    return F, T_df

# Added ------------------------------------- Multi ---------------------------------------
#def multi_forest():

 #   build_forest(df,trees=1000,none_limit=False,forest=True,auto=True,columns_percentage=50,bootstrap=False,count=0)


#1o vamos tentar ver com o q já temos 
# -----------------------------------------------------------------------------------------


def classify_df(DF,node,var=1):
    #var_list irá conter os índices onde a previsão da floresta foi 1
    #sevre para chegarmos as folhas
    #só serve para uma linha/amostra de dados serve 
    if isinstance(node,Leaf):
        prob=node.probability
        return [[prob[var],list(DF[:,-1])]] #-1 é o 'Index'                        
    t,f=partition(DF,node.question)
    T=classify_df(t,node.true_branch)
    F=classify_df(f,node.false_branch)
    return T+F #vamos fazendo return da soma das listas com os índices que vão ser previstos com 1


def prob_to_list(w,ind): #serve para o reduce da info das probas (sem usar limite)
    for i in range(len(ind[1])):
        if ind[1][i]!=int(ind[1][i]):
            print(ind[1][i],'----',int(ind[1][i]))
            print('i',i)
        w[int(ind[1][i])]=ind[0]
    return w
    
def tree_proba(df,forest,var=1):
    size=forest.size()
    for t in range(size):
        if t%10==0:
            print(t)
        node=forest.get_tree(t)    
        ko=classify_df(df,node,var=var)
        ko2=np.array([list(reduce(prob_to_list,ko,[0]*len(df)))])
        if t==0:
            tp2=np.array(ko2)
        else:
            tp2=np.concatenate((tp2,ko2))
                    
    return tp2.T

def tree_predictions(proba_list,tree_limite):
    #recebe o output de tree_proba (proba_list) e um tree_limite
    #para devolver bigout1
    final=[]
    for i in range(len(proba_list)):
        ok=[]
        for n in range(len(proba_list[i])):
            if proba_list[i][n]>=tree_limite:
                ok+=[1]
            else:
                ok+=[0]
        final+=[ok]
    m2=final  
    M2=[]
    for i in range(len(m2)):
        dix={0:0,1:0}
        for n in range(len(m2[i])):
            if m2[i][n]==1:
                dix[1]+=1
            else:
                dix[0]+=1
        M2+=[dix]
    return M2 #devolve já em dicionário
    #o mesmo formato do bigout1
    
def make_bigout2(proba_list):
    bigout2=[]
    for i in range(len(proba_list)):
        real=round(sum(proba_list[i]),2) # o que acontece na realidade
        bigout2+=[real]
    return bigout2


# ----- Tentativa de otimizar a Floresta

def good_trees(df,proba_list):
    real=list(df.iloc[:]['Won/NotWon'])
    trees=len(proba_list[0])
    PRED=[]
    NPRED=[]
    PRED_FORM=[]
    NPRED_FORM=[]
    TREE=[]
    for t in range(trees):
        TREE+=[t]
        pred=list(proba_list[:,t])
        predi=0
        npredi=0
        predi_form=0
        npredi_form=0
        for i in range(len(pred)):
            if (real[i]==1 and pred[i]>50) or (real[i]==0 and pred[i]<=50):
                predi+=1
                predi_form+=abs(round(pred[i]-50,2))
            else:
                npredi+=1
                npredi_form+=abs(round(pred[i]-50,2))
        pred_perc=round(100*(predi/(predi+npredi)),2)
        PRED+=[pred_perc]
        NPRED+=[round(100-pred_perc,2)]
        PRED_FORM+=[predi_form]
        NPRED_FORM+=[npredi_form]
    form_diff=list(map(lambda x,y:x-y,PRED_FORM,NPRED_FORM))
    gtree=pd.DataFrame({
        'Tree':TREE,'Predicted_%':PRED,'Not_Predicted_%':NPRED,
        'Predicted_Coef':PRED_FORM,'Not_Predicted_Coef':NPRED_FORM,
        'Diff_Coef':form_diff
    })
    return gtree

def remove_trees(gtrees,proba_list,predicted_limit=55,diff_coef_limit=400):
    #esta função calcula as melhores trees (e as piores)
    #e depois segundo um critério retira as piores trees da proba_list
    # e devolve uma nova proba_list
    to_remove=list(gtrees.loc[(gtrees['Predicted_%']<=predicted_limit) | (gtrees['Diff_Coef']<=diff_coef_limit)].iloc[:]['Tree'])
    for i in to_remove:
        proba_list[:,i]=[0]*len(proba_list)
    done=len(to_remove)
    n=0
    found=0
    while n<len(proba_list[0]) and found<=done:
        if np.count_nonzero(proba_list[:,n])==0:
            proba_list=np.delete(proba_list,n,1)
            found+=1
        else:
            n+=1
    return proba_list



#big_dixx-----------------------------------------------------------------------
from big_dix import *

def remove_columns(file):
    file=file.drop(['League','Date','Time','HT','AT'],axis=1)
    try:
        file=file.drop(['ODDH_Aver.','ODDD_Aver.','ODDA_Aver.'],axis=1)
    except:
        pass
    return file

def lambda_bigout(dic,size,var):
    return round(((dic[var])*100)/size,2)

def lambda_bigout2(val,size):
    return round(val/size,2)

def lambda_forest(limite,val,var):
    if val>=limite:
        return var
    else:
        return 1-var
    
def lambda_reality(pred,wnw,var):
    if pred==(1-var):
        if wnw==var:
            return '----('+str(var)+')'
        else:
            return '----('+str(1-var)+')'
    else:
        if pred==wnw:
            return 'YES'
        else:
            return 'NO'

def Big_dix(df,forest,T_df,var=1,tree_list=list(range(50,101)),
            forest_list=list(range(1,101)),optimize=False):
    df2=remove_columns(df)
    df2=df2.values
    df2=T(df2,T_df)
    index=np.array([[inx] for inx in range(len(df))]) #criamos a coluna index
    df2 = np.append(df2,index,axis=1) #juntamos a coluna index (e tem de estar na posição -1)
    ultimate=big_dix()
    big=big_dix()
    df_OVERALL=[]
    preB2= tree_proba(df2,forest,var=var) #um pre bigout2 e partir deste chegamos ao bigout1 e bigout2
    if optimize:
        gTree=good_trees(df2,preB2) 
        preB2=remove_trees(gTree,preB2,predicted_limit=50,diff_coef_limit=200)
        F_siize=len(preB2[0])
        print(len(preB2[0]))
    else:
        F_siize=forest.size()
    for TL in tree_list:
        print('T'+str(TL))
        tl=big_dix()
        bigout=tree_predictions(preB2,TL)
        bigout2=make_bigout2(preB2)
        for FL in forest_list:
            fl=big_dix()
            #print('bigout',bigout)
            
            df_aux1=pd.DataFrame({'Index':list(range(len(df))),'League':df['League'],'Date':df['Date'],
                                'Time':df['Time'],
                                'HT':df['HT'],'AT':df['AT'],
                                'Tree Score %':list(map(lambda_bigout2,bigout2,[F_siize]*len(bigout2))),
                                'Tree_var%'+str(TL):list(map(lambda_bigout,bigout,[F_siize]*len(bigout),[var]*len(bigout)))})
            df_aux2=pd.DataFrame({'ForestPredix_'+str(FL)+'%':list(map(
                lambda_forest,[FL]*len(df),df_aux1['Tree_var%'+str(TL)],[var]*len(df)))})
            df_aux3=pd.DataFrame({'ForestReal_'+str(FL)+'%':list(map(
                                 lambda_reality,df_aux2['ForestPredix_'+str(FL)+'%'],df['Won/NotWon'],[var]*len(df))),
                                  'Won/NotWon':df['Won/NotWon'],
                                  'ODDH_Aver.':df['ODDH_Aver.'],'ODDD_Aver.':df['ODDD_Aver.'],'ODDA_Aver.':df['ODDA_Aver.']}) #Newww
            
            aaaa=df_aux1['Tree_var%'+str(TL)]
            bbbb=df_aux2['ForestPredix_'+str(FL)+'%']
            dddd=df['Won/NotWon']
            cccc=list(map(lambda x,y,z:[x]+[y]+[z],aaaa,bbbb,dddd))
            df_All=pd.concat([df_aux1,df_aux2,df_aux3],axis=1)
            
            df_Yes=df_All.loc[(df_All['ForestReal_'+str(FL)+'%']=='YES')]
            df_No=df_All.loc[(df_All['ForestReal_'+str(FL)+'%']=='NO')]
            df_var=df_All.loc[(df_All['ForestReal_'+str(FL)+'%']=='----('+str(var)+')')]
            df_Nvar=df_All.loc[(df_All['ForestReal_'+str(FL)+'%']=='----('+str(1-var)+')')]
            df_Predicted=pd.concat([df_Yes,df_No]).sort_values(['Date','Time'],ascending=[True,True])
            df_NonPredicted=pd.concat([df_var,df_Nvar]).sort_values(['Date','Time'],ascending=[True,True])
            
            try:    
                AP=[round(100*(len(df_Yes)/(len(df_Yes)+len(df_No))),2)]
            except:
                AP=[0]
                
            try:
                AGP=[round(100*(len(df_Yes)/(len(df_Yes)+len(df_No)+len(df_var)+len(df_Nvar))),2)]
            except:
                AGP=[0]
                
            try:
                GP=[round(100*((len(df_Yes)+len(df_No))/(len(df_Yes)+len(df_No)+len(df_var)+len(df_Nvar))),2)]
            except:
                GP=[0]
                
            try:
                VP=[round(100*(len(df_Yes)/(len(df_var)+len(df_Yes))),2)]
            except:
                VP=[0]
                
            try:
                VG=[round(100*((len(df_var)+len(df_Yes))/(len(df_var)+len(df_Yes)+len(df_No)+len(df_Nvar))),2)]
            except:
                VG=[0]
            df_OverAll=pd.DataFrame({
                'Method':['TL'+str(TL)+'_FL'+str(FL)],
                'Predicted_Var':[var],
                'Accurate_Predictions':AP,
                'Games_Predicted':GP,
                'Accurate_Games_Predicted':AGP,
                'Var_Predicted':VP,
                'Var_Games':VG     
            })
            
            fl.add_keys(ALL=df_All,Predicted=df_Predicted,Not_Predicted=df_NonPredicted,Yes=df_Yes,No=df_No,
                        NotPred_Var_=df_var,Nvar=df_Nvar,Overall=df_OverAll)
            tl.add_keys_2(['FL'+str(FL)],[fl])
            
            df_OVERALL+=[df_OverAll]
            
        big.add_keys_2(['TL'+str(TL)],[tl])
    
    # new DF with Tree_Score
    df_score=pd.DataFrame({'Index':list(range(len(df))),'League':df['League'],'Date':df['Date'],
                                'Time':df['Time'],
                                'HT':df['HT'],'AT':df['AT'],
                                'Tree Score %':list(map(lambda_bigout2,bigout2,[F_siize]*len(bigout2))),
                                'Won/NotWon':df['Won/NotWon']})
    df_score=df_score.sort_values(['Tree Score %'],ascending=[False])
    #-----------------------------------------------------
    OA=pd.concat(df_OVERALL)
    ultimate.add_keys_2(['Tree_Forest','Tree_Score','OverAll'],[big,df_score,OA])
    return ultimate


    def Filter_Forest(Forest1,Test_df,T_df):
#Esta função serve para remover árvores repetidas
#Devolvendo uma floresta sem árvores repetidas
    New_F = Forest()
    df2=remove_columns(Test_df)
    df2=df2.values
    df2=T(df2,T_df)
    index=np.array([[inx] for inx in range(len(Test_df))]) #criamos a coluna index
    df2 = np.append(df2,index,axis=1) #juntamos a coluna index (e tem de estar na posição -1)
    proba_list = tree_proba(df2,Forest1)
    gt = good_trees(Test1,proba_list).sort_values('Predicted_%',ascending=True)
    gt2=gt.drop_duplicates(subset=['Predicted_%','Not_Predicted_%','Predicted_Coef','Not_Predicted_Coef'])
    for t in range(len(gt2)):
        tree = int(gt2.iloc[t]['Tree'])
        tree2 = Forest1.get_tree(tree)
        New_F.add_tree(tree2)
    return New_F
        




