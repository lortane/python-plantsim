# Python Package for communication with Siemens Tecnomatix Plant Simulation

This package enables the communication with the simulation software product "Tecnomatix Plant Simulation" by
Siemens. It speaks to PlantSim via the COM interface from within Python and includes useful mappings for
some more complex PlantSim data types like tables.

## Example

```python
import os
import sys
import time

import plantsim.plantsim as ps
from plantsim.simulation_data import SimulationData

if __name__ == "__main__":
    # Create a new plant simulation
    sim = ps.PlantSim(version="23.2", license_type="Student")

    # Load a model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(script_dir, "..", "models")
    if not os.path.exists(models_path):
        print("Error: models folder not found")
        sys.exit(1)

    sim.model = os.path.join(models_path, "Prueba_conexion 2.spp")
    sim.path_context = ".Models.Model"
    sim.event_controller = "EventController"

    try:
        sim.initialize()
    except RuntimeError as e:
        print(e)
        sys.exit(1)


    experiments = [
        SimulationData(
            input_variables=["inspeccion", "inspeccion"],
            values=[False, True],
            output_variables=["simulacion", "simulacion"],
        ),
        SimulationData(
            input_variables=["inspeccion", "inspeccion"],
            values=[True, False],
            output_variables=["simulacion", "simulacion"],
        ),
    ]

    # Measure time for parallel execution
    start_time = time.time()
    parallel_results = sim.run_simulations_in_parallel(experiments)
    parallel_time = time.time() - start_time
    print(f"Parallel execution time: {parallel_time:.2f} seconds")

    # Measure time for sequential execution
    start_time = time.time()
    sequential_results = [sim.run_simulation(exp) for exp in experiments]
    sequential_time = time.time() - start_time
    print(f"Sequential execution time: {sequential_time:.2f} seconds")

    # Compare results
    print("Parallel results:")
    for result in parallel_results:
        print(result)

    print("Sequential results:")
    for result in sequential_results:
        print(result)
```

## Setup

### Requirements

You need a working version of Tecnomatix Plant Simulation installed on your system to be able to use this package.

## Author

This package is currently developed and maintained by Tilo van Ekeris and Constantin Waubert de Puiseau.

## Maintainers

This package is currently maintained by Lorenzo Ortiz Aneiros.

## Disclaimer

Tecnomatix, Plant Simulation etc. are brand names of Siemens. This is NOT an official Siemens product.

This software is provided "as is" without warranty of any kind. See the LICENSE file for details.

Furthermore, this software is currently actively developed and used in research so that there are no guarantees
for stable interfaces etc.

## Copyright

```
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
```
