"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

import os
import win32com.client as win32

from ._error import Error
from ._exception import *
from ._dataframe import DataFrame

class PlantSim:

    def __init__(self, version='', visible=True, trust_models=False, license_type='Professional'):        
        """
        Initialize the Plant Simulation application
        :param version: The version of Plant Simulation to use
        :param visible: If True, the Plant Simulation window will be visible
        :param trust_models: If True, Plant Simulation models will be allowed to access the computer
        :param license_type: The license type to use (Professional, Student, Viewer)
        """

        print(f":: Launching Plant Simulation (version={version}, license={license_type}, visibility={visible}, trust_models={trust_models})")

        dispatch_string = 'Tecnomatix.PlantSimulation.RemoteControl'
        if version != '':
            dispatch_string += f'.{version}'

        # Early-binding version
        try:
            self.plantsim = win32.gencache.EnsureDispatch(dispatch_string)
        except Exception as e:
            raise RuntimeError(f"Failed to dispatch Plant Simulation with version '{version}': {e}")

        if visible:
            # Open the Plant Simulation window
            self.plantsim.SetVisible(True)

        if trust_models:
            # Allow Plant Simulation models to access the computer
            self.plantsim.SetTrustModels(True)

        self.license_type = license_type
        try:
            self.plantsim.SetLicenseType(self.license_type)
        except BaseException as e:
            if Error.extract(e.args) == Error.Code.INVALID_LICENSE:
                raise InvalidLicenseError(self.license_type)

        self.path_context = ''
        self.event_controller = ''

    def load_model(self, filepath: str):
        """
        Load a Plant Simulation model
        :param filepath: The path to the model file
        """
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Model file "{filepath}" not found!')

        print(f'  Loading model "{filepath}"...')
        try:
            self.plantsim.LoadModel(filepath)
        except BaseException as e:
            if Error.extract(e.args) == Error.Code.INVALID_LICENSE:
                raise InvalidLicenseError(self.license_type)
            
        print(f'  Model "{filepath}" loaded.')

    def set_path_context(self, path_context: str):
        """
        Set the path context to the current path context
        :param path_context: The path context in PlantSim
        """

        self.path_context = path_context
        self.plantsim.SetPathContext(self.path_context)

        print(f'  Path context set to "{self.path_context}".')

    def set_event_controller(self, event_controller: str='EventController'):
        """
        Set the event controller to the current path context
        :param event_controller: The name of the event controller in PlantSim
        """

        if not self.path_context:
            raise CommandOrderError("set_event_controller", "set_path_context")
        self.event_controller = f'{self.path_context}.{event_controller}'

        print(f'  Event controller set to "{self.event_controller}".')

    def reset_simulation(self):
        """
        Reset the simulation
        """

        if not self.event_controller:
            raise CommandOrderError("reset_simulation", "set_event_controller")
        self.plantsim.ResetSimulation(self.event_controller)

    def start_simulation(self):
        """
        Start the simulation
        """

        if not self.event_controller:
            raise CommandOrderError("start_simulation", "set_event_controller")

        self.plantsim.StartSimulation(self.event_controller)

    def stop_simulation(self):
        """
        Stop the simulation 
        """

        self.plantsim.StopSimulation()

    def is_simulation_running(self):
        """
        Check if the simulation is running
        :return: True if the simulation is running, False otherwise
        """

        return self.plantsim.IsSimulationRunning()

    def get_value(self, object_name: str):
        """
        Get the value of an object 
        :param object_name: The name of the object in PlantSim
        :return: The value of the object
        """

        return self.plantsim.GetValue(object_name)

    def set_value(self, object_name: str, value):
        """
        Set the value of an object in PlantSim
        :param object_name: The name of the object in PlantSim
        :param value: The value to set
        """

        self.plantsim.SetValue(object_name, value)

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
            command_string = f'{self.path_context}.{command_string}'
        else:
            command_string = f'.{command_string}'

        if parameter:
            self.plantsim.ExecuteSimTalk(command_string, parameter)
        else:
            self.plantsim.ExecuteSimTalk(command_string)

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

    def quit(self):
        """
        Quits the Plant Simulation application
        """

        self.plantsim.Quit()
