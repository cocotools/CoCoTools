import itertools

import networkx as nx


class AlgGraph1998Error(Exception):
    pass


class AlgGraph1998(nx.DiGraph):

    def _one_step_operation(self):
        pass

    def _terminal_operation(self):
        pass

    def _intermediate_operation(self):
        pass

    def _translate_node(self, input_node, output_map, mapp):
        """Return regions in output_map coextensive with input_node.

        Parameters
        ----------
        input_node : string

        output_map : string

        mapp : CoCoTools MapGraph

        Returns
        -------
        output_nodes : list
          Nodes in output_map coextensive with input_node according to
          relations in mapp.
        """
        if input_node.split('-')[0] == output_map:
            return [node]
        # All edges in mapp are reciprocal.
        neighbors = mapp.neighbors(input_node)
        return [n for n in neighbors if n.split('-')[0] == output_map]

    def algebra_of_transformation(self, mapp, conn, B):
        """Perform the 1998 algebra.

        Using spatial relationships in mapp, translate the anatomical
        connections in conn into the nomenclature of a desired brain map
        (B).

        Stephan & Kotter, 1998, in Neural Circuits and Networks.

        Parameters
        ----------
        mapp : MapGraph
          Graph of spatial relationships between regions from various
          brain maps.

        conn : ConGraph
          Graph of anatomical connections between brain regions.

        B : string
          Name of brain map to which translation will be performed.
        """
        for Ai0, Aj0 in conn.edges_iter():
            saB = self._translate_node(Ai0, B, mapp)
            taB = self._translate_node(Aj0, B, mapp)
            ARC = itertools.product(saB, taB)
            # We are not requiring that Ai0 and Aj0 be from the same map.
            A1 = Ai0.split('-')[0]
            A2 = Aj0.split('-')[0]
            for Bp, Bq in ARC:
                if Bp != Bq:
                    saA = self._translate_node(Bp, A1, mapp)
                    taA = self._translate_node(Bq, A2, mapp)
                    saAXtaA = itertools.product(saA, taA)
                    # Figure out which function to use.
