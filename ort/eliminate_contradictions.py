import copy

import nose.tools as nt
import networkx as nx

from deduce_rcs import Deducer, fin_autom

#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------

class Eliminator(object):
    def __init__(self, map_g):
        """Takes output of deduce_rcs and eliminates contradictory paths.

        Parameters
        ----------
        map_g : DiGraph instance
          Output of deduce_rcs.
        """
        self.map_g = map_g
        self.region = ''
        self.blank = ''

    def paths_blank_same_map(self):
        """
        """
        if self.blank == 'to':
            others = self.map_g.successors(self.region)
        elif self.blank == 'from':
            others = self.map_g.predecessors(self.region)
        else:
            raise ValueError, 'self.blank must be "from" or "to"'
        
        paths_dict = {}
        for other in others:
            if other.split('-')[0] == self.region.split('-')[0]:
                raise ValueError, 'bug in deduce_rcs: edge within a single map'
            if other.split('-')[0] in paths_dict:
                paths_dict[other.split('-')[0]].append(other)
            else:
                paths_dict[other.split('-')[0]] = [other]
        return paths_dict

    def contradictory_paths(self):
        """
        """
        for reg_same_map in self.paths_blank_same_map().values():
            rcs = [self.map_g[self.region][targ]['RC'] for targ in
                   reg_same_map]
            if len(rcs) > 1:
                if self.blank == 'to' and ('I' in rcs or 'S' in rcs):
                    return reg_same_map, rcs
                if self.blank == 'from' and ('I' in rcs or 'L' in rcs):
                    return reg_same_map, rcs
        return False

    def remove_edges(self, others):
        """For each node in a list, remove edges between it and self.region

        Parameters
        ----------
        others : list
          List of nodes all from the same brain map.
        """
        for other in others:
            self.map_g.remove_edge(self.region, other)
            self.map_g.remove_edge(other, self.region)
 
    def handleS(self, others, rcs):
        """
        """
        #Locate the Ss in rcs.
        start = 0
        badSs = []
        for time in range(rcs.count('S')):
            index = rcs.index('S', start)
            tpath = self.map_g[self.region][others[index]]['tpath']
            d = Deducer(self.map_g, done_previously='yes')
            #If this S is of category 2, keep it and remove the other edges.
            if fin_autom(d.get_word(tpath)) == 2:
                others.pop(index)
                self.remove_edges(others)
                break
            start = rcs.index('S', start) + 1
            badSs.append(others[index])

        #If we didn't break, we didn't find an S of category 2. So we'll remove
        #the Ss.
        else:
            self.remove_edges(badSs)

    def handleL(self, others, rcs):
        """
        """
        #Locate the Ls in rcs.
        start = 0
        Lindices = []
        for time in range(rcs.count('L')):
            Lindices.append(rcs.index('L', start))
            start = rcs.index('L', start) + 1
        Ls = [others[Lindex] for Lindex in Lindices]
        
        #Locate the Ss in rcs.
        start = 0
        d = Deducer(self.map_g, done_previously='yes')
        for time in range(rcs.count('S')):
            index = rcs.index('S', start)
            tpath = self.map_g[others[index]][self.region]['tpath']
            #If this S is of category 2, remove the Ls and keep everything
            #else.
            if fin_autom(d.get_word(tpath)) == 2:
                self.remove_edges(Ls)
                break
            start = rcs.index('S', start) + 1

        #If no Ss of category 2, see whether there are any Ls of category 3. If
        #so, keep that L and remove everything else.
        else:
            for Lindex in Lindices:
                tpath = self.map_g[others[Lindex]][self.region]['tpath']
                if fin_autom(d.get_word(tpath)) == 3:
                    others.pop(Lindex)
                    self.remove_edges(others)
                    break

            #If no Ls of category 3, remove all the Ls and keep everything
            #else.
            else:
                self.remove_edges(Ls)

    def eliminate_contradiction(self, contradictory_paths):
        """
        """
        #contradictory_paths exists iff (self.blank == 'to' and I or S in rcs)
        #or (self.blank == 'from' and I or L in rcs).
        if contradictory_paths:
            others, rcs = contradictory_paths
            #If there's an I, keep it and remove everything else.
            if 'I' in rcs:
                others.pop(rcs.index('I'))
                self.remove_edges(others)

            #There's no I. If self.blank == to, there must be at least one S.
            #Keep an S of category 2 if one exists and remove everything else;
            #otherwise remove all Ss and keep everything else.
            elif self.blank == 'to':
                self.handleS(others, rcs)

            #If self.blank == from, there must be at least one L. If there is
            #an S of category 2, remove all the Ls and keep everything else.
            #If not, but there is an L of category 3, keep that L and remove
            #everything else. If neither of these cases, remove all the Ls and
            #keep everything else.
            elif self.blank == 'from':
                self.handleL(others, rcs)

            else:
                raise ValueError, 'self.blank must be "from" or "to"'
                
    def iterate_nodes(self):
        """
        """
        for region in self.map_g:
            self.region = region
            self.blank = 'to'
            self.eliminate_contradiction(self.contradictory_targets())

            self.blank = 'from'
            self.eliminate_contradiction(self.contradictory_targets())

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

def test_iterate_nodes():
    pass

def test_eliminate_contradiction():
    #See third block of text in Appendix J.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='L')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='S')
    fake_map_g.add_edge('A-1', 'B-2', tpath=['A-1', 'B-2'], RC='O')
    fake_map_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'], RC='O')
    fake_map_g.add_edge('A-1', 'B-3', tpath=['A-1', 'B-3'], RC='I')
    fake_map_g.add_edge('B-3', 'A-1', tpath=['B-3', 'A-1'], RC='I')

    e = Eliminator(fake_map_g)
    e.region = 'A-1'
    e.blank = 'to'

    desired_g = copy.deepcopy(fake_map_g)

    e.eliminate_contradiction((['B-1', 'B-2', 'B-3'], ['L', 'O', 'I']))
    
    desired_g.remove_edges_from([('A-1', 'B-1'), ('A-1', 'B-2'),
                                 ('B-1', 'A-1'), ('B-2', 'A-1')])
    
    nt.assert_equal(e.map_g.edge, desired_g.edge)

    #Test that second conditional works.
    fake_map_g2 = nx.DiGraph()
    fake_map_g2.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='S')
    fake_map_g2.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='L')
    fake_map_g2.add_edge('A-1', 'B-2', tpath=['A-1', 'C-1', 'D-1', 'B-2'],
                         RC='S')
    fake_map_g2.add_edge('B-2', 'A-1', tpath=['B-2', 'D-1', 'C-1', 'A-1'],
                         RC='L')
    fake_map_g2.add_edge('A-1', 'C-1', tpath=['A-1', 'C-1'], RC='I')
    fake_map_g2.add_edge('C-1', 'A-1', tpath=['C-1', 'A-1'], RC='I')
    fake_map_g2.add_edge('C-1', 'D-1', tpath=['C-1', 'D-1'], RC='L')
    fake_map_g2.add_edge('D-1', 'C-1', tpath=['D-1', 'C-1'], RC='S')
    fake_map_g2.add_edge('D-1', 'B-2', tpath=['D-1', 'B-2'], RC='S')
    fake_map_g2.add_edge('B-2', 'D-1', tpath=['B-2', 'D-1'], RC='L')

    e2 = Eliminator(fake_map_g2)
    e2.region = 'A-1'
    e2.blank = 'to'

    desired_g2 = copy.deepcopy(fake_map_g2)

    e2.eliminate_contradiction((['B-1', 'B-2'], ['S', 'S']))

    desired_g2.remove_edges_from([('A-1', 'B-2'), ('B-2', 'A-1')])

    nt.assert_equal(e2.map_g.edge, desired_g2.edge)

    #Test that third conditional works.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'C-1', 'B-1'], RC='L')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'C-1', 'A-1'], RC='S')
    fake_map_g.add_edge('A-2', 'B-1', tpath=['A-2', 'B-1'], RC='O')
    fake_map_g.add_edge('B-1', 'A-2', tpath=['B-1', 'A-2'], RC='O')
    fake_map_g.add_edge('A-3', 'B-1', tpath=['A-3', 'B-1'], RC='O')
    fake_map_g.add_edge('B-1', 'A-3', tpath=['B-1', 'A-3'], RC='O')
    fake_map_g.add_edge('A-1', 'C-1', tpath=['A-1', 'C-1'], RC='L')
    fake_map_g.add_edge('C-1', 'A-1', tpath=['C-1', 'A-1'], RC='S')
    fake_map_g.add_edge('C-1', 'B-1', tpath=['C-1', 'B-1'], RC='O')
    fake_map_g.add_edge('B-1', 'C-1', tpath=['B-1', 'C-1'], RC='O')

    e = Eliminator(fake_map_g)
    e.region = 'B-1'
    e.blank = 'from'

    desired_g = copy.deepcopy(fake_map_g)

    e.eliminate_contradiction((['A-1', 'A-2', 'A-3'], ['L', 'O', 'O']))

    desired_g.remove_edges_from([('A-1', 'B-1'), ('B-1', 'A-1')])

    nt.assert_equal(e.map_g.edge, desired_g.edge)

def test_paths_blank_same_map():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='S')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='L')
    fake_map_g.add_edge('A-1', 'B-2', tpath=['A-1', 'B-2'], RC='S')
    fake_map_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'], RC='L')
    fake_map_g.add_edge('A-2', 'B-1', tpath=['A-2', 'B-1'], RC='S')
    fake_map_g.add_edge('B-1', 'A-2', tpath=['B-1', 'A-2'], RC='L')

    e = Eliminator(fake_map_g)
    e.region = 'A-1'
    e.blank = 'to'

    nt.assert_equal(e.paths_blank_same_map(), {'B': ['B-2', 'B-1']})

    e.region = 'B-1'
    e.blank = 'from'
    nt.assert_equal(e.paths_blank_same_map(), {'A': ['A-1', 'A-2']})

def test_contradictory_paths():
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='I')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='I')
    fake_map_g.add_edge('A-1', 'B-2', tpath=['A-1', 'B-2'], RC='S')
    fake_map_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'], RC='L')

    e = Eliminator(fake_map_g)
    e.region = 'A-1'
    e.blank = 'to'

    nt.assert_equal(e.contradictory_paths(), (['B-2', 'B-1'], ['S', 'I']))

    e.region = 'B-1'
    e.blank = 'to'
    nt.assert_false(e.contradictory_paths())

    
