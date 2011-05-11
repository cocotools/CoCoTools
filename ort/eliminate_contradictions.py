from __future__ import print_function

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
        self.bad_edges = set()

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

    def keep_track_of_edges_to_remove(self, others):
        """Mark edges responsible for a contradiction for removal.

        First, we remove the edges between self.region and each other. This,
        however, is not enough. Stephan et al. fail to note that we must also
        remove all of the edges that depend on these edges (i.e., that have one
        of these edges in their tpath).

        It is a shame to have to remove these extra edges, because they may be
        supported by other connections that still exist in our graph. In order
        to see these other supports, however, we would need to keep track of
        all possible tpaths in the deduce_rcs script. So far, we have not
        implemented this level of note-taking.

        Because there is potential tpath-asymmetry, however, we'll only remove
        a symmetrical pair of edges if both tpaths depend on the edges removed
        between other and self.region. If only one tpath depends on the removed
        edges, we'll change this tpath to equal the reverse of the
        non-dependent tpath.

        Parameters
        ----------
        others : list
          List of nodes all from the same brain map.
        """
        for other in others:

            self.bad_edges.add((self.region, other))
            self.bad_edges.add((other, self.region))

            for source, target in self.map_g.edges_iter():

                #Keep track of dependent edges with variable bad.
                bad = []

                #See whether (other, self.region) or (self.region, other)
                #is in either of source <--> target's tpaths.
                tpath1 = self.map_g[source][target]['tpath']
                tpath2 = self.map_g[target][source]['tpath']

                if (tpath1 == [self.region, other] or
                    tpath1 == [other, self.region]):
                    bad.extend([source, target])
                elif self.region in set(tpath1):

                    #We need to see whether the region in tpath1 after or
                    #before self.region is other. But we need to handle the
                    #possibility that self.region is the first or last
                    #region in tpath.
                    try:
                        if tpath1[tpath1.index(self.region)+1] == other:
                            bad.extend([source, target])
                    except IndexError:
                        pass
                    try:
                        if tpath1[tpath1.index(self.region)-1] == other:
                            bad.extend([source, target])
                    except IndexError:
                        pass
                else:
                    pass
                
                if (tpath2 == [self.region, other] or
                    tpath2 == [other, self.region]):
                    bad.extend([target, source])
                elif self.region in set(tpath2):

                    try:
                        if tpath2[tpath2.index(self.region)+1] == other:
                            bad.extend([target, source])
                    except IndexError:
                        pass
                    try:
                        if tpath2[tpath2.index(self.region)-1] == other:
                            bad.extend([target, source])
                    except IndexError:
                        pass
                else:
                    pass

                if len(bad) > 4:
                    raise ValueError, 'definition of bad is erroneous'

                if len(bad) == 2:
                    #The reverse of the bad edge has a non-dependent tpath.
                    #gp stands for good path.
                    gp = copy.deepcopy(self.map_g[bad[1]][bad[0]]['tpath'])

                    gp.reverse()

                    #Set the dependent tpath to be the reverse of the good
                    #one.
                    self.map_g[bad[0]][bad[1]]['tpath'] = gp

                elif len(bad) == 4:
                    #Both edges are dependent -- gotta remove 'em.
                    self.bad_edges.add((source, target))
                    self.bad_edges.add((target, source))

                else:
                    pass

    def handleS(self, others, rcs):
        """
        """
        #Locate the Ss in rcs.
        start = 0
        badSs = []
        for time in range(rcs.count('S')):
            index = rcs.index('S', start)
            tpath = self.map_g[self.region][others[index]]['tpath']
            d = Deducer(self.map_g)
            #If this S is of category 2, keep it and remove the other edges.
            if fin_autom(d.get_word(tpath)) == 2:
                others.pop(index)
                self.keep_track_of_edges_to_remove(others)
                break
            start = rcs.index('S', start) + 1
            badSs.append(others[index])

        #If we didn't break, we didn't find an S of category 2. So we'll remove
        #the Ss.
        else:
            self.keep_track_of_edges_to_remove(badSs)

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
        d = Deducer(self.map_g)
        for time in range(rcs.count('S')):
            index = rcs.index('S', start)
            tpath = self.map_g[others[index]][self.region]['tpath']
            #If this S is of category 2, remove the Ls and keep everything
            #else.
            if fin_autom(d.get_word(tpath)) == 2:
                self.keep_track_of_edges_to_remove(Ls)
                break
            start = rcs.index('S', start) + 1

        #If no Ss of category 2, see whether there are any Ls of category 3. If
        #so, keep that L and remove everything else.
        else:
            for Lindex in Lindices:
                tpath = self.map_g[others[Lindex]][self.region]['tpath']
                if fin_autom(d.get_word(tpath)) == 3:
                    others.pop(Lindex)
                    self.keep_track_of_edges_to_remove(others)
                    break

            #If no Ls of category 3, remove all the Ls and keep everything
            #else.
            else:
                self.keep_track_of_edges_to_remove(Ls)

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
                self.keep_track_of_edges_to_remove(others)

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
        count = 0
        for region in self.map_g:
            self.region = region
            self.blank = 'to'
            self.eliminate_contradiction(self.contradictory_paths())

            self.blank = 'from'
            self.eliminate_contradiction(self.contradictory_paths())

            count += 1
            print('Eliminate: %d/%d' % (count, len(self.map_g)))
        self.map_g.remove_edges_from(self.bad_edges)

#-----------------------------------------------------------------------------
# Test Functions
#-----------------------------------------------------------------------------

def test_remove_edges():
    fake_map_g = nx.DiGraph()
    #Contradictions will be in A-1 <--> B-1 and A-1 <--> B-2.
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='L')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='S')
    fake_map_g.add_edge('A-1', 'B-2', tpath=['A-1', 'B-2'], RC='O')
    fake_map_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'], RC='O')
    fake_map_g.add_edge('A-1', 'B-3', tpath=['A-1', 'B-3'], RC='I')
    fake_map_g.add_edge('B-3', 'A-1', tpath=['B-3', 'A-1'], RC='I')

    #Make dependent edges between C-1 and D-1.
    fake_map_g.add_edge('C-1', 'D-1', RC='L',
                        tpath=['C-1', 'A-1', 'B-1', 'D-1'])
    fake_map_g.add_edge('D-1', 'C-1', RC='S',
                        tpath=['D-1', 'B-1', 'A-1', 'C-1'])

    #Make just one dependent edge between A-1 and E-1.
    fake_map_g.add_edge('A-1', 'E-1', RC='O', tpath=['A-1', 'B-2', 'E-1'])
    fake_map_g.add_edge('E-1', 'A-1', RC='O', tpath=['E-1', 'A-1'])

    #Make the rest of the edges that are needed to support the dependent edges.
    fake_map_g.add_edge('C-1', 'A-1', RC='I', tpath=['C-1', 'A-1'])
    fake_map_g.add_edge('A-1', 'C-1', RC='I', tpath=['A-1', 'C-1'])
    fake_map_g.add_edge('B-1', 'D-1', RC='I', tpath=['B-1', 'D-1'])
    fake_map_g.add_edge('D-1', 'B-1', RC='I', tpath=['D-1', 'B-1'])
    fake_map_g.add_edge('B-2', 'E-1', RC='I', tpath=['B-2', 'E-1'])
    fake_map_g.add_edge('E-1', 'B-2', RC='I', tpath=['E-1', 'B-2'])

    desired_g = copy.deepcopy(fake_map_g)

    e = Eliminator(fake_map_g)
    e.region = 'A-1'
    e.keep_track_of_edges_to_remove(['B-1', 'B-2'])

    desired_g['A-1']['E-1']['tpath'] = ['A-1', 'E-1']

    nt.assert_equal(e.map_g.edge, desired_g.edge)
    nt.assert_equal(e.bad_edges, set([('A-1', 'B-1'), ('B-1', 'A-1'),
                                      ('A-1', 'B-2'), ('B-2', 'A-1'),
                                      ('C-1', 'D-1'), ('D-1', 'C-1')]))

def test_iterate_nodes():
    #See third block of text in Appendix J.
    fake_map_g = nx.DiGraph()
    fake_map_g.add_edge('A-1', 'B-1', tpath=['A-1', 'B-1'], RC='L')
    fake_map_g.add_edge('B-1', 'A-1', tpath=['B-1', 'A-1'], RC='S')
    fake_map_g.add_edge('A-1', 'B-2', tpath=['A-1', 'B-2'], RC='O')
    fake_map_g.add_edge('B-2', 'A-1', tpath=['B-2', 'A-1'], RC='O')
    fake_map_g.add_edge('A-1', 'B-3', tpath=['A-1', 'B-3'], RC='I')
    fake_map_g.add_edge('B-3', 'A-1', tpath=['B-3', 'A-1'], RC='I')

    e = Eliminator(fake_map_g)

    desired_g = copy.deepcopy(fake_map_g)

    e.iterate_nodes()
    
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

    e2.iterate_nodes()

    desired_g2.remove_edges_from([('A-1', 'B-2'), ('B-2', 'A-1')])

    nt.assert_equal(e2.map_g.edge['A-1'], desired_g2.edge['A-1'])

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

    e.iterate_nodes()

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

    
