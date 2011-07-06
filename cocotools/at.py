"""Algebra of Transformation

See Stephan et al., Trans. Roy. Soc. B, 2000.

Notes:

1) This script should be taking into account, for each anatomical connection
processed, which site was injected (see p. 43, first full paragraph as well as
Appendix C). Unfortunately, this information is not listed in CoCoMac XML
output and is therefore inaccessible to us.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from __future__ import print_function

# Third party
import networkx as nx
import nose.tools as nt

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class AT(object):
    def __init__(self, map_g, conn_g, target_map):
        """map_g must have the following properties:

        i) If A-1 is larger than or identical to B-1, there is no other region
        in A with a relationship to B-1.

        ii) If A-1 is smaller than or overlaps with B-1, there is another
        region in A with a relationship to B-1.

        iii) If map_g[A-1][B-1] exists, then map_g[B-1][A-1] exists.
        """
        self.map_g = map_g
        self.conn_g = conn_g
        self.target_map = target_map
        self.target_g = nx.DiGraph()
        self.now = ''
        self.other = ''

    def find_areas(self, source_reg, target_map=None):
        """Find areas in self.target_map coextensive with source_reg.

        Parameters
        ----------
        source_reg : string
          Region from a source map.

        target_map : string
          Map from which regions coextensive with source_reg are sought.

        Returns
        -------
        List of regions from self.target_map coextensive with source_reg.
        """
        if not target_map:
            target_map = self.target_map
        return [region for region in self.map_g.successors(source_reg) if
                region.split('-')[0] == target_map]

    def reverse_find(self, forward_list, target_map):
        """Find areas in target_map coextensive with areas in forward_list.

        Parameters
        ----------
        forward_list : list
          List of regions from self.target_map

        target_map : string
          Source map in the overall scheme of the AT.

        Returns
        -------
        map2map : dict
          Each key is a region in forward_list; each value is a list of regions
          in target_map coextensive with the key.
        """
        map2map = {}
        for region in forward_list:
            map2map[region] = self.find_areas(region, target_map)
        return map2map

    def single_step(self, source_region, target_region):
        """Determine target_region's EC from source_region's EC.

        Parameters
        ----------
        source_region : string
          Region from a source map coextensive with target_region.

        target_region : string
          Region from self.target_map.

        Returns
        -------
        EC for target_region.
        """
        rules = {'L': {'N': 'N', 'P': 'U', 'X': 'U', 'C': 'C'},
                 'I': {'N': 'N', 'P': 'P', 'X': 'X', 'C': 'C'}}
        rc = self.map_g.edge[source_region][target_region]['RC']
        #EC='p' found in conn_g, as downloaded from cocomac.org.
        return rules[rc][self.get_ec(source_region).upper()]

    def multi_step(self, source_list, target_region):
        """Determine target_region's EC from source_list regions' ECs.

        The rules are specified in Table 1. multi_step lacks commutative
        properties: One order in source_list may produce ec_target='P' while
        another produces ec_target='X'. We do not consider this weakness
        significant, given our plan to use final ECs of 'X' and 'P' the same
        way.

        Parameters
        ----------
        source_list : list
          List of regions from a source map coextensive with the target_region.

        target_region : string
          Region from self.target_map.

        Returns
        -------
        ec_target : string
          EC for target_region.
        """
        rules = {'B': {'S': {'N': 'N',
                             'P': 'P',
                             'X': 'X',
                             'C': 'C'
                             },
                       'O': {'N': 'N',
                             'P': 'U',
                             'X': 'U',
                             'C': 'C'
                             },
                       },
                 'N': {'S': {'N': 'N',
                             'P': 'P',
                             'X': 'P',
                             'C': 'P'
                             },
                       'O': {'N': 'N',
                             'P': 'U',
                             'X': 'U',
                             'C': 'P'
                             }
                              },
                  'U': {'S': {'N': 'U',
                              'P': 'P',
                              'X': 'X',
                              'C': 'X'
                              },
                        'O': {'N': 'U',
                              'P': 'U',
                              'X': 'U',
                              'C': 'X'
                              }
                        },
                  'P': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              },
                        'O': {'N': 'P',
                              'P': 'P',
                              'X': 'P',
                              'C': 'P'
                              }
                        },
                  'X': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'X'
                              },
                        'O': {'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'X'
                              }
                        },
                  'C': {'S': {'N': 'P',
                              'P': 'P',
                              'X': 'X',
                              'C': 'C'
                              },
                        'O': {'N': 'P',
                              'P': 'X',
                              'X': 'X',
                              'C': 'C'
                              }
                        }
                  }
        ec_target = 'B'
        for source_region in source_list:
            rc = self.map_g[source_region][target_region]['RC']
            ec_target = rules[ec_target][rc][self.get_ec(source_region)]
        return ec_target

    def iterate_trans_dict(self, trans_dict):
        """Determine ECs for regions in self.target_map.

        Parameters
        ----------
        trans_dict : dict
          Maps regions in self.target_map to coextensive regions in a source
          map.

        Returns
        -------
        ec_dict : dict
          Maps same regions in self.target_map to ECs.
        """
        ec_dict = {}
        for target_reg, source_list in trans_dict.iteritems():
            if len(source_list) == 1:
                ec_dict[target_reg] = self.single_step(source_list[0],
                                                       target_reg)
            elif len(source_list) > 1:
                ec_dict[target_reg] = self.multi_step(source_list, target_reg)
            else:
                raise ValueError, 'source_list must not be empty'
        return ec_dict

    def get_ec(self, source_region):
        """Retrieve EC for the source_region.

        Parameters
        ----------
        source_region : string
          Region from a source map coextensive with region in self.target_map.

        Returns
        -------
        source_region's EC for connetion with self.other
          From source region or to source region according to self.now.
        """
        #We'll say that all of a region is always connected to itself.
        if source_region == self.other:
            return 'C'

        #If we've gotten this far, source_region and self.other are different
        #regions.
        if self.now == 'from':
            if (source_region, self.other) in self.conn_g.edges_iter():
                return self.conn_g[source_region][self.other]['EC_s']
        else:
            if (self.other, source_region) in self.conn_g.edges_iter():
                return self.conn_g[self.other][source_region]['EC_t']

        #And if we've gotten this far, the connection of interest is absent
        #from self.conn_g. We don't know whether it exists in nature.
        return 'U'

    def run_one_end(self, end_reg):
        """Run one node of an anatomical connection through the AT.

        Parameters
        ----------
        end_reg : string
          Region forming one end of the anatomical connection being processed.

        Returns
        -------
        dict mapping regions in self.target_map to ECs for this connection.
        """
        coext_w_end = self.find_areas(end_reg)        
        end_dict = self.reverse_find(coext_w_end, end_reg.split('-')[0])
        return self.iterate_trans_dict(end_dict)

    def add_edge(self, from_, ec_s, to, ec_t):
        """This needs some work!
        """
        if from_ != to:
            if ec_s != 'U' and ec_t != 'U':
                if not self.target_g.has_edge(from_, to):
                    self.target_g.add_edge(from_, to, EC_s=[ec_s], EC_t=[ec_t])
                else:
                    self.target_g[from_][to]['EC_s'].append(ec_s)
                    self.target_g[from_][to]['EC_t'].append(ec_t)

    def process_one_edge(self, from_, to):
        """Run both ends of one anatomical connection through the AT.

        Add edges to self.target_g as appropriate.

        Having this as its own function allows one to more easily read along
        in the Stephan et al. paper (p. 43).

        Parameters
        ----------
        from_ : string
          Source node of the anatomical connection being processed.

        to : string
          Target node of the anatomical connection being processed.

        Returns
        -------
        None
          Potentially adds and/or changes edges in self.target_g.
        """
        #Perform the AT on the source node (from_).
        if from_.split('-')[0] == self.target_map:
                from_ec_dict = {from_: self.conn_g[from_][to]['EC_s']}
        else:
            self.now = 'from'
            self.other = to
            from_ec_dict = self.run_one_end(from_)

        #Now perform the AT on the target node (to).
        if to.split('-')[0] == self.target_map:
            to_ec_dict = {to: self.conn_g[from_][to]['EC_t']}
        else:
            self.now = 'to'
            self.other = from_
            to_ec_dict = self.run_one_end(to)

        #With the ec_dicts, add/adjust edges in self.target_g as appropriate.
        for from_targ, ec_s in from_ec_dict.iteritems():
            for to_targ, ec_t in to_ec_dict.iteritems():
                self.add_edge(from_targ, ec_s, to_targ, ec_t)

    def iterate_edges(self):
        count = 0
        for from_, to in self.conn_g.edges():
            self.process_one_edge(from_, to)
            count += 1
            print('AT: %d/%d' % (count, len(self.conn_g.edges())))
