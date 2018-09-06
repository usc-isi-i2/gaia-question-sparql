

class Relaxation(object):
    def __init__(self,
                 wider_range=False,
                 larger_bound=False,
                 ignore_enttype=False,
                 at_least_n=0,
                 on_supergraph=False
                 ):
        self.wider_range = wider_range
        self.larger_bound = larger_bound
        self.ignore_enttype = ignore_enttype
        self.at_least_n = at_least_n
        self.on_supergraph = on_supergraph

    @staticmethod
    def help():
        return """
        relaxation arguments:
            wider_range:    [bool] relax the start/end offset,
            larger_bound:   [bool],
            ignore_enttype: [bool],
            at_least_n:     [int >= 0],
            on_supergraph:  [bool] .
        """
