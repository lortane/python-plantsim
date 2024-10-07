"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

from typing import Any, List, Iterator, Tuple


class SimulationData:
    def __init__(
        self, input_variables: List[str], values: List[Any], output_variables: List[str]
    ):
        self._input_variables = input_variables
        self._values = values
        self._output_variables = output_variables
        self._index = 0

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        self._index = 0
        return self

    def __next__(self) -> Tuple[str, Any]:
        if self._index < len(self._input_variables):
            result = (self._input_variables[self._index], self._values[self._index])
            self._index += 1
            return result
        else:
            raise StopIteration()

    def __str__(self) -> str:
        return (
            f"SimulationData(\n"
            f"  input_variables={self._input_variables},\n"
            f"  values={self._values},\n"
            f"  output_variables={self._output_variables}\n"
            f")"
        )

    def get_output_variables(self) -> List[str]:
        return self._output_variables


class SimulationResult:
    def __init__(self, output_variables: List[str], values: List[Any]):
        self._output_variables = output_variables
        self._values = values

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        self._index = 0
        return self

    def __next__(self) -> Tuple[str, Any]:
        if self._index < len(self._output_variables):
            result = (self._output_variables[self._index], self._values[self._index])
            self._index += 1
            return result
        else:
            raise StopIteration()

    def __str__(self) -> str:
        return (
            f"SimulationResult(\n"
            f"  output_variables={self._output_variables},\n"
            f"  values={self._values}\n"
            f")"
        )
