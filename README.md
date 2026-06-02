# run_horton

Runs the horton part package developed by Cheng within the Stamm group. https://github.com/LISA-partitioning-method/horton-part

# How to set-up
## Installation
Should work effortlessly with the included conda environment constructor and activate it.
```
   # at top-level of this repo
   conda env update -f install/run_horton_env.yaml && conda activate run_horton
```
Install it as a pip package within the new (and activated) environment.
```
    # At top-level of this repo 
    python -m build && pip install . 
```
Test the installation
```
   pytest
```

## How to Run
```
    # activate the environment and run at any place (just provide valide path to fchk)
    run_horton_wpart.py --exc --wfn <path-to-.fchk-file>
```

## Test


## CamCASP basis sets
If CamCASP basis sets should be used, then a single-command installation is required (This requires camcasp to be installed and finds CamCASP basis sets through the $CAMCASP environment variable).
Go to the ```basis directory```. Find more information in the ```BASIS.md``` file.

## Tests
Run the tests in ```tests/basic_tests``` (the one with set2-11-avqz basis requires the generation of CamCASP basis sets as described in the previous paragraph).
