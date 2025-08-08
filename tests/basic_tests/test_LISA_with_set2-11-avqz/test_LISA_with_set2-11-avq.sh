#!/bin/bash
conda init bash
conda activate run_horton_testAug
run_horton_wpart.py --method LISA --basis set2-11-avqz --wfn ../../example_files/pbe0_aug-cc-pVDZ_h2.fchk --exc
