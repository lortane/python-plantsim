"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

import os
import concurrent.futures
import win32com.client as win32
from typing import Any, List, Tuple

from ._error import Error
from ._exception import *
from ._dataframe import DataFrame
from ._internal import _run_simulation_worker

class PlantSim:

    def __init__(self, version='', license_type='Professional'):        
        """
        Initialize the Plant Simulation application
        :param version: The version of Plant Simulation to use
        :param license_type: The license type to use (Professional, Student, Viewer)
        """

        self._dispatch_string = 'Tecnomatix.PlantSimulation.RemoteControl'
        self._version = version
        if self._version != '':
            self._dispatch_string += f'.{self._version}'

        self._license_type = license_type
        self._visible = False
        self._trust_models = False
        self._path_context = None
        self._event_controller = None
        self._model = None
        self._plantsim = None

    def initialize(self):
        """
        Initialize the Plant Simulation application
        """

        try:
            self._plantsim = win32.gencache.EnsureDispatch(self._dispatch_string)
        except Exception as e:
            raise RuntimeError(f"Failed to dispatch Plant Simulation with version '{self._version}': {e}")

        try:
            self._plantsim.SetLicenseType(self._license_type)
        except BaseException as e:
            if Error.extract(e.args) == Error.Code.INVALID_LICENSE:
                raise InvalidLicenseError(self._license_type)
            
        self._plantsim.LoadModel(self.model)
        self._plantsim.SetPathContext(self._path_context)

        if self._trust_models:
            self._plantsim.SetTrustModels(True)

        if self._visible:
            self._plantsim.SetVisible(True)
            
        print(f":: Plant Simulation initialized with the following parameters:\n"
                f"   Version: {self._version}\n"
                f"   License Type: {self._license_type}\n"
                f"   Visible: {self._visible}\n"
                f"   Trust Models: {self._trust_models}\n"
                f"   Path Context: {self._path_context}\n"
                f"   Event Controller: {self._event_controller}\n"
                f"   Model: {self._model}")

    def get_value(self, object_name: str):
        """
        Get the value of an object 
        :param object_name: The name of the object in PlantSim
        :return: The value of the object
        """

        return self._plantsim.GetValue(object_name)

    def set_value(self, object_name: str, value):
        """
        Set the value of an object in PlantSim
        :param object_name: The name of the object in PlantSim
        :param value: The value to set
        """

        self._plantsim.SetValue(object_name, value)

    def execute_simtalk(self, command_string: str, parameter=None, from_path_context: bool=True):
        """
        Execute a SimTalk command accodring to COM documentation:
        PlantSim.ExecuteSimTalk("->real; return 3.14159")
        PlantSim.ExecuteSimTalk("param r:real->real; return r*r", 3.14159)
        :param command_string: Command to be executed
        :param parameter: (optional); parameter, if command contains a parameter to be set
        :param from_path_context: if true, command should be formulated form the path context.
                                Else, needs the whole path in the command
        """
        if from_path_context:
            command_string = f'{self._path_context}.{command_string}'
        else:
            command_string = f'.{command_string}'

        if parameter:
            self._plantsim.ExecuteSimTalk(command_string, parameter)
        else:
            self._plantsim.ExecuteSimTalk(command_string)

    def get_table(self, table_name: str) -> DataFrame:
        """
        Reads the PlantSim table into a pandas DataFrame
        :param table_name: The name of the table in PlantSim
        :return: The pandas DataFrame with the table data
        """

        return DataFrame(self, table_name)

    def set_table(self, table_name: str, data_frame: DataFrame):
        """
        Writes the DataFrame back to the PlantSim table.
        :param table_name: The name of the table in PlantSim
        :param data_frame: The pandas DataFrame to write to the table
        """
        row_count, col_count = data_frame.shape

        # Write the DataFrame to the PlantSim table
        for row_idx in range(row_count):
            for col_idx in range(col_count):
                value = data_frame.iloc[row_idx, col_idx]
                self.set_value(f'{table_name}[{col_idx + 1}, {row_idx + 1}]', value)

    def start_simulation(self):
        """
        Start the simulation
        """
        self._plantsim.StartSimulation(self._event_controller)

    def is_simulation_running(self):
        """
        Check if the simulation is running
        :return: True if the simulation is running, False otherwise
        """
        return self._plantsim.IsSimulationRunning()
    
    def reset_simulation(self):
        """
        Reset the simulation
        """
        self._plantsim.ResetSimulation(self._event_controller)

    def run_simulation(self, data: Tuple[str, Any, str]) -> Any:
        """
        Run the simulation
        :param data: Tuple containing (input_variable, value, output_variable)
        :return: The result of the simulation
        """
        input_variable, value, output_variable = data

        self.set_value(input_variable, value)
        self.start_simulation()

        while self.is_simulation_running():
            pass

        result = self.get_value(output_variable)
        self.reset_simulation()

        return result

    def run_simulations_in_parallel(self, simulation_params: List[Tuple[str, Any, str]], max_workers: int=None) -> List[Any]:
        """
        Run multiple simulations in parallel using multiprocessing.Pool
        :param simulation_params: List of tuples, each containing (input_variable, value, output_variable)
        :param max_workers: Maximum number of worker processes to use (default: number of CPUs)
        :return: List of results from each simulation
        """
        pool_params = [
            (
                self._trust_models,
                self._dispatch_string,
                self._version,
                self._model,
                self._path_context,
                self._event_controller,
                params,
                self._license_type
            ) for params in simulation_params
        ]

        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_params = {executor.submit(_run_simulation_worker, param): param for param in pool_params}
            for future in concurrent.futures.as_completed(future_to_params):
                params = future_to_params[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'Simulation with params {params} generated an exception: {exc}')
        return results

    def quit(self):
        """
        Quit the Plant Simulation application
        """
        self._plantsim.Quit()

    @property
    def version(self):
        return self._version

    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, value):
        self._visible = value

    @property
    def trust_models(self):
        return self._trust_models
    
    @trust_models.setter
    def trust_models(self, value):
        self._trust_models = value

    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f'Model file "{path}" not found!')

        self._model = path

    @property
    def path_context(self):
        return self._path_context
    
    @path_context.setter
    def path_context(self, value):
        self._path_context = value

    @property
    def event_controller(self):
        return self._event_controller
    
    @event_controller.setter
    def event_controller(self, value):
        if not self._path_context:
            raise CommandOrderError("set_event_controller", "set_path_context")
        self._event_controller = f'{self._path_context}.{value}'
