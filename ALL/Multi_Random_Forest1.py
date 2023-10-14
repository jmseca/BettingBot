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
executor=cf.ProcessPoolExecutor(max_workers=15)

print('Este módulo usa pandas.Dataframe')
print('E está feito para apenas prever variáveis categóricas 0/1')

def var_values(df,column): #dá nos uma lista dos valores de uma variável 
    #Nota, cada variável está associada a uma coluna
    coluna=list(df.iloc[:,column]) #transforma coluna em lista
    q=[]
    for val in coluna:
        if val not in q:
            q+=[val]
    return q

######################## Algoritmo de ordenação Mergesort
def fusao(u,v):
    res=[]
    i=0
    j=0
    for k in range(len(u)+len(v)):
        if i<len(u) and (j==len(v) or u[i]<v[j]):
            res.append(u[i])
            i=i+1
        else:
            res.append(v[j])
            j=j+1
    return res

def mergesort(w):
    if len(w)<2:
        return w
    else:
        m=len(w)//2
        w1=mergesort(w[:m])
        w2=mergesort(w[m:])
        return fusao(w1,w2)
#  #  #  #   #   #  #   #   #  #  #  #  #   # ALGORITMO DE ORDENAÇÃO MERGESORT



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
    #dá as médias dos valores adjacentes para fazer as perguntas
    v1=mergesort(var_values(df,column)) #dá jeito ter estes valores ordenados
    values=[]
    for i in range(len(v1)-1):
        values+=[((v1[i]+v1[i+1])/2)]
    return values 
 
    
    
def depend_counts(df):
    #devolve um dicionário com os valores da variável dependente e as vezes q aparecem
    #NOTA, esta função assume q a variável depend está na última coluna da df
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
                return val > self.value1
            else:
                return self.value1<= val <= self.value2
        else:
            return val==self.value1
#as perguntas tipo 1 podem dar muitoooooooo jeito
        
        
def partition(df, Q):
    true=df.loc[(df[df.columns[Q.column]]>=Q.value1)]
    false=df.loc[(df[df.columns[Q.column]]<Q.value1)]
    return true,false


def gini(df):
    impurity=1
    counts=depend_counts(df)
    for depend in counts:
        impurity-=((counts[depend]/len(df.index))**2)
    return impurity

def info_gain(true,false,current_impurity):
    #true/false são as df q resultam de fazer uma pergunta (definida previamente)
    #current_impurity é o gini da df sem ser dividida por uma pergunta
    p=(len(true)/(len(true)+len(false)))
    info_gain=current_impurity - ((p*gini(true))+((1-p)*gini(false)))
    #print('GAIN',info_gain,'len(true)',len(true),'len(false)',len(false))
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
    print('Starting best_column_question')
    startquestion=time.perf_counter()
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
                    mini=ohshit_aux(df,column)
                    print('len_colum',len(values)+2)# se não me engano var_values=values+2 (em termos de size)
                    print(mini,'-----MA MINIIIIII-----')
                    for i1 in range(len(values)-mini): #se i1 for para lá de values[-2], não rende (ver caderno)
                        for i2 in range(i1+mini,len(values)): #isto do mini é novo, cuidado com erros
                            print('i1',i1,'i2',i2,mini<=(i2-i1),'Just checking')
                            q=Question(column,values[i1],values[i2],tipo=1)
                            t,f =partition(df,q)
                            #se a pergunta não divide os dados fazemos SKIP
                            if len(t) == 0 or len(f) == 0:
                                continue
                            gain = info_gain(t,f,current_impurity)
                            if gain >= best_gain:
                                best_gain, best_question = gain, q
    #print(best_question.value1,best_question.value2,best_question.tipo,'Da coluna:',df.columns[best_question.column],'Com gain:',best_gain)
    finishquestion=time.perf_counter()
    print(f'Best_column_question in {round(finishquestion-startquestion,2)} seconds')
    print('Ending best_column_question')
    return best_question,best_gain

# #  #  Função que faz o MultiProcessing das várias perguntas das várias col #

def multi_columns(df,ind):
    print('Starting Multicolumns')
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
    print('Ending multi_columns')
    return gq[ab][0],gq[ab][1]

#  #  #   #   #   #  # Função Best_Node (também serve para as Random Forests)
def best_node_MULTI(df,forest=False,auto=True,columns_percentage=50): #melhor pergunta de todas as colunas
    print('Starting best_node_MULTI')
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
    
    else: # se quisermos usar esta função para o modelo Random_Forests
        
        if auto: #em modo automático usa a raíz quadrada das colunas
            stop=round(np.sqrt(columns)) 
        else: #se não tiver em auto, escolhemos a percentagem de perguntas a analisar
            stop=round((columns*(columns_percentage))/100)
            
        ind=[] #lista dos índices das colunas q vamos usar
        i=0
        done=False
        while not(done):
            abcd=random.randrange(columns)
            if len(var_values(df,abcd))==1:
                print('----Coluna com 1 var-------')
                #print(df.columns[abcd])
                #print(list(df.iloc[:,abcd]))
                #print(df,'DF')
                #print('--------------------------------')
            if (abcd not in ind) and (len(var_values(df,abcd))!=1):
                ind+=[abcd]      #este ciclo encontra as colunas aleatórias 
            if len(ind)==stop:                    # que vamos utilizar
                done=True
            i+=1
        #print(ind,'colunas a analisar no multi_columns')
        best_question, best_gain=multi_columns(df,ind) #MULTIPROCESSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #print(df.columns[best_question.column],best_question.value1,best_question.value2,best_question.tipo,best_gain,'Melhor Pergunta Do Node')
        #print(f'Node in {round(time2-time1,2)} seconds')
        print('Ending best_node_MULTI')
        return best_question, best_gain
        
##  #  #  #   #  #   #   #  #   #   #   #   #   #   #   #   #   #   #  #  #  
#  #  #   #   #   #  # Função Best_Node (também serve para as Random Forests )#cópia caso a outra corra mal
def best_node(df,forest=False,auto=True,columns_percentage=50): #melhor pergunta de todas as colunas
    columns=len(df.columns)
    best_question=None
    best_gain=0
    if not(forest): #se não quisermos usar esta função para o modelo Random Forests
        #print(columns-1,'columns, best_node')
        for i in range(columns-1): #a última coluna é a var. dep. por isso não queremos saber a sua pergunta (xD)
            #print(i,'column,best_node')
            if len(var_values(df,i))==1:
               # print('opa, afinal tava mal --------------------')
                continue
            q, gain=best_column_question(df,i)
            if gain >= best_gain:
                best_gain, best_question = gain, q
        #print(best_question.column,best_question.value1,best_question.value2,best_question.tipo)
        return best_question, best_gain

    else: # se quisermos usar esta função para o modelo Random_Forests

        if auto: #em modo automático usa a raíz quadrada das colunas
            stop=round(np.sqrt(columns))
        else: #se não tiver em auto, escolhemos a percentagem de perguntas a analisar
            stop=round((columns*(columns_percentage))/100)

        ind=[] #lista dos índices das colunas q vamos usar
        i=0
        done=False
        while not(done):
            abcd=random.randrange(columns) 
            #if len(var_values(df,abcd))==1:
                #print('--------ORA BOLAS----')
                #print(df.columns[abcd],'coluna')
                #print(df,'DF')
            if (abcd not in ind) and (len(var_values(df,abcd))!=1):
                ind+=[abcd]      #este ciclo encontra as colunas aleatórias 
            if len(ind)==stop:                    # que vamos utilizar
                done=True
            i+=1
        #print(ind,'Da coluni')
        for n in ind:
            q, gain=best_column_question(df,n)
            if gain >= best_gain:
                best_gain, best_question = gain, q
        #print(best_question.column,best_question.value1,best_question.value2,best_question.tipo)
        return best_question, best_gain

##  #  #  #   #  #   #   #  #   #   #   #   #   #   #   #   #   #   #  #  # 

def proba(df):
    #calcula a probabilidade dos valores de um dicionário (em percentagem, para evitar float errors)
    #É necessário para as Leafs
    ind=len(df.index)
    dicti=depend_counts(df)
    new={0:0,1:0}  # este módulo de3 decision trees está feito para var dep de 0/1 APENAS
    for var in dicti:
        prob=round(100*(dicti[var]/ind),1)
        new[var]=prob
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




def build_tree(df,limit=None,forest=False,auto=True,columns_percentage=50,count=0):
    #função recursiva que faz árvore (very nice)
    #limit: 2^limit (2**limit) é o número de leafs máximas que queremos
    #limit=None, significa que não tem número máximo e constrói a árvore sem limites
    #count é um 'counter' necessário para fazer funcionar o limit
    #mas como a função é recursiva, ele tem de ser carregado de recursão em recursão
    #como argumento. Não modificar o count qnd chamamos a função é 0 e sempre será
    print('Building Tree')
    if count==limit:
        return Leaf(df)
    q,gain=best_node_MULTI(df,forest,auto,columns_percentage)
    if gain == 0:
        return Leaf(df)
    ###########################
    #ATENÇÃO!!!!!!!!!- Muito específico
    #Foi apenas para um modelo
    if len(df)<30:
        return Leaf(df)
    t, f =partition(df, q)
    print('!!!!! Len T:',len(t.index),'Len F:',len(f.index),'!!!!!!!')
    count+=1
    #if len(t.index)==1:
    #    print(count,'count')
    #    print('---------- T Leaf------------------')
    #    return Leaf(t)
    #if len(f.index)==1:
    #    print(count,'count')
    #    print('---------- F Leaf------------------')
    #    return Leaf(f)
    true_branch=build_tree(t,limit=limit,forest=forest,auto=auto,columns_percentage=columns_percentage,count=count)
    false_branch=build_tree(f,limit=limit,forest=forest,auto=auto,columns_percentage=columns_percentage,count=count)
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
    
def test_tree(df,tree,var=1,tree_limite=60,proba=False):
    #testa uma árvore, sabendo que a var só é considerada 1 se probabilidade>=limite
    #devolve uma lista com os valores q previu
    #proba diz se queremos a probability, ou usar o limite
    size=len(df.index)
    predicted=[] #valores previstos vão estar em lista
    for i in range(size):
        row=pd.DataFrame(df.iloc[i,:]).T
        d_proba=classify_row(row,tree)
        if not(proba):
            if d_proba[var]>=tree_limite:
                predicted+=[var]
            else:
                predicted+=[1-var] #se var=0,1 e se var=1,0
        else:
            predicted+=[d_proba[var]]
    #print('red',predicted)
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
        

def build_forest(df,trees=1000,none_limit=False,my_limit=4,forest=True,auto=True,columns_percentage=50,bootstrap=False,count=0):
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
    for i in range(trees):
        if bootstrap:
            print('i',i)
            new_df=random_df(df)
            new_tree= build_tree(new_df,limit=limit,forest=forest,auto=auto,columns_percentage=columns_percentage,count=count)
            F.add_tree(new_tree)
        else:
            print('i',i)
            start1=time.perf_counter()
            new_tree= build_tree(df,limit=limit,forest=forest,auto=auto,columns_percentage=columns_percentage,count=count)
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
 
 
 
 

def forest_classify(df,forest,tree_limite=60):
    #devolve lista de dicionários em que cada dict refer-se a uma amostra/linha
    #e os valores de cada dict referem-se as previsões de cada árvore em 
    #relação a essa amostra
    rows=len(df.index)
    bigout=[]
    bigout2=[]
    for i in range(rows):
        print(i,'i')
        output={0:0,1:0}
        output2=0
        row=pd.DataFrame(df.iloc[i,:]).T
        trees=forest.size()
        for n in range(trees):
            tree=forest.get_tree(n)
            
            val=test_tree(row,tree,tree_limite=tree_limite)[0] #previsões 0/1
            
            val2=test_tree(row,tree,tree_limite=tree_limite,proba=True)[0] #score
            output2+=val2 #score
            output[val]+=1 #previsões 0/1
            
        bigout+=[output]
        
        bigout2+=[output2]
    return bigout,bigout2

def forest_predictions(df, forest, var=1, forest_limite=60,tree_limite=60):
    #devolve uma lista com as previsões da floresta
    #impondo um limite (percentagem) a uma variável
    #(só dizemos que se trata dessa variável se a percentagem de probabilidade)
    #for igual ou superior
    final=[]
    classi=forest_classify(df,forest,tree_limite=tree_limite)
    #print(classi)
    for i in classi:
        print('len',len(final))
        prob=round((i[var]/(forest.size()))*100,2)
        if prob>=forest_limite:
            final+=[var]
        else:
            final+=[1-var]
    return final

def cmat_forest(df,forest,var=1,limite=60):
    real=list(df.iloc[:,-1])
    predicted=forest_predictions(df,forest,var,limite)
    print('predicted',predicted)
    cmat=np.array([[0,0],[0,0]])
    for i in range(len(real)):
        if real[i]==1 and predicted[i]==1:
            cmat[0][0]+=1
        elif real[i]==1 and predicted[i]==0:
            cmat[1][0]+=1
        elif real[i]==0 and predicted[i]==1:
            cmat[0][1]+=1
        elif real[i]==0 and predicted[i]==0:
            cmat[1][1]+=1
        else:
            print('Erro na cmat_forest')
            return 'Erro na cmat_forest'
    return cmat, pred_percent(cmat,1-var)

##############################---BIG_DIX--------------

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
            
def go_get(dixx,count=0):
    if count==0:
        print(type(dixx))
    print(dixx.keys())
    new=input("Choose One of The Above: ")
    if new not in dixx.keys():
        raise('Valor não existe no big_dix')
    dixx=dixx.dix[new]
    if type(dixx)==big_dix:
        count+=1
        return go_get(dixx,count)
    else:
        return dixx
    
    



