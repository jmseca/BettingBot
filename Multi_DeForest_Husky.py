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
executor=cf.ProcessPoolExecutor(max_workers=15)

print('Este módulo usa pandas.Dataframe')
print('E está feito para apenas prever variáveis categóricas 0/1')
print(' ')
print('No DeForest, escolhemos as colunas a analisar por árvore')
print('Ao contrário do Random_Forest, onde fazíamos random')


def var_values(df,column): #dá nos uma lista dos valores de uma variável 
    #Nota, cada variável está associada a uma coluna
    return list(df[df.columns[column]].unique())

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
    
    
       
def not_categorical_values(df,column):
    #ncv1=time.perf_counter()
    #dá as médias dos valores adjacentes para fazer as perguntas
    v1=sorted(list(df.iloc[:][df.columns[column]].round(4))) #dá jeito ter estes valores ordenados
    values=[]
    for i in range(len(v1)-1):
        values+=[round(((v1[i]+v1[i+1])/2),4)]
    #ncv2=time.perf_counter()
    #Fprint(f'not_categorical_values in {round(ncv2-ncv1,6)} seconds')
    return values 
 
    
    
def depend_counts(df,fast=False):
    #devolve um dicionário com os valores da variável dependente e as vezes q aparecem
    #NOTA, esta função assume q a variável depend está na última coluna da df
    if fast:
        coluna=df[:,-1] #que neste caso é np.array
        counts=np.unique(coluna,return_counts=True)[1]
        return counts #lista com dois elementos
        #[0] número de vezes do 0
        #[1] número de vezes do 1
    else:
        counts={}
        coluna=list(df.iloc[:,-1])
        for val in coluna:
            if val not in counts:
                counts[val]=0
            counts[val]+=1
        return counts

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
        

def partition(df,Q,fast=False): #fast usa/devolve numpy arrays || not(fast) usa/devolve pd.DF
    if fast:
        df2=df.values
        #timeP=time.perf_counter()
    
        t1=np.where(df2[:,Q.column]>=Q.value1)
        false=np.delete(df2,t1,0)
        f1=np.where(df2[:,Q.column]<Q.value1)
        true=np.delete(df2,f1,0)
        
        #timeP2=time.perf_counter()
        #print(f'Fast Partition in {round(timeP2-timeP,6)} seconds')
        return true,false
    else:
        #timeP=time.perf_counter()
        #divide uma dataframe em valores que que acertam a pergunta e que erram
        #só resulta para perguntas numéricas do tipo 0
        #se precisarmso de perguntas string, usamos o old_partition
        true=df.loc[(df[df.columns[Q.column]]>=Q.value1)]
        false=df.loc[(df[df.columns[Q.column]]<Q.value1)]
        #timeP2=time.perf_counter()
        #print(f'Slow Partition in {round(timeP2-timeP,6)} seconds')
    return true,false


def gini(df,fast=False):
    if fast:
        impurity=1
        counts=depend_counts(df)#,fast=True)
        for depend in counts:
            impurity-=((depend/len(df))**2)
        return impurity
    else:
        impurity=1
        counts=depend_counts(df)
        for depend in counts:
            impurity-=((counts[depend]/len(df.index))**2)
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
    val=var_values(df,column)
    diff=[3] #não interessa a quantidade de valores de uma variável, vou definir que o mínimo no máximo é 3
    diff+=[1+(val%6)] #vou definir a regra em grupos de 6
    mini=min(diff)
    return mini

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
            t,f =partition(df,q)#,fast=True)
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
            t,f =partition(df,q)#,fast=True)
            gain = info_gain(t,f,current_impurity)
            if gain >= best_gain:
                best_gain, best_question = gain, q
        else:
            #print('oh shit, here we go again, best_question')
            values=not_categorical_values(df,column)
            #print(values,'oh shit values')
            for i in range(perguntas): #Faz ciclo dos tipos de perguntas (1 ou 2)
                if i==0: #para perguntas tipo 0
                    for val in values:
                        q=Question(column,val,tipo=0)
                        t,f =partition(df,q)#,fast=True)
                        #se a pergunta não divide os dados fazemos SKIP
                        if len(t) == 0 or len(f) == 0:
                            continue
                        gain = info_gain(t,f,current_impurity)
                        if gain >= best_gain:
                            best_gain, best_question = gain, q
                            
                else: #para perguntas tipo 1
                    mini=ohshit_aux(df,column)
                    print('len_colum',len(values)+2)# se não me engano var_values=values+2 (em termos de size)
                    print(mini,'-----MA MINIIIIII-----')
                    for i1 in range(len(values)-mini): #se i1 for para lá de values[-2], não rende (ver caderno)
                        for i2 in range(i1+mini,len(values)): #isto do mini é novo, cuidado com erros
                            print('i1',i1,'i2',i2,mini<=(i2-i1),'Just checking')
                            q=Question(column,values[i1],values[i2],tipo=1)
                            t,f =partition(df,q)#,fast=True)
                            #se a pergunta não divide os dados fazemos SKIP
                            if len(t) == 0 or len(f) == 0:
                                continue
                            gain = info_gain(t,f,current_impurity)
                            if gain >= best_gain:
                                best_gain, best_question = gain, q
    #print(best_question.value1,best_question.value2,best_question.tipo,'Da coluna:',df.columns[best_question.column],'Com gain:',best_gain)
    #finishquestion=time.perf_counter()
    #print(f'Best_column_question in {round(finishquestion-startquestion,6)} seconds')
    #print('Ending best_column_question')
    return best_question,best_gain

# #  #  Função que faz o MultiProcessing das várias perguntas das várias col #

def multi_columns(df,ind):
    #time_mc1=time.perf_counter()
    #ind é a lista com as colunas 
    gq=list(executor.map(best_column_question,[df]*len(ind),ind))
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
def best_node_MULTI(df,colunas,count,forest=False): #melhor pergunta de todas as colunas
    #print('Starting best_node_MULTI')
    #time1=time.perf_counter()

    columns=len(df.columns)-1
    best_question=None
    best_gain=0
    if not(forest): #se não quisermos usar esta função para o modelo Random Forests
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
        best_question, best_gain=multi_columns(df,colunas)
        #time2=time.perf_counter()
        #print(f'best_node_MULTI in {round(time2-time1,6)} seconds')
        return best_question, best_gain
        
            

##  #  #  #   #  #   #   #  #   #   #   #   #   #   #   #   #   #   #  #  # 

def proba(df):
    #prob1=time.perf_counter()
    #calcula a probabilidade dos valores de um dicionário (em percentagem, para evitar float errors)
    #É necessário para as Leafs
    ind=len(df.index)
    dicti=depend_counts(df)
    new={0:0,1:0}  # este módulo de3 decision trees está feito para var dep de 0/1 APENAS
    for var in dicti:
        prob=round(100*(dicti[var]/ind),1)
        new[var]=prob
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




def build_tree(df,colunas,limit=None,forest=False,count=0): #colunas é por nome, não é índice
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
    q,gain=best_node_MULTI(df,colunas,count,forest) 
    if gain == 0:
        return Leaf(df)
    t, f =partition(df, q)
    #print('!!!!! Len T:',len(t.index),'Len F:',len(f.index),'!!!!!!!')
    count+=1
    #if len(t)<50:
    #    true_branch=t
    #else:
    true_branch=build_tree(t,colunas,limit=limit,forest=forest,count=count)
    #if len(f)<50:
    #    false_branch=f
    #else:
    false_branch=build_tree(f,colunas,limit=limit,forest=forest,count=count)
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


def name_index(df,column): #transforma o nome das colunas nos índices correspondentes
    columnz=df.columns
    ind=[]
    for w,i in enumerate(columnz):
        if i==column:
            return w
        

def build_forest(df,lista,none_limit=False,my_limit=4,forest=True,bootstrap=False,count=0):
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
    for m in range(len(lista_ind)):
        colunas=lista_ind[m]
        if m<2: #dps apago, é só para ver se funciona
            print(colunas,'colunas (dps apagar o print)')
        if bootstrap:
            print('tree',m)
            new_df=random_df(df)
            new_tree= build_tree(new_df,colunas,limit=limit,forest=forest,count=count)
            F.add_tree(new_tree)
        else:
            print('tree',m)
            start1=time.perf_counter()
            new_tree= build_tree(df,colunas,limit=limit,forest=forest,count=count)
            F.add_tree(new_tree)
            finish1=time.perf_counter()
            print(f'Tree in {round(finish1-start1,2)} segundos')
            print('||')
            print('||')
            print('Forest Size = ',F.size())
            print('||')
            print('||')

    return F

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
        return [[prob[var],list(DF.iloc[:]['Index'])]]
    
    t,f=partition(DF,node.question)
    if (DF.columns[node.question.column]=='Won/NotWon') or (DF.columns[node.question.column]=='Index'):
        print('Big OOpps')
        raise('Erro')
    T=classify_df(t,node.true_branch)
    F=classify_df(f,node.false_branch)
    return T+F #vamos fazendo return da soma das listas com os índices que vão ser previstos com 1


def prob_to_list(w,ind): #serve para o reduce da info das probas (sem usar limite)
    for i in range(len(ind[1])):
        w[ind[1][i]]=ind[0]
    return w
    
def tree_proba(df,forest,var=1):
    size=forest.size()
    for t in range(size):
        if t%10==0:
            print(t)
        node=F.get_tree(t)    
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


