print('Which Leagues?')
print('(all -> All the Leagues || done -> No more Leagues)')
leagues_aux = 0
leagues_aux2 = 0 #serve para não ter de fazer raise quando me engano no input
leagues_add = []
while leagues_aux not in ['all','done']:
    if (leagues_aux!=0) and (leagues_aux2!=1):
        leagues_add+=[leagues_aux]
    print(['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A'])
    leagues_aux = str(input('--------->'))
    if (leagues_aux in leagues_add) and (leagues_aux not in ['all','done']) and (leagues_aux not in ['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A']):
    	print('Argument not valid')
    	leagues_aux2 = 1

if leagues_aux=='all':
	leagues = ['Premier_League','Bundesliga','Ligue_1','La_Liga','Serie_A']
else:
	leagues = leagues_add

print(leagues,'L')
