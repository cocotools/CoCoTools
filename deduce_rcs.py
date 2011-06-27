"""Deduce inter-map relations unstated in the literature.

1) A big question concerns how to deal with nodes within a single map that
cover the same space on standard cortex. ORT assumes that each map specifies a
set of regions that are mutually exclusive and collectively exhaustive in their
coverage of brain space; however, many maps defined supraregions that contain
sub-regions.

For now we are pretending this issue doesn't exist (as Stephan et al.
implicitly do).

2) For an unknown reason, the output of this graph is not necessarily
symmetrical: i.e., the existence of map_g[A-1][B-1] does not imply the
existence ofmap_g[B-1][A-1], as it should.

My guess is that this error has its source in the definition of the FA, as an
asymmetry error has already been linked to a bad FA definition (the correction
of which is documented in the function fin_autom).
"""

import networkx as nx
import nose.tools as nt
import copy

#------------------------------------------------------------------------------
#Class Definitions
#------------------------------------------------------------------------------

class Deducer(object):
    def __init__(self, map_g):
        """The mapping graph (map_g) submitted to Deducer must have the
        following property:

        i) If map_g[A-1][B-1] exists, then map_g[B-1][A-1] exists.

        ii) Each edge must have attributes 'RC' and 'tpath'.
        """
        self.map_g = map_g

    def get_word(self, tpath):
        """Given a tpath, return corresponding transformation path code.

        Parameters
        ----------
        tpath : list
          List of regions that form chain from the first region in the list to
          the last, allowing an edge between the two.

        Returns
        -------
        word : string
          Concatenated RCs describing relations of the tpath, also called the
          transformation path code.
        """
        from_, to = 0, 1
        word = ''
        while to < len(tpath):
            word += self.map_g[tpath[from_]][tpath[to]]['RC']
            from_ += 1
            to += 1
        return word

    def handle_new_edge(self, aff, node, eff):
        """Add edge from aff to eff if it would be valid.

        Requirements for validity are i) all regions in the new edge's tpath
        must be from different maps and ii) the tpath's word must fall in a
        valid path category.

        Stephan et al. state that the word for an edge, in addition to its
        transformation path, should be stored with the edge. However, because
        a word can be looked up easily given an edge's transformation path (see
        self.get_word), we store only the transformation path.

        We use the transformation path category hierarchy to optimize edges.
        Another possibility we don't implement is the use of PD codes (see
        Appendix I).

        Parameters
        ----------
        aff : string
          One of node's currently existing afferents.
          
        node : string
          Node from self.map_g currently being processed.

        eff : string
          One of node's currently existing efferents.

        Returns
        -------
        None
          Potentially adds or changes an edge in self.map_g.
        """
        new_tpath = self.map_g[aff][node]['tpath'] + \
                    self.map_g[node][eff]['tpath'][1:]

        new_category = fin_autom(self.get_word(new_tpath))
        
        if no_tpath_dups(new_tpath) and new_category:
            if (aff, eff) in self.map_g.edges_iter():
                if (new_category <
                    fin_autom(self.get_word(self.map_g[aff][eff]['tpath']))):
                    self.map_g[aff][eff]['tpath'] = new_tpath
            else:
                self.map_g.add_edge(aff, eff, tpath=new_tpath,
                                    RC=self.determine_rc_res(new_tpath))
        
    def process_node(self, node):
        """Try to make edges from node's afferents to its efferents.

        Parameters
        ----------
        node : string
          Node from self.map_g currently being processed.

        Returns
        -------
        None
          Calls self.handle_new_edge, which potentially changes self.map_g.
        """
        for afferent in self.map_g.predecessors(node):
            for efferent in self.map_g.successors(node):
                if afferent.split('-')[0] != efferent.split('-')[0]:
                    self.handle_new_edge(afferent, node, efferent)

    def iterate_nodes(self):
        """Perform deduction process for each node in self.map_g.

        Parameters
        ----------
        None

        Returns
        -------
        None
          Valid deduced edges are added to self.map_g.
        """
        for node in self.map_g:
            self.process_node(node)

    def determine_rc_res(self, tpath):
        """Given a tpath's category, return its RC_res.

        See Appendix E. My code here assumes that a transformation path from A
        to B exists if and only if there is an edge in self.map_g from A to B.
        It also assumes that we are working with a sufficiently large base of
        relational information on all of the involved maps. When the latter
        assumption totally fails, assume RC='O', per Stephan et al.

        Parameters
        ----------
        path_category : int
          Category to which fin_autom assigned this edge's tpath.

        Returns
        -------
        string
          RC_res for the edge.
        """
        rules = {1: 'I', 2: 'S', 3: 'L', 5: 'O'}

        if fin_autom(self.get_word(tpath)) != 4:
            return rules[fin_autom(self.get_word(tpath))]

        #I know what follows is *ugly*, but the logic is complicated and I
        #couldn't think of a clean way to write it.
        if ([reg for reg in self.map_g.successors(tpath[0]) if
            fin_autom(self.get_word(self.map_g[tpath[0]][reg]['tpath'])) in
            (3, 5) and reg != tpath[-1] and reg.split('-')[0] ==
            tpath[-1].split('-')[0]] and not [reg for reg in
            self.map_g.successors(tpath[-1]) if reg != tpath[0] and
            reg.split('-')[0] == tpath[0].split('-')[0]]):
            return 'L'

        if ([reg for reg in self.map_g.predecessors(tpath[-1]) if
            fin_autom(self.get_word(self.map_g[reg][tpath[-1]]['tpath'])) in
            (2, 5) and reg != tpath[0] and reg.split('-')[0] ==
            tpath[0].split('-')[0]] and not [reg for reg in
            self.map_g.predecessors(tpath[0]) if reg != tpath[-1] and
            reg.split('-')[0] == tpath[-1].split('-')[0]]):
            return 'S'

        if ([reg for reg in self.map_g.predecessors(tpath[-1]) if
            fin_autom(self.get_word(self.map_g[reg][tpath[-1]]['tpath'])) in
            (2, 5) and reg != tpath[0] and reg.split('-')[0] ==
            tpath[0].split('-')[0]] and [reg for reg in
            self.map_g.predecessors(tpath[0]) if
            fin_autom(self.get_word(self.map_g[reg][tpath[0]]['tpath'])) in
            (2, 5) and reg != tpath[-1] and reg.split('-')[0] ==
            tpath[-1].split('-')[0]] and not [reg for reg in
            self.map_g.successors(tpath[0]) if
            fin_autom(self.get_word(self.map_g[tpath[0]][reg]['tpath'])) in
            (1, 2) and reg != tpath[-1] and reg.split('-')[0] ==
            tpath[-1].split('-')[0]]):
            return 'O'

        #If all of the previous conditionals failed, we don't have enough
        #information about the maps to resolve this relation. Per Stephan et
        #al., adopt a worst-case behavior and assume RC='O'.
        return 'O'

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def no_tpath_dups(tpath):
    """Return True if no regions with same map in tpath, False otherwise.

    Parameters
    ----------
    tpath : list
      Chain of regions each with a known relation to the region in front of and
      behind it in the list.

    Returns
    -------
    True or False : boolean
      Indicates whether every region in the tpath is from a unique map.
    """
    map_list = []
    
    for region in tpath:
        map_list.append(region.split('-')[0])

    for map in map_list:
        if map_list.count(map) > 1:
            break
        
    else:
        return True    

    return False

def fin_autom(word):
    """Given a transformation path code (i.e., word), return its path category.

    According to Stephan et al., 'OS' is assigned to path category 0 (i.e.,
    invalid), whereas 'LO', the reverse of 'OS', is considered valid (category
    4). On first glance, this asymmetry seems wrong.

    Further analysis demonstrates its incorrectness: There is no way to draw
    three regions A, B, and C with RCs (A,B)='O' and (B,C)='S' such that A and
    C are disjoint.

    To remediate this apparent error in Stephan et al's definition, I have
    changed delta['S'][5] from 0 to 4.

    Parameters
    ----------
    word : string
      Concatenated RCs from a tpath -- also known as a transformation path
      code.

    Returns
    -------
    state : int
      Path category of the word (1-5 are valid, 0 is invalid).
    """
    delta = {'I': {'START': 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 0: 0},
             'S': {'START': 2, 1: 2, 2: 2, 3: 4, 4: 4, 5: 4, 0: 0},
             'L': {'START': 3, 1: 3, 2: 0, 3: 3, 4: 0, 5: 0, 0: 0},
             'O': {'START': 5, 1: 5, 2: 0, 3: 4, 4: 0, 5: 0, 0: 0}
             }
    state = 'START'
    for letter in word:
        state = delta[letter][state]
    if state == 'START':
        state = 0
    return state
