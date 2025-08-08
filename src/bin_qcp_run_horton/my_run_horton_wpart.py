#!/usr/bin/env python
import os
import numpy as np
import os, sys , glob, re, json 

from qcp_run_horton.execution.main import main

exc_flag='exc'

def parser():
    # ARGPARSE
    description='DESCRIPTION:\nThis script runs partitioning according to the HORTON wpart extension'
    epilog=f"RUN INSTRUCTION:\nJust get a dummy input file by running:\n\t{__file__}\nChange the dummy input file and run\n\t"
    f"{__file__} -inp <*.inp>"
    import argparse
    par=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description=description, epilog=epilog,
    )
    # Add the arguments
    addar=par.add_argument
    addar('--inp', help='Input file (a default input file will be generated if function is run without options)')
    addar('--method', help=f"Partitioning method", default=None, choices=['MBIS','LISA'])
    addar('--basis', help=f"Partitioning method", default=None)
    addar('--wfn', type=str, help=f"Wave Function file")
    addar(f"--{exc_flag}", action='store_true', help=f"Execute the calculation")
    
    # Parse the args
    args=par.parse_args()
    def get_args(tag):
        return vars(args)[tag]
    inp_fi=args.inp
    method=args.method
    basis=args.basis
    if not basis is None:
        if basis.lower()=='none': basis=None
    execute=get_args(exc_flag)
    wfn_file=args.wfn

    main(inp_fi, method=method, basis=basis, wfn_file=wfn_file, execute=execute)
    if not execute:
        print(f"Execution flag was not activated. (activate with --{exc_flag})")

if __name__=='__main__':
    parser()

