"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

from enum import Enum

class Error:

    class Code(Enum):
        INVALID_LICENSE = -2147221503

    @staticmethod
    def extract(args):
        return args[2][5]
