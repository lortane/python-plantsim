import pythoncom
import win32com.client as win32

from ._error import Error
from ._exception import InvalidLicenseError

def _run_simulation_worker(params):
    """
    Worker function to run a simulation. This is needed to avoid issues with pickling.
    :param params: Tuple containing (trust_models, dispatch_string, version, model_filepath, path_context, event_controller, data, license_type)
    :return: The result of the simulation
    """
    (trust_models, dispatch_string, version, model_filepath, path_context, event_controller, data, license_type) = params
    input_variable, value, output_variable = data

    pythoncom.CoInitialize()
    try:
        # Initialize the Plant Simulation application
        try:
            com_object = win32.gencache.EnsureDispatch(dispatch_string)
        except Exception as e:
            raise RuntimeError(f"Failed to dispatch Plant Simulation with version '{version}': {e}")

        if trust_models:
            com_object.SetTrustModels(True)

        try:
            com_object.SetLicenseType(license_type)
        except BaseException as e:
            if Error.extract(e.args) == Error.Code.INVALID_LICENSE:
                raise InvalidLicenseError(license_type)
            
        com_object.LoadModel(model_filepath)
        com_object.SetPathContext(path_context)

        # Run the simulation
        com_object.SetValue(input_variable, value)
        com_object.StartSimulation(event_controller)

        while com_object.IsSimulationRunning():
            pass

        result = com_object.GetValue(output_variable)
        com_object.ResetSimulation(event_controller)
    finally:
        pythoncom.CoUninitialize()

    return result