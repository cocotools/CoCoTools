from numpy import mean
from networkx import DiGraph


class ConGraphError(Exception):
    pass


class ConGraph(DiGraph):

#------------------------------------------------------------------------------
# Construction Methods
#------------------------------------------------------------------------------
    
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

#------------------------------------------------------------------------------
# Translation Methods
#------------------------------------------------------------------------------

    def _single_ec_step(self, s, rc, t, node_label):
        """Perform single-step operation of algebra of transformation.

        Returns
        -------
        EC, mean PDC : tuple
          EC and mean PDC for new node (role indicated by node_label).
        """
        process_ec = {'I': {'N': 'N',
                            'P': 'P',
                            'X': 'X',
                            'C': 'C'},
                      'L': {'N': 'N',
                            'P': 'U',
                            'X': 'U',
                            'C': 'C'}}
        try:
            edge_dict = self[s][t]
        except KeyError:
            return 'U', 18
        return (process_ec[rc][edge_dict['EC_%s' % node_label]],
                mean([edge_dict['PDC_EC_%s' % node_label],
                      edge_dict['PDC_Site_%s' % node_label]]))

    def _multi_ec_step(self, s, rc, t, node_label, ec, pdc_sum):
        process_ec = {'B': {'S': {'Np': 'Up',
                                  'Nx': 'Up',
                                  'Nc': 'N',
                                  'N': 'N',
                                  'P': 'P',
                                  'X': 'X',
                                  'C': 'C'
                                  },
                            'O': {'Np': 'Ux',
                                  'Nx': 'Ux',
                                  'Nc': 'N',
                                  'N': 'N',
                                  'P': 'Ux',
                                  'X': 'Ux',
                                  'C': 'C'
                                  }
                            },
                      'N': {'S': {'Np': 'Up',
                                  'Nx': 'Up',
                                  'Nc': 'N',
                                  'N': 'N',
                                  'P': 'P',
                                  'X': 'P',
                                  'C': 'P'
                                  },
                            'O': {'Np': 'Up',
                                  'Nx': 'Up',
                                  'Nc': 'N',
                                  'N': 'N',
                                  'P': 'Up',
                                  'X': 'Up',
                                  'C': 'P'
                                  }
                            },
                      'Up': {'S': {'Np': 'Up',
                                   'Nx': 'Up',
                                   'Nc': 'Up',
                                   'N': 'Up',
                                   'P': 'P',
                                   'X': 'P',
                                   'C': 'P'
                                   },
                             'O': {'Np': 'Up',
                                   'Nx': 'Up',
                                   'Nc': 'Up',
                                   'N': 'Up',
                                   'P': 'Up',
                                   'X': 'Up',
                                   'C': 'P'
                                   }
                             },
                      'Ux': {'S': {'Np': 'Up',
                                   'Nx': 'Up',
                                   'Nc': 'Up',
                                   'N': 'Up',
                                   'P': 'P',
                                   'X': 'X',
                                   'C': 'X'
                                   },
                             'O': {'Np': 'Ux',
                                   'Nx': 'Ux',
                                   'Nc': 'Up',
                                   'N': 'Up',
                                   'P': 'Ux',
                                   'X': 'Ux',
                                   'C': 'X'
                                   }
                             },
                      'P': {'S': {'Np': 'P',
                                  'Nx': 'P',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'P',
                                  'X': 'P',
                                  'C': 'P'
                                  },
                            'O': {'Np': 'P',
                                  'Nx': 'P',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'P',
                                  'X': 'P',
                                  'C': 'P'
                                  }
                            },
                      'X': {'S': {'Np': 'P',
                                  'Nx': 'P',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'P',
                                  'X': 'X',
                                  'C': 'X'
                                  },
                            'O': {'Np': 'X',
                                  'Nx': 'X',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'X',
                                  'X': 'X',
                                  'C': 'X'
                                  }
                            },
                      'C': {'S': {'Np': 'P',
                                  'Nx': 'P',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'P',
                                  'X': 'X',
                                  'C': 'C'
                                  },
                            'O': {'Np': 'X',
                                  'Nx': 'X',
                                  'Nc': 'P',
                                  'N': 'P',
                                  'P': 'X',
                                  'X': 'X',
                                  'C': 'C'
                                  }
                            }
                      }
        try:
            edge_dict = self[s][t]
        except KeyError:
            # The connection from s to t has not been studied.
            edge_dict = {'EC_Source': 'N',
                         'EC_Target': 'N',
                         'PDC_EC_Source': 18,
                         'PDC_EC_Target': 18,
                         'PDC_Site_Source': 18,
                         'PDC_Site_Target': 18}
        return (process_ec[ec][rc][edge_dict['EC_%s' % node_label]],
                pdc_sum + edge_dict['PDC_EC_%s' % node_label] +
                edge_dict['PDC_Site_%s' % node_label])
            
            
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
            if not (type(value) in (int, float, float64) and 0 <= value <= 18):
                raise ConGraphError('PDC is %s, type is %s' %
                                    (value, type(value)))
        elif key.split('_')[0] == 'EC':
            assert value in ('C', 'N', 'P', 'X', 'Nc', 'Np', 'Nx')
        elif key == 'Degree':
            ecs = [attr['EC_Source'], attr['EC_Target']]
            assert ((value == '0' and 'N' in ecs)
                    or (value in ('1', '2', '3', 'X') and 'N' not in ecs))
    
            
def _mean_pdcs(old_attr, new_attr):
    return [mean((a['PDC_Site_Source'],
                  a['PDC_Site_Target'],
                  a['PDC_EC_Source'],
                  a['PDC_EC_Target'],
                  a['PDC_Density'])) for a in (old_attr, new_attr)]

def _ec_points(old_attr, new_attr):
    # Score it like golf.
    points = {'C': -4, 'N': -4, 'Nc': -4, 'P': -3, 'X': -2, 'Np': -1, 'Nx': 0}
    return [sum((points[a['EC_Source']],
                 points[a['EC_Target']])) for a in (old_attr, new_attr)]

