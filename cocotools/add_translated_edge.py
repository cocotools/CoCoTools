def add_translated_edge(endg, mapp, conn, desired_map, method, edge):
        """This function translates one edge in conn to nomenclature of desired_bmap.

        Useful for testing registrations of specific edges or interrogating differences between ORT and mORT.

        Parameters
        ----------
        mapp : MapGraph
          Graph of spatial relationships between BrainSites from various
          BrainMaps.

        conn : ConGraph
          Graph of anatomical connections between BrainSites.

        desired_map : string
          Name of BrainMap to which translation will be performed.

        method : string
          AT method to be used: 'original' (that of Stephan & Kotter)
          or 'modified'
        """
        endg.map = desired_map
        # Add all target-map nodes to the EndGraph.  We need to search both
        # the map and con graphs because one can contain nodes the other
        # doesn't have.
        for node in set(mapp.nodes()+conn.nodes()):
            if node.split('-')[0] == desired_map:
                endg.add_node(node.split('-', 1)[-1])
        at_setting = {'original': endg._translate_attr_original,
                      'modified': endg._translate_attr_modified}
        endg._translate_attr = at_setting[method]
        for original_s, original_t in edge:
            s_dict = endg._make_translation_dict(mapp, original_s, desired_map)
            t_dict = endg._make_translation_dict(mapp, original_t, desired_map)
            for s_mapping in s_dict.iteritems():
                for t_mapping in t_dict.iteritems():
                    attr = endg._translate_attr(s_mapping, t_mapping, mapp,
                                                conn)
                    # The first element in each mapping is the node in
                    # desired_map.  We must remove the brain map name,
                    # pre-pended to the name of the area.  (Note that
                    # the brain map is stored as self.map.)
                    new_source = s_mapping[0].split('-', 1)[-1]
                    new_target = t_mapping[0].split('-', 1)[-1]
                    endg.add_edge(new_source, new_target, attr)
