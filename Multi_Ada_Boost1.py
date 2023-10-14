# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:23:56 2020

@author: joaom
"""
import time
import pandas as pd
import numpy as np
import concurrent.futures as cf
import random

executor=cf.ProcessPoolExecutor(max_workers=20)
#import random

print('Amount_of_Say, Weights, ... vão estar na ordem das unidades com 6 casas decimais')
print('também está feito apenas para variáveis 0/1')

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
 
# # #  # #  # # # # #  # Aux do Not_Cat_Values # #  # #
def notaux(i,v1):
    #print('doing sth')
    return ((v1[i]+v1[i+1])/2)
# #  # # # #  # # #  # #


def not_categorical_values(df,column):
    #print('está nos not_categ_values')
    #dá as médias dos valores adjacentes para fazer as perguntas
    v1=mergesort(var_values(df,column)) #dá jeito ter estes valores ordenados
    values=[]
    #print(v1,'cenas do mergesort')
    #def notaux(i,v1):
     #   return ((v1[i]+v1[i+1])/2)
    #print('avanço1')
    #print('11',list(range(len(v1)-1)))
    #print('22',[[v1]*(len(v1)-1)])
    #values=executor.map(notaux,list(range(len(v1)-1)),[[v1]*(len(v1)-1)])
    #print('avanço2',values)
    for i in range(len(v1)-1):
        values+=[((v1[i]+v1[i+1])/2)]
    return values 
 
    
    
def ada_depend_counts(df):
    #devolve um dicionário com os valores da variável dependente e as vezes q aparecem
    #É para ser usada no adaboost, pois neste modelo, colocamos os pesos na coluna -1, e as var dep. na -2
    counts={}
    coluna=list(df.iloc[:,-2])
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
            return val == self.value1
            
def partition(df, Q):
    true=df.loc[(df[df.columns[Q.column]]>=Q.value1)]
    false=df.loc[(df[df.columns[Q.column]]<Q.value1)]
    return true,false


def choose_correct(t,f): #escolhe qual das folhas do stump prevê 1 e qual prevê 0
    cc1=time.perf_counter()
    #devolve boleano, erro menor
    #True se true_rows prever 1
    #False se true_rows prever 0
    #caso 1, true->1  false->0
    #caso 2, true->0  false->1
    #t,f=partition(df,question)
    #sizef=len(f.index)
    #sizet=len(t.index)
    erro1=0  #caso 1, true->1  false->0
    erro2=0  #caso 2, true->0  false->1

    erro1+=sum(list((t.loc[(t[t.columns[-2]])==0])[t.columns[-1]]))
    erro2+=sum(list((t.loc[(t[t.columns[-2]])==1])[t.columns[-1]]))

    erro1+=sum(list((f.loc[(f[f.columns[-2]])==0])[f.columns[-1]]))
    erro2+=sum(list((f.loc[(f[f.columns[-2]])==1])[f.columns[-1]]))
    #print(erro1,erro2)   
    cc2=time.perf_counter()    
    #print(f'choose_correct in {round(cc2-cc1,2)} seconds')
    if erro1>=erro2:
        return False,erro2
    else:
        return True,erro1

# # #  # # # #  # # Função auxiliar das perguntas tipo 1 (oh shit here we go again) ####
def ohshit_aux(df,column):
    #dá o mínimo do tamanho dos intervalos que podemos fazer com as perguntas tipo1
    #antes o modelo fazia muitas vezes perguntas a um só valor de uma variável,
    #o que é muito mau para a relação bias/variance
    #(acho eu) se depois os resultados não forem benéficos é só voltar ao normal
    val=len(var_values(df,column))
    diff=[3] #não interessa a quantidade de valores de uma variável, vou definir que o mínimo no máximo é 3
    diff+=[1+(val%6)] #vou definir a regra em grupos de 6
    mini=min(diff)
    return mini

##  #  #  #  #  #   # #  #  # #  #  # #  # # #  # # ##     #    #  # #  # # #  # # # #
    
def Ada_best_column_question(df,column,perguntas=1):
    start=time.perf_counter()
    #print('Going best_columns')
    best_question=None
    boly=None
    Err=1
    if string_column(df,column):
        #print('gone to string')
        values = var_values(df,column)
        for val in values:
            q=Question(column,val)
            t,f =partition(df,q)
            #se a pergunta não divide os dados fazemos SKIP
            if len(t) == 0 or len(f) == 0:
                continue
            b, erro=choose_correct(t,f)
            if erro <= Err:
                boly, Err, best_question = b, erro, q
    else:
        if is_categorical(df,column):
            #print('gone to categorical')
            values = var_values(df,column) 
            assert len(values)==2
            value = (values[0]+values[1])/2
            q=Question(column,value,tipo=0)
            t,f =partition(df,q)
            b, erro=choose_correct(t,f)
            if erro <= Err:
                boly, Err ,best_question = b,erro,q
        else:
            #print('já foste')
            #print('oh shit, here we go again, best_question')
            values=not_categorical_values(df,column)
            #print(values,'oh shit values')
            #print(values,'values')
            for i in range(perguntas): #Faz ciclo dos tipos de perguntas (1 ou 2)
                if i==0: #para perguntas tipo 0
                    for val in values:
                        q=Question(column,val,tipo=0)
                        t,f =partition(df,q)
                        #se a pergunta não divide os dados fazemos SKIP
                        if len(t) == 0 or len(f) == 0:
                            continue
                        b, erro=choose_correct(t,f)
                        if erro <= Err:
                            boly, Err, best_question = b, erro, q


                else: #para perguntas tipo 1
                    print('OMGGG')
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
                            b, erro=choose_correct(t,f)
                            if erro <= Err:
                                boly, Err, best_question = b, erro, q                         
    #print(best_question.value1,best_question.value2,best_question.tipo)
    finish=time.perf_counter()
    #print(f' Best Column in {round(start,finish,2)} seconds')
    return best_question,boly,Err

#  # # #  # #  #  #  #  # #  # #  # #  # #   # #  # # #  # #  # # #  # #  #  # #  #

def multi_columns(df,ind):
    mc1=time.perf_counter()
    #ind é a lista com as colunas 
    #print('Está no multi_columns')
    gq=list(executor.map(Ada_best_column_question,[df]*len(ind),ind))
    #print('--GQ--',gq)
    #gq é uma lista de listas com perguntas e gains
    gq_gain=[gq[i][2] for i in range(len(gq))]
    min_err=min(gq_gain)
    ab=0
    done=False
    while ab<len(gq) and not done:
        if gq[ab][2]==min_err:
            done=True
        else:
            ab+=1
    mc2=time.perf_counter()
    #print(f'Multi_columns in {round(mc2-mc1,2)} seconds')
    return gq[ab][0],gq[ab][1],gq[ab][2]



def Ada_best_stump(df,auto_columns,columns_percentage): #NOTA, esta função apenas serve para ADABOOST, não tem random de colunas
    #ou de amostras, para fazer Random_Forest
    #se der erro ver OldAda_best_stump no final
    Err=1
    best_question=None
    boly=None
    columns=len(df.columns)-2
    ind=[]
    if auto_columns: #em modo automático usa a raíz quadrada das colunas
        stop=round(np.sqrt(columns)) 
    else: #se não tiver em auto, escolhemos a percentagem de perguntas a analisar
        stop=round((columns*(columns_percentage))/100)
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
    print('ind',ind)
    #print('Going multi_columns')
    best_question, boly, Err=multi_columns(df,ind)
    #print(best_question.column,best_question.value1,best_question.value2,best_question.tipo)
    return best_question, boly, Err

def amount_of_say(error):
    if error==0:
        return round((1/2)*np.log(1/(0+10**(-308))),6) #fui testar, e é mínimo que podemos adicionar sem dar erro
    elif error==1:
        return round((1/2)*np.log((0+10**(-323))/1),6) #fui testar, e é mínimo que podemos adicionar sem dar erro
    elif 0<error<1:
        return round((1/2)*np.log((1-error)/error),6)
    else:
        print('Erro no amount_of_say')
        return 'Erro no amount_of_say'







class AdaLeaf:
#as adaLeaf dizem se preveem 0/1  
    def __init__(self,var):
        self.var=var
        
    #Leaf é um dicionário com as var. dep e as vezes q aparecem
    
class Stump:
    def __init__(self,question,leaf1,leaf2,a_of_say):
        self.question=question
        self.true_branch=leaf1
        self.false_branch=leaf2
        self.a_of_say=a_of_say #amount of say
        
    
class AdaForest:
    #floresta de Stumps
    
    def __init__(self):
        self.stumps=[]
        
    def add_stump(self,stump):
        (self.stumps)+=[stump]
        
    def size(self):
        return len(self.stumps)
    
    def get_stump(self,ind):
        return self.stumps[ind]
    
    def merge_adaforests(self,adaforest):
        (self.stumps)+=(adaforest.stumps)
        
   
#  # #  # #lambdas para o first_weight #  #  # #
def lambda2(x,size):
    return round(x/size,6)

def lambda1(x,var,var_percentage,varz,notvarz):
    if x==var:
        return (var_percentage)/(varz*100)
    else:
        return ((100-var_percentage)/(notvarz*100))

# #  #  #  #  #  #  #  # #  # # #  # #  #    
def first_weights(df,auto=True,var=1,var_percentage=70):
    size=len(df.index)
    if auto:
        simple=[1]*size
        w1=list(executor.map(lambda2,simple,[size]*len(simple)))
        weights=pd.DataFrame({'Sample_Weights':w1})
        df=pd.concat([df,weights],sort=False,axis=1)
    else:
        varz=0
        notvarz=0
        for i in range(size):
            if df.iloc[i][-1]==var: #as var dep ainda estão na última coluna
                varz+=1
            else:
                notvarz+=1
        dep=list(df.iloc[:,-1])
        w1=list(executor.map(lambda1,dep,[var]*len(dep),[var_percentage]*len(dep),[varz]*len(dep),[notvarz]*len(dep)))
        weights=pd.DataFrame({'Sample_Weights':w1})
        df=pd.concat([df,weights],sort=False,axis=1)
        
    return df

def right_wrong(df,question,boly):
    #ja verificado que da o mesmo resultado que o old_right_wrong
    newrw=time.perf_counter()
    a=list(np.where(np.logical_or(np.logical_or(np.logical_and((df[df.columns[question.column]]>=question.value1),np.logical_and((df[df.columns[-2]]==1),(not(boly)))),
             np.logical_and((df[df.columns[question.column]]>=question.value1),np.logical_and((df[df.columns[-2]]==0),(boly)))),np.logical_or(
             np.logical_and((df[df.columns[question.column]]<question.value1),np.logical_and((df[df.columns[-2]]==1),(boly))), 
             np.logical_and((df[df.columns[question.column]]<question.value1),np.logical_and((df[df.columns[-2]]==0),(not(boly)))))),'W','R'))
    newrw2=time.perf_counter()
    print(f'Finito RW in {round(newrw2-newrw,2)} seconds')
    return a



    
        
def aux_weights(df,rw,a_say):
    size=len(df.index)
    old_weight=list(df.iloc[:,-1])
    df=df.drop('Sample_Weights',axis=1)
    new_weight=[]
    for i in range(size):
        if rw[i]=='R':
            new_weight+=[old_weight[i]*(np.e**(-a_say))]
        else:
            new_weight+=[old_weight[i]*(np.e**(a_say))]
    return df,new_weight

#  # # #  # #  # #  # # Lambdas para os new_weights  #  # # #
def lambda3(x,re):
    return round(x/re,6)

 # # #  # #  # # #  # #  # # #  # #  # # #  ##

def new_weights(df,rw,a_say):
    df,new_weights=aux_weights(df,rw,a_say)
    re=sum(new_weights)
    s_weight=list(executor.map(lambda3 ,new_weights,[re]*len(new_weights)))
    #print('PESOS',s_weight)
    Weight=pd.DataFrame({'Sample_Weights':s_weight})
    df=pd.concat([df,Weight],sort=False,axis=1)
    return df
    
    
    
def build_stump(df,auto_columns,columns_percentage):
    #função para AdaBoost, não serve para mais nada
    abs1=time.perf_counter()
    best_question, boly, Err = Ada_best_stump(df,auto_columns,columns_percentage)
    abs2=time.perf_counter()
    print(f'Found best stump in {round(abs2-abs1,2)} seconds')
    rw=right_wrong(df,best_question,boly)
    abs3=time.perf_counter()
    print(f'Done right_wrong in {round(abs3-abs2,2)} seconds')
    a_say=amount_of_say(Err)
    if boly:
        a1=AdaLeaf(1)
        a2=AdaLeaf(0)   
    else:
        a1=AdaLeaf(0)
        a2=AdaLeaf(1)
    df=new_weights(df,rw,a_say)
    return Stump(best_question,a1,a2,a_say),df
    
    
def build_AdaForest(df,stumps=100,auto=True,auto_columns=True,column_percentage=50,var=1,var_percentage=70):
    ada=AdaForest()
    df=first_weights(df,auto=auto,var=var,var_percentage=var_percentage)
    for i in range(stumps):
        print(i,'stump')
        time1=time.perf_counter()
        stump,df=build_stump(df,auto_columns,column_percentage)
        time2=time.perf_counter()
        print(f'__________________STUMP IN {round(time2-time1,2)} SECONDS____________________')
        ada.add_stump(stump)
    return ada
    
def Ada_predict_row(row,adaforest,auto=True,var=1,limite=70):
    size=adaforest.size()
    ones=0 #guardando o a_say das previsões de 1
    zeros=0  #guardando o a_say das previsões de 1
    for i in range(size):
        stump=adaforest.get_stump(i)
        q=stump.question
        if q.match(row):
            if stump.true_branch.var==1:
                ones+=stump.a_of_say
            else:
                zeros+=stump.a_of_say
        else:
            if stump.false_branch.var==1:
                ones+=stump.a_of_say
            else:
                zeros+=stump.a_of_say
    if auto:
        if ones>zeros:
            return 1
        else:
            return 0
    else:
        if var==1:
            if round(100*(ones/(zeros+ones)),2)>=limite:
                return 1
            else:
                return 0
        elif var==0:
            if round(100*(zeros/(zeros+ones)),2)>=limite:
                return 0
            else:
                return 1
            
            
def Ada_predict(df,adaforest,auto=True,var=1,limite=70):
    size1=len(df.index)
    predictions=[]
    for i in range(size1):
        print(i)
        row=pd.DataFrame(df.iloc[i,:]).T
        pred=Ada_predict_row(row,adaforest,auto=auto,var=var,limite=limite)
        predictions+=[pred]
    return predictions


# #   #  #  #  # FUNÇÕES PARA A CMAT #  #  #  #   #   #   #   #   #  #  #  #  # #  #  #  #  #  #  #  #  #  # #  #   #
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
#  #  # #  # # #  # # #  # # # #  # ##  # #  # # # # #   # #  #  #  ##   #   # #  #   #   #  #   #    #   #   #   #   #   

def Ada_cmat(df,adaforest,auto=False,var=1,limite=60):
    real=list(df.iloc[:,-1]) #VERIFICAR, mas como adicionamos as colunas dos pesos nas funções, as df original fica igual
    predicted=Ada_predict(df,adaforest,auto=auto,var=var,limite=limite)
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

#  #  #  # #  #  #  #  # Funções para vizualisar a Ada_Forest

def Q_info(adaforest,names=False,df=None):
    #devolve os a_of_say,tipo, coluna e valores de cada pergunta (com o seu índice)
    size= adaforest.size()
    info=[]
    for i in range(size):
        stump=adaforest.get_stump(i)
        if names: #dá nos o nome das colunas em vez do índice
            coluna=df.columns[stump.question.column]
        else:
            coluna=stump.question.column
        info+=[[i,stump.a_of_say,coluna,stump.question.tipo,stump.question.value1,stump.question.value2]]
    return info

def used_columns(adaforest,names=False,df=None):
    #dá um dicionário com as vezes que cada coluna foi usada
    dic={}
    if names: #se tivermos df, temos todas as colunas no dic
        for c in df.columns:
            dic[c]=0
    size= adaforest.size()
    for i in range(size):
        stump=adaforest.get_stump(i)
        if names: #dá nos o nome das colunas em vez do índice
            coluna=df.columns[stump.question.column]
        else:
            coluna=stump.question.column
        if coluna not in dic:
            dic[coluna]=0
        dic[coluna]+=1
    return dic


# --------- Old_Stuff
    
#def oldAda_best_stump(df): #NOTA, esta função apenas serve para ADABOOST, não tem random de colunas
#    #ou de amostras, para fazer Random_Forest
#    Err=1
#    best_question=None
#    boly=None
#    columns=len(df.columns)
#    ind=[]
#    for i in range(columns-2): #a última coluna são os pesos e a -2 as var. dep
#        #print(i,'coluna')
#        if len(var_values(df,i))==1:
#            continue
#        #q, b, erro=Ada_best_column_question(df,i)
#        #if erro <= Err
#        #    best_question,boly, Err = q, b, erro
#        ind+=[i]
#    print('Going multi_columns')
#   best_question, boly, Err=multi_columns(df,ind)
#    #print(best_question.column,best_question.value1,best_question.value2,best_question.tipo)
#    return best_question, boly, Err
    
#def Oldchoose_correct(t,f): #escolhe qual das folhas do stump prevê 1 e qual prevê 0
#    cc1=time.perf_counter()
#    #devolve boleano, erro menor
#    #True se true_rows prever 1
#    #False se true_rows prever 0
#    #caso 1, true->1  false->0
#    #caso 2, true->0  false->1
#    #t,f=partition(df,question)
#    sizef=len(f.index)
#    sizet=len(t.index)
#    erro1=0  #caso 1, true->1  false->0
#    erro2=0  #caso 2, true->0  false->1
#    for i in range(sizet):
#        if t.iloc[i][-2]==0:
#            erro1+=t.iloc[i][-1]
#        else:
#            erro2+=t.iloc[i][-1]
#    for n in range(sizef):
#        if f.iloc[n][-2]==1:
#            erro1+=f.iloc[n][-1]
#        else:
#            erro2+=f.iloc[n][-1]
#    #print(erro1,erro2)   
#    cc2=time.perf_counter()    
#    print(f'choose_correct in {round(cc2-cc1,2)} seconds')
#    if erro1>=erro2:
#        return False,erro2
#    else:
#        return True,erro1
    
#aux right_wrong #  # #  #
#def rw_aux(l,ind,question,boly): 
#    if question.match(l): #True
#        if ind==1:
#            if boly:
#                return 'R'
#            else:
#                return 'W'
#        else:
#            if boly:
#                return 'W'
#            else:
#                return 'R'
#    else:
#        if ind==1:
#            if boly:
#                return 'W'
#            else:
#                return 'R'
#        else:
#            if boly:
#                return 'R'
#            else:
#                return 'W'

# #  #  # # #  #  # # # # #  # #  # #  # #  # # # # # # ##

#def old_right_wrong(df,question,boly):
#    l=[pd.DataFrame(df.iloc[i,:]).T for i in range(len(df.index))]
#    ind=[df.iloc[i][-2] for i in range(len(df.index))]
#    qu=[question]*len(ind)
#    bol=[boly]*len(ind)
#    rw=list(executor.map(rw_aux,l,ind,qu,bol))            
#    return rw     
