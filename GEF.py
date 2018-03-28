import sys
from pulp import *
import numpy as np

def Dia(g):
    return max([aff[i, j] for i in g for j in g])

def LP(g):
    return max([skills[i]-skills[j] for i in g for j in g])

def sumLP(g):
    return sum([LP(c) for c in g])

def sumDia(g):
    return sum([Dia(c) for c in g])

def convertAFF(Aff,n):
    afflist=[]
    for i in range(0, n):
        for j in range(i,n):
            if i != j:
                afflist.append([i,j,Aff[i,j]])
    return afflist

def convertAFF2(Aff,n,groupAff):
    afflist=[]
    for i in range(0, n):
        for j in range(i+1,n):
            if Aff[i,j] not in groupAff:
                if i !=j:
                    afflist.append([i,j,Aff[i,j]])
    return afflist

def getNext(Aff,k,n,groupAff,boarders):
    if groupAff == []:
        AffList = convertAFF(Aff,n)
        AffList.sort(key=lambda L : L[2],reverse=False)
        boarders = []
        while len(boarders) < k:
            T = AffList.pop(0)
            if boarders == []:
                U = {}
            else:
                U = set().union(*boarders)
            if T[0] not in U and T[1] not in U:
                boarders.append([T[0],T[1]])
                groupAff.append(T[2])
        return [groupAff,boarders]
    else:
        j = 0
        AffList = convertAFF2(Aff,n,groupAff)
        AffList.sort(key=lambda L: L[2], reverse=False)
        while AffList != []:
            T = AffList.pop(0)
            for i in range(0,k):
                if groupAff[i] < T[2]:
                    TemB = boarders.pop(i)
                    TemA = groupAff.pop(i)
                    U = set().union(*boarders)
                    if T[0] not in U and T[1] not in U:
                        groupAff.append(T[2])
                        boarders.append([T[0],T[1]])
                        return [groupAff,boarders]
                    else:
                        groupAff.append(TemA)
                        boarders.append(TemB)
        print('No more Next!')
        return 0



def grouping(people,n,k,Aff,optLP):
    g = []
    for i in range(0,k):
        g.append([])
    groupAff = []
    boarders = []
    while(True):
        [groupAff,boarders] = getNext(Aff,k,n,groupAff,boarders)
        T = set(people)
        for c in boarders:
            T -= set(c)
        T = list(T)
        for j in range(0, k):
            for i in range(0,len(T)):
                if aff[T[0], boarders[j][0]] <= groupAff[j] & aff[T[0], boarders[j][1]] <= groupAff[j]:
                    g[j].append(T[0])
                    T.pop(0)
        print(T)
        if len(T) == 0:
            return [b + c for (b, c) in zip(g, boarders)]
        else:
            g = []
            for i in range(0, k):
                g.append([])

g = grouping(people,n,k,aff,OptLP)


n = 9
k = 3
skills = [np.random.random_integers(1, 100) for i in range(0, n)]
b = np.random.random_integers(1, 100, size=(n, n))
aff = np.tril(b) + np.tril(b, -1).T
np.fill_diagonal(aff, 0)



people = [i for i in range(0,n)]#####Index of each person
rank = list(skills)
rank.sort()
OptLP = sum(rank[(n-k):n]) - sum(rank[0:k])
print("The Optimal learning potential is", OptLP)####optimal overall Learning Potential

possible_groups= []
for size in range(2,n-2*(k-1)+1):
    possible_groups +=[tuple(c) for c in pulp.combination(people,size)]#####All the possible grouping(exponential)

x = pulp.LpVariable.dicts('group', possible_groups,
                            lowBound = 0,
                            upBound = 1,
                            cat = pulp.LpInteger)
######ILP MODEL
Grouping_model = pulp.LpProblem("Grouping Model", pulp.LpMinimize)
Grouping_model += sum([Dia(group) * x[group] for group in possible_groups])
Grouping_model += sum([x[group] for group in possible_groups]) == k
for person in people:
    Grouping_model += sum([x[group] for group in possible_groups
                                if person in group]) == 1, "Must_seat_%s"%person

Grouping_model.solve()
#######

#######Output
sumAff =0
sumLP =0
for group in possible_groups:
    if x[group].value() == 1.0:
        print(group,"Learning Potential is \t",LP(group),"Affinity Diameter is\t",Dia(group))
        sumAff += Dia(group)
        sumLP += LP(group)

print("Over all affinity is",sumAff,"Over all Learning Potential is", sumLP)



sumAff2 = 0

g = grouping(people,n,k,aff,OptLP)
for groups in g:
    sumAff2 += Dia(groups)

print("group_appfinity",sumAff2)
print("group_ratio",sumAff2/sumAff)
