# run_horton

Runs the horton part package developed by Cheng within the Stamm group. https://github.com/LISA-partitioning-method/horton-part

# How to set-up
## Installation
Should work effortlessly with the included conda environment constructor.
But a installation from scratch may be more difficult and one has to tinker out the necessary versioning constraint between packages.


## CamCASP basis sets
If CamCASP basis sets should be used, then a single-command installation is required (This requires camcasp to be installed and finds CamCASP basis sets through the $CAMCASP environment variable).
Go to the ```basis directory```. Find more information in the ```BASIS.md``` file.

## Tests
Run the tests in ```tests/basic_tests``` (the one with set2-11-avqz basis requires the generation of CamCASP basis sets as described in the previous paragraph).
