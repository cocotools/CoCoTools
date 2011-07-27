#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from cStringIO import StringIO
import xml.etree.ElementTree as etree

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class XMLReader(object):

    def __init__(self, search_type, xml):
        prim_tag = {'Mapping': 'PrimaryRelation',
                    'Connectivity': 'IntegratedPrimaryProjection'}
        self.prim_tag = prim_tag[search_type]
        self.tag_prefix = './/{http://www.cocomac.org}'
        self.search_string, self.prim_iterator = self.string2primiter(xml)

    def string2primiter(self, xml_string):
        s = StringIO()
        s.write(xml_string)
        s.seek(0)
        tree = etree.parse(s)
        s.close()
        prefix = self.tag_prefix
        return (tree.find('%sSearchString' % prefix).text,
                tree.iterfind('%s%s' % (prefix, self.prim_tag)))

    def prim2data(self, prim):
        prefix = self.tag_prefix
        site_ids = prim.findall(prefix + 'ID_BrainSite')
        if self.prim_tag == 'PrimaryRelation':
            edge_attr = {}
            for datum in ('RC', 'PDC'):
                try:
                    edge_attr[datum] = [prim.find(prefix + datum).text]
                except AttributeError:
                    edge_attr[datum] = [None]
        elif self.prim_tag == 'IntegratedPrimaryProjection':
            site_pdcs = prim.findall(prefix + 'PDC_Site')
            ecs = prim.findall(prefix + 'EC')
            ec_pdcs = prim.findall(prefix + 'PDC_EC')
            edge_attr = {'source_pdc': [site_pdcs[0].text],
                         'source_ec': [ecs[0].text],
                         'source_ec_pdc': [ec_pdcs[0].text],
                         'target_pdc': [site_pdcs[1].text],
                         'target_ec': [ecs[1].text],
                         'target_ec_pdc': [ec_pdcs[1].text],
                         'weight': [prim.find(prefix + 'Degree').text],
                         'weight_pdc': [prim.find(prefix + 'PDC_Density').text]
                         }
        else:
            raise ValueError('invalid search type')
        return site_ids[0].text, site_ids[1].text, edge_attr
