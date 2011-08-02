#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from cStringIO import StringIO
import xml.etree.ElementTree as etree

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

# The lower the index of a letter in PDC, the higher its precision.
ALLOWED_VALUES = {'PDC': ('A', 'C', 'H', 'L', 'D', 'F', 'J', 'N', 'B', 'G',
                          'E', 'K', 'I', 'O', 'M', 'P', 'Q', 'R'),
                  'RC': ('I', 'S', 'L', 'O', 'SO', 'LO', 'ISLO'),
                  'EC': ('C', 'P', 'X', 'N'),
                  'Degree': ('0', '1', '2', '3', 'X')}

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class XMLReader(object):

    def __init__(self, search_type, xml):
        tags = {'Mapping': {'prim': 'PrimaryRelation', 'data': ('RC', 'PDC')},
                'Connectivity': {'prim': 'IntegratedPrimaryProjection',
                                 'data': ('PDC_Site', 'EC', 'PDC_EC', 'Degree',
                                          'PDC_Density')}}
        tag_dict = tags[search_type]
        self.prim_tag = tag_dict['prim']
        self.data_tags = tag_dict['data']
        self.tag_prefix = './/{http://www.cocomac.org}'
        self.search_string, self.prim_iterator = self.string2primiter(xml)

    def string2primiter(self, xml_string):
        s = StringIO()
        s.write(xml_string)
        s.seek(0)
        tree = etree.parse(s)
        s.close()
        tag_prefix = self.tag_prefix
        return (tree.find('%sSearchString' % tag_prefix).text,
                tree.iterfind('%s%s' % (tag_prefix, self.prim_tag)))

    def prim2data(self, prim):
        """Clean and return source, target, and edge attributes in a prim.

        Cleaning means making all entries uppercase and all invalid
        entries None.
        """
        tag_prefix = self.tag_prefix
        edge_attr = {}
        for label in self.data_tags:
            if 'EC' in label or 'Site' in label:
                specifiers = ('Source', 'Target')
            else:
                specifiers = ('',)
            for spec in specifiers:
                if spec:
                    site = prim.find(tag_prefix + '%sSite' % spec)
                    data = site.find(tag_prefix + label)
                    key = '_'.join((label, spec))
                else:
                    data = prim.find(tag_prefix + label)
                    key = label
                try:
                    value = data.text
                except AttributeError:
                    edge_attr[key] = [None]
                else:
                    value = value.upper()
                    if value in ALLOWED_VALUES[label.split('_')[0]]:
                        edge_attr[key] = [value]
                    else:
                        edge_attr[key] = [None]
        if self.prim_tag == 'PrimaryRelation':
            edge_attr['TP'] = [[]]
        site_ids = prim.findall(tag_prefix + 'ID_BrainSite')
        return site_ids[0].text, site_ids[1].text, edge_attr
