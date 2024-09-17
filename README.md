# Python Package for communication with Siemens Tecnomatix Plant Simulation

This package enables the communication with the simulation software product "Tecnomatix Plant Simulation" by
Siemens. It speaks to PlantSim via the COM interface from within Python and includes useful mappings for
some more complex PlantSim data types like tables.


## Example

```python
import plantsim.plantsim as ps

plantsim.load_model('model.spp')
plantsim.set_path_context('.Models.Model')

table = sim.get_table(plantsim, 'DataTable')
print(table) 

new_table = pd.DataFrame({
    'Column1': [1, 2],
    'Column2': [3, 4]
})

sim.set_table("DataTable", new_table)
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
