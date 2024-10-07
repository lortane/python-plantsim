"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

import pandas as pd


class DataFrame(pd.DataFrame):
    def __init__(self, plantsim, table_name):
        """
        Table mapping for PlantSim Tables (e.g., DataTable, ExplorerTable)
        :param plantsim: Plantsim instance (with loaded model) that is queried
        :param table_name: The object name within Plantsim relative to the current path context
        """
        col_count = plantsim.get_value(f"{table_name}.XDim")
        row_count = plantsim.get_value(f"{table_name}.YDim")

        if row_count > 0 and col_count > 0:
            data = [
                [
                    plantsim.get_value(f"{table_name}[{col_idx + 1}, {row_idx + 1}]")
                    for col_idx in range(col_count + 1)
                ]
                for row_idx in range(row_count + 1)
            ]
            super().__init__(data[1:], columns=data[0])
        else:
            super().__init__()

    def __str__(self):
        """
        Returns string representation via pandas DataFrame
        :return: string representation of table
        """
        if not self.empty:
            return super().__str__()
        else:
            return "<empty table>"
