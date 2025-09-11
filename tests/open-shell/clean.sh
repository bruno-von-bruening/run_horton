#!/bin/bash
rm horton_wpart_controller_example.json horton_wpart_controller_example.yaml \
   kld_history.json *_charges.txt *_moments.txt moment.mom results.json solution.json
run_horton_wpart.py --method LISA --basis set2-11-avqz --wfn pbe0_aug-cc-pvtz_h2+.fchk --exc
