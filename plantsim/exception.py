"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

class InvalidLicenseError(Exception):
    """
    Exception raised for invalid license types in PlantSim.
    
    Attributes:
        license_type -- input license type which caused the error
        message -- explanation of the error
    """

    def __init__(self, license_type, message="Invalid license type provided"):
        self.license_type = license_type
        self.message = f"{message}: {license_type}"
        super().__init__(self.message)
    
class CommandOrderError(Exception):
    """
    Exception raised for invalid command order in PlantSim.
    
    Attributes:
        command -- input command which caused the error
        message -- explanation of the error
    """

    def __init__(self, command, prerequisite, message="Command run out of order"):
        self.command = command
        self.prerequisite = prerequisite
        self.message = f"{message}: '{command}' should be run after '{prerequisite}'"
        super().__init__(self.message)