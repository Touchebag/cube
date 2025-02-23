class SolveResult:
    def __init__(self):
        self.move_list = dict()

    def add_move(self, timestamp, state):
        self.move_list[timestamp] = state

    def get_results(self):
        start_time = min(self.move_list.keys())
        results = dict()

        for timestamp,state in self.move_list.items():
            if state.is_cross_solved():
                if "cross_time" not in results.keys():
                    cross_timestamp = timestamp
                    results["cross_time"] = cross_timestamp - start_time

                if state.is_f2l_solved():
                    if "f2l_time" not in results.keys():
                        f2l_timestamp = timestamp
                        results["f2l_time"] = f2l_timestamp - cross_timestamp

                    if state.is_oll_solved():
                        if "oll_time" not in results.keys():
                            oll_timestamp = timestamp
                            results["oll_time"] = oll_timestamp - f2l_timestamp

                        if state.is_solved():
                            results["pll_time"] = timestamp - oll_timestamp
                            results["total_time"] = timestamp - start_time

        return results

    def get_time(self):
        if len(self.move_list) > 0:
            return max(self.move_list.keys()) - min(self.move_list.keys())
        else:
            return 0
