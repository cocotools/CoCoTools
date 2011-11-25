from copy import deepcopy

from numpy import mean, float64
from networkx import DiGraph, NetworkXError

from unittest import TestCase

from mocker import MockerTestCase

from cocotools import ConGraph

#------------------------------------------------------------------------------
# Integration Tests
#------------------------------------------------------------------------------

def test__pick_one_level_of_resolution():
    conn = ConGraph()
    conn.add_edge('A-1', 'B', {'EC_Source': 'X', 'EC_Target': 'X',
                               'PDC_EC_Source': 0, 'PDC_EC_Target': 0,
                               'PDC_Site_Source': 0, 'PDC_Site_Target': 0,
                               
    mapp = mg.MapGraph(conn)
    mapp._pick_one_level_of_resolution('A', 'B', 'I')
    nt.assert_equal(
        
        
class MakeTranslationDictTestCase(TestCase):
    
    def test_diff_map(self):
        m = mg.MapGraph(ConGraph())
        ebunch = [('A-1', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
                  ('A-2', 'B-1', {'TP': [], 'PDC': 0, 'RC': 'S'}),
                  ('A-4', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-4', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-5', 'B-2', {'TP': [], 'PDC': 0, 'RC': 'O'}),
                  ('A-5', 'B-3', {'TP': [], 'PDC': 0, 'RC': 'O'})]
        m.add_edges_from(ebunch)
        self.assertEqual(m._make_translation_dict('A-1', 'B'),
                         {'B-1': {'S': ['A-1', 'A-2'],
                                  'I': [],
                                  'L': [],
                                  'O': []}})

    def test_same_map(self):
        m = mg.MapGraph(ConGraph())
        self.assertEqual(m._make_translation_dict('B-1', 'B'),
                         {'B-1': {'S': [],
                                  'I': ['B-1'],
                                  'L': [],
                                  'O': []}})

#------------------------------------------------------------------------------
# Method Unit Tests
#------------------------------------------------------------------------------

class TP_PDCS_TestCase(TestCase):

    def setUp(self):
        self.tp_pdcs = mg.MapGraph._tp_pdcs.im_func
        self.g = DiGraph()
    
    def test_len_tp_greater_than_one(self):
        self.g.add_edges_from((('D-1', 'D-2', {'PDC': 18}),
                               ('D-2', 'C-1', {'PDC': 1}),
                               ('C-1', 'A-2', {'PDC': 18}),
                               ('D-1', 'C-1', {'PDC': 18}),
                               ('C-1', 'D-2', {'PDC': 1}),
                               ('D-2', 'A-2', {'PDC': 8})))
        old_attr = {'RC': 'S', 'PDC': 18, 'TP': ['D-2', 'C-1']}
        new_attr = {'RC': 'S', 'PDC': 18, 'TP': ['C-1', 'D-2']}
        self.assertEqual(self.tp_pdcs(self.g, 'D-1', 'A-2', old_attr,
                                      new_attr),
                         [12 + 1/3.0, 9.0])

    def test_len_tp_equals_one(self):
        self.g.add_edges_from((('C-1', 'D-1', {'PDC': 18}),
                               ('D-1', 'A-1', {'PDC': 2})))
        old_attr = new_attr = {'RC': 'O', 'PDC': 18, 'TP': ['D-1']}
        self.assertEqual(self.tp_pdcs(self.g, 'C-1', 'A-1', old_attr,
                                       new_attr),
                          [10, 10])

    def test_no_attr2(self):
        self.g.add_edges_from((('A-1', 'B-1', {'PDC': 7}),
                               ('B-1', 'C-1', {'PDC': 11}),
                               ('C-1', 'D-1', {'PDC': 3})))
        self.assertEqual(self.tp_pdcs(self.g, 'A-1', 'D-1',
                                      {'TP': ['B-1', 'C-1']}),
                         [7])
            
    
class AssertValidEdgeTestCase(TestCase):

    def setUp(self):
        self.AVE = mg.MapGraph._assert_valid_edge.im_func

    def test_tp_empty(self):
        attr = {'PDC': 5, 'RC': 'I', 'TP': []}
        self.assertFalse(self.AVE(None, 'A', 'B', attr))

    def test_missing_tp_relation(self):
        g = DiGraph()
        g.add_edges_from([('A', 'B'), ('B', 'C'), ('D', 'E')])
        attr = {'PDC': 5, 'RC': 'I', 'TP': ['B', 'C', 'D']}
        self.assertRaises(mg.MapGraphError, self.AVE, g, 'A', 'E', attr)

    def test_valid(self):
        g = DiGraph()
        g.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')])
        attr = {'PDC': 5, 'RC': 'I', 'TP': ['B', 'C', 'D']}
        self.assertFalse(self.AVE(g, 'A', 'E', attr))
                                                           

def test__code():
    g = DiGraph()
    g.add_edges_from((('X', 'A', {'RC': 'S'}),
                      ('A', 'B', {'RC': 'I'}),
                      ('B', 'Y', {'RC': 'L'})))
    nt.assert_equal(mg.MapGraph._code.im_func(g, 'X', ['A', 'B'], 'Y'), 'SIL')


def test_translate_node():
    g = DiGraph()
    g.add_edges_from([('A-1', 'B-1'), ('A-1', 'C-1'), ('A-1', 'B-2')])
    translate_node = mg.MapGraph._translate_node.im_func
    nt.assert_equal(translate_node(g, 'A-1', 'B'), ['B-2', 'B-1'])


#------------------------------------------------------------------------------
# Support Function Unit Tests
#------------------------------------------------------------------------------

def test__pdcs():
    old_attr = {'PDC': 0}
    new_attr = {'PDC': 18}
    nt.assert_equal(mg._pdcs(old_attr, new_attr), (0, 18))


def test__tp_len():
    old_attr = {'TP': ['A', 'B', 'C']}
    new_attr = {'TP': []}
    nt.assert_equal(mg._tp_len(old_attr, new_attr), (3, 0))


def test__reverse_attr():
    attr = {'RC': 'S', 'PDC': 5, 'TP': ['A', 'B', 'C']}
    nt.assert_equal(mg._reverse_attr(attr),
                    {'RC': 'L', 'PDC': 5, 'TP': ['C', 'B', 'A']})
    # Make sure the original value has not been modified.
    nt.assert_equal(attr, {'RC': 'S', 'PDC': 5, 'TP': ['A', 'B', 'C']})
    


    def _tp_pdcs(self, source, target, attr1, attr2=None):
        """Return mean PDC for relation chain in attr(s).

        Called by _update_attr and deduce_edges.
        """
        if not attr2:
            tps = (attr1['TP'],)
        else:
            tps = (attr1['TP'], attr2['TP'])
        mean_pdcs = []
        for tp in tps:
            if tp:
                full_tp = [source] + tp + [target]
                pdcs = []
                for i in range(len(full_tp) - 1):
                    pdcs.append(self[full_tp[i]][full_tp[i + 1]]['PDC'])
                mean_pdcs.append(mean(pdcs))
            else:
                mean_pdcs.append(self[source][target]['PDC'])
        return mean_pdcs
    
    def _update_attr(self, source, target, new_attr):
        """Called by _add_edge."""
        old_attr = self[source][target]
        funcs = (_tp_len, _pdcs, self._tp_pdcs)
        arg_groups = [(old_attr, new_attr)] * 2 + [(source, target, old_attr,
                                                    new_attr)]
        for func, args in zip(funcs, arg_groups):
            old_value, new_value = func(*args)
            if old_value < new_value:
                return old_attr
            if old_value > new_value:
                return new_attr
        return old_attr

    def _assert_valid_edge(self, source, target, attr):
        """Called by _add_edge."""
        value = attr['TP']
        assert isinstance(value, list)
        if value:
            full_tp = [source] + value + [target]
            for i in range(len(full_tp) - 1):
                i_s, i_t = full_tp[i], full_tp[i + 1]
                if not self.has_edge(i_s, i_t):
                    raise MapGraphError('TP for (%s, %s) assumes (%s, %s).' %
                                        (source, target, i_s, i_t))
        value = attr['PDC']
        if not (type(value) in (int, float, float64) and 0 <= value <= 18):
            raise MapGraphError('PDC is %s, type is %s' % (value, type(value)))
        value = attr['RC']
        if value not in ('I', 'S', 'L', 'O'):
            raise MapGraphError('RC is %s' % value)
    
    def _add_edge(self, source, target, new_attr):
        """Called by add_edge."""
        if source.split('-')[0] != target.split('-')[0]:
            self._assert_valid_edge(source, target, new_attr)
            if self.has_edge(source, target):
                new_attr = self._update_attr(source, target, new_attr)
            DiGraph.add_edge.im_func(self, source, target, new_attr)
        else:
            self._pick_one_level_of_resolution(source, target, new_attr['RC'])

    def _pick_one_level_of_resolution(self, source, target, rc):
        pass

    def add_edge(self, source, target, new_attr):
        """Add an edge from source to target if it is new and valid.

        For the edge to be valid, new_attr must have as keys 'TP' (mapping
        to a list of nodes each of which has an edge to the next), 'PDC'
        (mapping to a float between 0 and 18, inclusive), and 'RC' (mapping
        to a valid relation code).

        If an edge from source to target is already present, the set of
        attributes with the shortest transformation path (TP) is kept.
        Ties are resolved by choosing the set with the lower precision
        description code (PDC), and failing that, the lower mean PDC of
        the edges in the TP.

        Parameters
        ----------
        source, target : strings
          Nodes.

        new_attr : dict
          Dictionary of edge attributes.
        """
        self._add_edge(source, target, new_attr)
        reverse_attr = _reverse_attr(new_attr)
        self._add_edge(target, source, reverse_attr)

    def add_edges_from(self, ebunch):
        """Add the edges in ebunch if they are new and valid.

        The docstring for add_edge explains what is meant by valid and how
        attributes for the same source and target are updated.

        Parameters
        ----------
        ebunch : container of edges
          Edges must be provided as (source, target, new_attr) tuples; they
          are added using add_edge.
        """
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

#------------------------------------------------------------------------------
# Deduction Methods
#------------------------------------------------------------------------------

    def deduce_edges(self):
        """Deduce new edges based on those in the graph and add them.

        This implementation is faithful to the algorithm described in
        Stephan et al. (2000) with two exceptions:

        (1) Kotter and Wanke's (2005) adjustment to the determination of
        single relation codes for deduced edges is incorporated.
        """
        for node in self.nodes_iter():
            ebunch = []
            for p in self.predecessors(node):
                for s in self.successors(node):
                    if p != s:
                        tp = self[p][node]['TP'] + [node] + self[node][s]['TP']
                        rc_res = _rc_res(self._code(p, tp, s))
                        if rc_res:
                            attr = {'TP': tp, 'RC': rc_res,
                                    'PDC': self._tp_pdcs(p, s, {'TP': tp})[0]}
                            ebunch.append((p, s, attr))
            self.add_edges_from(ebunch)

#------------------------------------------------------------------------------
# Translation Methods
#------------------------------------------------------------------------------

    def _make_translation_dict(self, node, desired_bmap):
        """Map regions in desired_bmap to regions in node's map."""
        translation_dict = {}
        node_map = node.split('-')[0]
        for new_node in self._translate_node(node, desired_bmap):
            translation_dict[new_node] = {'S': [], 'I': [], 'L': [], 'O': []}
            node_dict = translation_dict[new_node]
            for rc in node_dict:
                node_dict[rc] = self._translate_node(new_node, node_map, rc)
        return translation_dict

            
    def _translate_node(self, node, out_map, rc=None):
        """Return list of nodes from out_map coextensive with node."""
        if node.split('-')[0] == out_map and (rc == None or rc == 'I'):
            return [node]
        neighbors = []
        for method in (self.successors, self.predecessors):
            try:
                neighbors += method(node)
            except NetworkXError:
                pass
        result = [n for n in set(neighbors) if n.split('-')[0] == out_map]
        if rc:
            result = [n for n in result if self[n][node]['RC'] == rc]
        return result

#------------------------------------------------------------------------------
# Support Functions
#------------------------------------------------------------------------------

def _pdcs(old_attr, new_attr):
    """Called by _update_attr."""
    return old_attr['PDC'], new_attr['PDC']


def _tp_len(old_attr, new_attr):
    """Called by _update_attr."""
    return len(old_attr['TP']), len(new_attr['TP'])

        
def _reverse_attr(attr):
    """Called by add_edge."""
    rc_switch = {'I': 'I', 'S': 'L', 'L': 'S', 'O': 'O', None: None}
    # Need to deep copy to prevent modification of attr.
    tp = deepcopy(attr['TP'])
    tp.reverse()
    return {'RC': rc_switch[attr['RC']], 'PDC': attr['PDC'],
            'TP': tp}
