from networkx import DiGraph


class EndGraphError(Exception):
    pass


class EndGraph(DiGraph):

    def add_edge(self, source, target, new_attr, method):
        if method == 'dan':
            add_edge = DiGraph.add_edge.im_func
            if not self.has_edge(source, target):
                add_edge(self, source, target, new_attr)
            else:
                for key, value in new_attr.iteritems():
                    try:
                        self[source][target][key] += value
                    except KeyError:
                        self[source][target][key] = value
        elif method == 'ort':
            _assert_valid_attr(new_attr)
            add_edge = DiGraph.add_edge.im_func
            if not self.has_edge(source, target):
                add_edge(self, source, target, new_attr)
            else:
                old_attr = self[source][target]
                add_edge(self, source, target, _update_attr(old_attr,
                                                            new_attr))
        else:
            raise EndGraphError('Invalid method supplied.')

    def add_edges_from(self, ebunch, method):
        for (source, target, new_attr) in ebunch:
            self.add_edge(source, target, new_attr, method)

    def add_translated_edges(self, mapp, conn, desired_bmap, method):
        if method == 'dan':
            self.dan_translate(mapp, conn, desired_bmap)
        elif method == 'ort':
            self.ort_translate(mapp, conn, desired_bmap)

    def dan_translate(self, mapp, conn, desired_bmap):
        num_edges = conn.number_of_edges()
        conn_edges = conn.edges()
        while conn_edges:
            s, t = conn_edges.pop()
            s_map, t_map = s.split('-')[0], t.split('-')[0]
            ebunch = []
            for new_s, new_t in mapp._translate_edge(s, t, desired_bmap):
                old_edges = mapp._translate_edge(new_s, new_t, s_map, t_map)
                incomplete = False
                for old_s, old_t in old_edges:
                    try:
                        degree = conn[old_s][old_t]['Degree']
                    except KeyError:
                        incomplete = True
                        continue
                    if degree != '0':
                        attr = {'ebunches_for': [(s_map, t_map)]}
                        break
                else:
                    if incomplete:
                        attr = {'ebunches_incomplete': [(s_map, t_map)]}
                    else:
                        attr = {'ebunches_against': [(s_map, t_map)]}
                for processed_edge in old_edges:
                    try:
                        conn_edges.remove(processed_edge)
                    except ValueError:
                        pass
                ebunch.append((new_s, new_t, attr))
            self.add_edges_from(ebunch, 'dan')

    def ort_translate(self, mapp, conn, desired_bmap):
        for s, t in conn.edges_iter():
            s_map = s.split('-')[0]
            # new_sources will have regions from desired_bmap
            # coextensive with source as keys and (ec, pdc) tuples as
            # values.
            new_sources = {}
            for new_s in mapp._translate_node(s, desired_bmap):
                single_steps, multi_steps = mapp._separate_rcs(new_s, s_map)
                new_sources[new_s] = []
                for old_s, rc in single_steps:
                    new_sources[new_s].append(conn._single_ec_step(old_s, rc,
                                                                   t,
                                                                   'Source'))
                if multi_steps:
                    ec = 'B'
                    pdc_sum = 0.0
                    for old_s, rc in multi_steps:
                        ec, pdc_sum = conn._multi_ec_step(old_s, rc, t,
                                                          'Source', ec,
                                                          pdc_sum)
                    avg_pdc = pdc_sum / (2 * len(multi_steps))
                    new_sources[new_s].append((ec, avg_pdc))
            t_map = t.split('-')[0]
            new_targets = {}
            for new_t in mapp._translate_node(t, desired_bmap):
                single_steps, multi_steps = mapp._separate_rcs(new_t, t_map)
                new_targets[new_t] = []
                for old_t, rc in single_steps:
                    new_targets[new_t].append(conn._single_ec_step(s, rc,
                                                                   old_t,
                                                                   'Target'))
                if multi_steps:
                    ec = 'B'
                    pdc_sum = 0.0
                    for old_t, rc in multi_steps:
                        ec, pdc_sum = conn._multi_ec_step(s, rc, old_t,
                                                          'Target', ec,
                                                          pdc_sum)
                    avg_pdc = pdc_sum / (2 * len(multi_steps))
                    new_targets[new_t].append((ec, avg_pdc))
            for new_s, s_values in new_sources.iteritems():
                for new_t, t_values in new_targets.iteritems():
                    for s_value in s_values:
                        for t_value in t_values:
                            self.add_edge(new_s, new_t,
                                          {'EC_Source': s_value[0],
                                           'EC_Target': t_value[0],
                                           'PDC_Source': s_value[1],
                                           'PDC_Target': t_value[1],
                                           'original_maps': (s_map, t_map)},
                                          'ort')

    def add_controversy_scores(self):
        for source, target in self.edges_iter():
            edge_dict = self[source][target]
            for group in ('for', 'against'):
                try:
                    exec '%s_ = len(edge_dict["ebunches_%s"])' % (group, group)
                except KeyError:
                    exec '%s_ = 0' % group
            try:
                edge_dict['score'] = (for_ - against_) / float(for_ + against_)
            except ZeroDivisionError:
                edge_dict['score'] = 0


def _assert_valid_attr(attr):
    for key in ('EC_Source', 'EC_Target', 'PDC_Source', 'PDC_Target',
                'original_maps'):
        value = attr[key]
        if 'PDC' in key:
            if not (type(value) in (int, float, np.float64) and
                    0 <= value <= 18):
                raise EndGraphError('PDC is %s, type is %s' %
                                    (value, type(value)))
        elif 'EC' in key:
            assert value in ('Up', 'Ux', 'N', 'Nc', 'Np', 'Nx', 'C', 'P', 'X')
        elif key == 'original_maps':
            assert isinstance(value, tuple)
        
            
def _update_attr(old_attr, new_attr):
    for func in (_devalue_u, _value_presence, _mean_pdcs):
        old_value, new_value = func(old_attr, new_attr)
        if old_value < new_value:
            return old_attr
        if old_value > new_value:
            return new_attr
    return old_attr


def _devalue_u(old_attr, new_attr):
    # Score it like golf.
    points = []
    for a in (old_attr, new_attr):
        count = 0
        for ec in (a['EC_Source'], a['EC_Target']):
            if ec == 'Up':
                count += 1
            elif ec == 'Ux':
                count += 2
        points.append(count)
    return points


def _value_presence(old_attr, new_attr):
    old_ecs = old_attr['EC_Source'], old_attr['EC_Target']
    if 'N' in old_ecs:
        old_value = 1
    else:
        old_value = 0
    new_ecs = new_attr['EC_Source'], new_attr['EC_Target']
    if 'N' in new_ecs:
        new_value = 1
    else:
        new_value = 0
    return old_value, new_value


def _mean_pdcs(old_attr, new_attr):
    return [np.mean((a['PDC_Source'], a['PDC_Target'])) for a in
            (old_attr, new_attr)]                
