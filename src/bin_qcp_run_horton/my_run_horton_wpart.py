#!/usr/bin/env python
import os
import numpy as np
import os, sys , glob, re, json 

from qcp_run_horton.execution.main import main

exc_flag='exc'
rad_grid_flag='rad_grid_dens'
ang_grid_flag='ang_grid_dens'

def parser():
    # ARGPARSE
    description='DESCRIPTION:\nThis script runs partitioning according to the HORTON wpart extension.'+ \
    'If not input file is provided a example input file will be printed. If excution is requested (see flag below) then defaults will be chosen'
    epilog=f"RUN INSTRUCTION:\nJust get a dummy input file by running:\n\t{__file__}\nChange the dummy input file and run\n\t"
    f"{__file__} -inp <*.inp>"
    import argparse
    par=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description=description, epilog=epilog,
    )
    # Add the arguments
    addar=par.add_argument
    addar('inp', nargs='?', help='Input file (a default input file will be generated if function is run without options)')
    addar('--method', help=f"Partitioning method", default=None, choices=['MBIS','LISA'])
    addar('--basis', help=f"Partitioning method", default=None)
    addar('--wfn', type=str, help=f"Wave Function file")
    addar(f"--{rad_grid_flag}", type=int, help=f"Radial Atomic Grid Density keyword")
    addar(f"--{ang_grid_flag}", type=str, help=f"Angular Grid Density keyword")
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
    rad_grid_dens=get_args(rad_grid_flag)
    ang_grid_dens=get_args(ang_grid_flag)
    wfn_file=args.wfn

    kwargs={}
    kwargs.update( take_defaults= (execute and inp_fi is None))


    main(inp_fi, method=method, basis=basis,
        rad_grid_dens=rad_grid_dens, ang_grid_dens=ang_grid_dens,
         wfn_file=wfn_file, execute=execute, **kwargs)
    if not execute:
        print(f"Execution flag was not activated. (activate with --{exc_flag})")

if __name__=='__main__':
    parser()

