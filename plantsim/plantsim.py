"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

import os
import win32com.client as win32

from .error import Error
from .attribute_explorer import AttributeExplorer
from .exception import *
from .table import DataFrame

class Plantsim:

    def __init__(self, version='', visible=True, trust_models=False, license_type='Professional'):
        print(f'\n+++ Launching Plant Simulation (version={version}, license={license_type}, visibility={visible}, trust_models={trust_models}) +++\n')

        dispatch_string = 'Tecnomatix.PlantSimulation.RemoteControl'
        if version != '':
            dispatch_string += f'.{version}'

        # Late-binding version
        #self.plantsim = win32.Dispatch(dispatch_string)

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

    def load_model(self, filepath):
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Model file "{filepath}" not found!')

        print(f'Loading model "{filepath}"...')
        try:
            self.plantsim.LoadModel(filepath)
        except BaseException as e:
            if Error.extract(e.args) == Error.Code.INVALID_LICENSE:
                raise InvalidLicenseError(self.license_type)

    def set_path_context(self, path_context):

        self.path_context = path_context
        self.plantsim.SetPathContext(self.path_context)

    def set_event_controller(self, event_controller='EventController'):

        if not self.path_context:
            raise CommandOrderError("set_event_controller", "set_path_context")
        self.event_controller = f'{self.path_context}.{event_controller}'

    def reset_simulation(self):

        if not self.event_controller:
            raise CommandOrderError("reset_simulation", "set_event_controller")

        self.plantsim.ResetSimulation(self.event_controller)

    def start_simulation(self):

        if not self.event_controller:
            raise CommandOrderError("start_simulation", "set_event_controller")

        self.plantsim.StartSimulation(self.event_controller)

    def get_object(self, object_name):
        # "Smart" getter that has some limited ability to decide which kind of object to return

        internal_class_name = self.get_value(f'{object_name}.internalClassName')

        if internal_class_name == 'AttributeExplorer':
            # Attribute explorer that dynamically fills a table
            return AttributeExplorer(self, object_name)

        elif internal_class_name == 'NwData':
            # Normal string
            return self.get_value(object_name)

        # Fallback: Return raw value of object
        else:
            return self.get_value(object_name)

    def get_value(self, object_name):

        return self.plantsim.GetValue(object_name)

    def set_value(self, object_name, value):

        self.plantsim.SetValue(object_name, value)

    def execute_simtalk(self, command_string, parameter=None, from_path_context=True):
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

    def get_table(self, table_name):
        """
        Reads the PlantSim table into a pandas DataFrame
        :param table_name: The name of the table in PlantSim
        :return: The pandas DataFrame with the table data
        """

        return DataFrame(self, table_name)

    def set_table(self, table_name, data_frame):
        """
        Writes the DataFrame back to the PlantSim table.
        :param table_name: The name of the table in PlantSim
        :param data_frame: The pandas DataFrame to write to the table
        """
        row_count, col_count = data_frame.shape

        # Set the dimensions of the PlantSim table
        self.set_value(f'{table_name}.XDim', col_count)
        self.set_value(f'{table_name}.YDim', row_count)

        # Write the DataFrame to the PlantSim table
        for row_idx in range(row_count):
            for col_idx in range(col_count):
                value = data_frame.iloc[row_idx, col_idx]
                self.set_value(f'{table_name}[{col_idx + 1}, {row_idx + 1}]', value)

    def quit(self):

        self.plantsim.Quit()
