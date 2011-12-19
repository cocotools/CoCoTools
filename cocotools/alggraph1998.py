import itertools

import networkx as nx


class AlgGraph1998Error(Exception):
    pass


class AlgGraph1998(nx.DiGraph):

    def __init__(self, mapp):
        nx.DiGraph.__init__.im_func(self)
        self.conn = mapp.conn
        self.mapp = mapp

    def _multi_step_operation(self, pair1, pair2):
        """A combination of the intermediate and terminal operations.

        Notes
        -----
        Stephan & Kotter assume "all areas of saA and taA as a unified
        piece of cortex are equivalent to or include Bp and Bq,
        respectively."  However, this is not necessarily the case: Many
        brain maps deliberately fail to encompass the entire cortex.  As a
        result, the logic of this operation is incorrect: A final EC of C
        or N should never occur.
        """
        RC1, EC1 = pair1
        RC2, EC2 = pair2
        if (RC1, RC2, EC1, EC2) == ('S', 'S', 'C', 'C'): # 7
            return 'S', 'C'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'C', 'P'): # 8
            return 'S', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'C', 'N'): # 9
            return 'S', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'P', 'P'): # 10
            return 'S', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'P', 'N'): # 11
            return 'S', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'N', 'N'): # 12
            return 'S', 'N'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'C', 'C'): # 13
            return 'O', 'C'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'C', 'P'): # 14
            return 'O', ('P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'C', 'N'): # 15
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'P', 'C'): # 16
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'P', 'P'): # 17
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'P', 'N'): # 18
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'N', 'C'): # 19
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'N', 'P'): # 20
            return 'O', ('N', 'P')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'N', 'N'): # 21
            return 'O', 'N'
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'C', 'C'): # 22
            return 'O', 'C'
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'C', 'P'): # 23
            return 'O', ('P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'C', 'N'): # 24
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'P', 'P'): # 25
            return 'O', ('N', 'P', 'C')                    
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'P', 'N'): # 26
            return 'O', ('N', 'P')
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'N', 'N'): # 27
            return 'O', 'N'
        # The following rules are not contained in the 1998 paper.
        # They have been added to account for ECs of U, indicating
        # connections that have not been studied.
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'C', 'U'): # 28
            return 'S', ('P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'P', 'U'): # 29
            return 'S', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'U', 'U'): # 30
            return 'S', ('N', 'P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'S', 'U', 'N'): # 31
            return 'S', ('N', 'P')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'C', 'U'): # 32
            return 'O', ('P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'P', 'U'): # 33
            return 'O', 'P'
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'U', 'C'): # 34
            return 'O', ('P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'U', 'P'): # 35
            return 'O', ('N', 'P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'U', 'U'): # 36
            return 'O', ('N', 'P', 'C')
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'U', 'N'): # 37
            return 'O', ''
        elif (RC1, RC2, EC1, EC2) == ('S', 'O', 'N', 'U'): # 38
            return 'O', ''
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'N', 'N'): # 39
            return 'O', ''
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'N', 'N'): # 40
            return 'O', ''
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'N', 'N'): # 41
            return 'O', ''
        elif (RC1, RC2, EC1, EC2) == ('O', 'O', 'N', 'N'): # 42
            return 'O', ''
        else:
            raise AlgGraph1998Error('invalid input: %s, %s, %s, %s' % (pair1,
                                                                       pair2))

    def _order_RC_EC_pairs(self, RC_list, EC_list):
        unordered_pairs = zip(RC_list, EC_list)
        ordered_pairs = []
        for pair in [('S', 'C'), ('S', 'P'), ('S', 'N'), ('O', 'C'),
                     ('O', 'P'), ('O', 'N')]:
            while pair in unordered_pairs:
                unordered_pairs.remove(pair)
                ordered_pairs.append(pair)
        if unordered_pairs:
            raise AlgGraph1998Error('Invalid RC/EC pairs: %s' %
                                    unordered_pairs)
        return ordered_pairs
                
    def _one_step_operation(self, RC, EC):
        if (RC, EC) == ('I', 'C'): # 1
            return 'C'
        if (RC, EC) == ('I', 'P'): # 2
            return 'P'
        if (RC, EC) == ('I', 'N'): # 3
            return 'N'
        if (RC, EC) == ('L', 'C'): # 4
            return 'C'
        if (RC, EC) == ('L', 'P'): # 5
            return ('N', 'P', 'C')
        if (RC, EC) == ('L', 'N'): # 6
            return 'N'

    def _get_RCs(self, A_list, Bx):
        return [self.mapp[Ax][Bx]['RC'] for Ax in A_list]

    def _get_maximum_ECs(self, saA, taA):
        """Return the maximum ECs for edges between saA and taA.

        For each region in saA, of its sCs to the regions in taA, get the
        most extensive one. Then acquire the corresponding maximum rCs for
        the regions in taA.

        Parameters
        ----------
        saA : list
          Those areas in the original brain map that overlap with the
          source being processed in the desired brain map.

        taA : list
          Those areas in the original brain map that overlap with the
          target being processed in the desired brain map.

        Returns
        -------
        sC_list : list
          List with maximum sC for each region in saA.

        rC_list : list
          List with maximum rC for each region in taA.
        """
        # Although not introduced in the 1998 paper, 'U' appears here
        # to account for the situation in which an edge has not been
        # tested in the original literature.  U means C, P, or N.
        EC_rank = ('C', 'P', 'U', 'N')
        sC_list = []
        for Aix in saA:
            maximum_sC = 'N'
            for Ajx in taA:
                try:
                    sC = self.conn[Aix][Ajx]['sC']
                except KeyError:
                    sC = 'U'
                if EC_rank.index(sC) < EC_rank.index(maximum_sC):
                    maximum_sC = sC
            sC_list.append(maximum_sC)

        rC_list = []
        for Ajx in taA:
            maximum_rC = 'N'
            for Aix in saA:
                try:
                    rC = self.conn[Aix][Ajx]['rC']
                except KeyError:
                    rC = 'U'
                if EC_rank.index(rC) < EC_rank.index(maximum_rC):
                    maximum_rC = rC
            rC_list.append(maximum_rC)
        return sC_list, rC_list

    def _translate_node(self, input_node, output_map):
        """Return regions in output_map coextensive with input_node.

        Parameters
        ----------
        input_node : string

        output_map : string

        Returns
        -------
        output_nodes : list
          Nodes in output_map coextensive with input_node according to
          relations in self.mapp.
        """
        if input_node.split('-')[0] == output_map:
            return [node]
        # All edges in self.mapp are reciprocal.
        neighbors = self.mapp.neighbors(input_node)
        return [n for n in neighbors if n.split('-')[0] == output_map]

    def algebra_of_transformation(self, B):
        """Perform the 1998 algebra.

        Using spatial relationships in self.mapp, translate the anatomical
        connections in self.conn into the nomenclature of a desired brain
        map (B).

        Stephan & Kotter, 1998, in Neural Circuits and Networks.

        Parameters
        ----------
        B : string
          Name of brain map to which translation will be performed.

        Notes
        -----
        In original data, allowed ECs are N, P, and C and allowed PrCs are
        NN, PP, PC, CP, and CC.  A PrC of UU is given to edges that do not
        appear in the original data.
        """
        for Ai0, Aj0 in self.conn.edges_iter():
            saB = self._translate_node(Ai0, B)
            taB = self._translate_node(Aj0, B)
            ARC = itertools.product(saB, taB)
            # We are not requiring that Ai0 and Aj0 be from the same map.
            A1 = Ai0.split('-')[0]
            A2 = Aj0.split('-')[0]
            for Bp, Bq in ARC:
                if Bp == Bq:
                    continue
                saA = self._translate_node(Bp, A1)
                taA = self._translate_node(Bq, A2)
                sC_list, rC_list = self._get_maximum_ECs(saA, taA)
                sRC_list = self._get_RCs(saA, Bp)
                rRC_list = self._get_RCs(taA, Bq)

                if len(sRC_list) == 1:
                    sCres = self._one_step_operation(sRC_list[0], sC_list[0])
                else:
                    ordered_pairs = self._order_RC_EC_pairs(sRC_list, sC_list)
                    result = ordered_pairs[0]
                    for pair in ordered_pairs[1:]:
                        result = self._multi_step_operation(result, pair)
                    sCres = result[1]

                if len(rRC_list) == 1:
                    rCres = self._one_step_operation(rRC_list[0], rC_list[0])
                else:
                    ordered_pairs = self._order_RC_EC_pairs(rRC_list, rC_list)
                    result = ordered_pairs[0]
                    for pair in ordered_pairs[1:]:
                        result = self._multi_step_operation(result, pair)
                    rCres = result[1]

                self.add_edge(Bp, Bq, sC=sCres, rC=rCres)
