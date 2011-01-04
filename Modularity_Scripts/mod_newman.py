#!/usr/bin/python

""" Creates a graph from a nodes text file and an edges text file.
Also implements Newman's community detection algorithm
(see Newman, MEJ, 2006, PNAS 103(23):8577-8582).
Original script contributed in ticket #158 in NetworkX Developer Zone."""

import networkx as nx
import numpy as np
import make_graph as mg
from numpy import linalg as LA

## FUNCTIONS ##

#COMPUTE ONE ELEMENT OF B (MODULARITY MATRIX) FROM EQUATION 3
def bg(g,i,j,nbunch):
  def a(i,j):
    if j in g.neighbors(i): return 1
    else: return 0
  def b(i,j):
    m = len(g.edges())
    return (a(i,j) - 1.0*g.degree(i)*g.degree(j)/(2*m))
  if i == j and len(nbunch) < len(g):
    return b(i,j) - sum([b(i,k) for k in nbunch])
  else:
    return b(i,j)

#PERFORM VARIATION ON K-L ALGORITHM FROM PAGE 8580
def klRefine(s,B):
  def flip(v,pos):
    newv = v.copy()
    newv[pos] = -1*v[pos]
    return newv 
  def dQ(s2):
    return np.dot(np.dot(s2,B),s2) 
  sBest = s
  dQBest = dQ(sBest)
  while True:
    trials = [dQ(flip(sBest,i)) for i in range(len(sBest))]
    if max(trials) > dQBest:
      i = trials.index(max(trials))
      sBest = flip(sBest,i)
      dQBest = dQ(sBest)
    else:
      break
  return sBest

#TRY TO SPLIT INTO TWO BEST COMMUNITIES
def split(g,nbunch,errorMargin=100,doKL=True):
  B = np.array([[bg(g,i,j,nbunch) for j in nbunch] for i in nbunch])
  w,v = LA.eigh(B)
  nb1 = []
  nb2 = []
  i = list(w).index(max(w))
  s = np.array([(1 if x > 0 else -1) for x in v[:,i]])
  dQ = np.dot(np.dot(s,B),s)/(4*len(g.edges()))
  if dQ <= errorMargin*np.finfo(np.double).eps:
    return False 
  if doKL:
    s = klRefine(s,B)
    dQ = np.dot(np.dot(s,B),s)/(4*len(g.edges()))
  global Q
  Q += dQ
  for j in range(len(s)):
    if s[j] < 0:
      nb1.append(nbunch[j])
    else:
      nb2.append(nbunch[j])
  return (nb1,nb2)

#TRY TO SPLIT THE RESULTANT COMMUNITIES FURTHER
def recursive(g,nbunch):
  nb = split(g,nbunch)
  if not nb:
    global resultList
    resultList.append(nbunch)
    return
  else:
    recursive(g,nb[0])
    recursive(g,nb[1])

#RETURN THE FINAL Q (MODULARITY VALUE) WITH THE COMMUNITIES
#AND THEIR MEMBERS
def detect_communities(g):
  global resultList
  resultList = []
  global Q
  Q = 0
  recursive(g,g.nodes())  

##RUN IT##

detect_communities(mg.make_graph())

##MAKE PRETTY RESULTS FILE##

results = open(str(raw_input('Enter name for results file: ')), 'w')

results.write('Newman 2006 Modularity Results for {0}\n\n'.format(str(raw_input('Enter edges file again: '))))

results.write('Q = {0}\n\n'.format(Q))

for x in range(len(resultList)):
  results.write('Community #'+str(x+1)+':\n')
  for y in range(len(resultList[x])):
    results.write(str(resultList[x][y])+'\n')
  results.write('\n')
