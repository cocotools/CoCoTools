from numpy import mean
from networkx import DiGraph

from cocotools.utils import ALLOWED_VALUES


class ConGraph(DiGraph):

    def add_edge(self, source, target, new_attr):
        _assert_valid_attr(new_attr)
        add_edge = DiGraph.add_edge.im_func
        if not self.has_edge(source, target):
            add_edge(self, source, target, new_attr)
        else:
            old_attr = self[source][target]
            add_edge(self, source, target, _update_attr(old_attr, new_attr))

    def add_edges_from(self, ebunch):
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr)

            
def _update_attr(old_attr, new_attr):
    for func in (_mean_pdcs, _ec_points):
        old_value, new_value = func(old_attr, new_attr)
        if old_value < new_value:
            return old_attr
        if old_value > new_value:
            return new_attr
    return old_attr

            
def _assert_valid_attr(attr):
    for key in ('EC_Source', 'PDC_Site_Source', 'PDC_EC_Source', 'Degree',
                'EC_Target', 'PDC_Site_Target', 'PDC_EC_Target', 
                'PDC_Density'):
        value = attr[key]
        if 'PDC' in key:
            assert isinstance(value, int)
            assert value >= 0 and value <= 18
            continue
        assert not value or value in ALLOWED_VALUES[key.split('_')[0]]
        if key == 'Degree':
            ecs = [attr['EC_Source'], attr['EC_Target']]
            assert value
            assert (value == '0' and 'N' in ecs) or (value != '0' and 'N'
                                                     not in ecs)
    
            
def _mean_pdcs(old_attr, new_attr):
    return [mean((a['PDC_Site_Source'],
                  a['PDC_Site_Target'],
                  a['PDC_EC_Source'],
                  a['PDC_EC_Target'],
                  a['PDC_Density'])) for a in (old_attr, new_attr)]

def _ec_points(old_attr, new_attr):
    # Score it like golf.
    points = {'C': -2, 'N': -2, 'P': -1, 'X': 0}
    return [sum((points[a['EC_Source']],
                 points[a['EC_Target']])) for a in (old_attr, new_attr)]

