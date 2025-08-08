
# v0.1.02 updated installation
Furthermore also change from qc_... to qcp_... pip package imports (in accordance to convention change).

# v0.01.03 new parser, rearrangments, and new installer


## Parser and main structure
New parser based on yaml instead of custom input file. Works together with corresponding pydantic Basemodel structure. 
(base of this is constructed in qcp_global_utils package)
This also involved rewriting of the main parts of the package and the run_horton_part.py executable.

## Rearrangment
Moved bin files and made them PATH-accessible through pip installation.

Replaced old path based imports with package based imports. 

Introduced ```util/``` folder for package. Should allow for better overview of key package loading and more compact python files.

## Formal Changes
Changed convention of ISA solution (allowing contracted gaussian) and regularised ISA solution to its corresponding ```qcp_objects``` class.
This has been largely done in the previous commit, but probably this was just a bug fix.
