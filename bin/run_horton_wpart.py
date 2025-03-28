#!/usr/bin/env python
import os
import numpy as np
import os, sys , glob, re, json ; sys.path.insert(1, os.environ['SCR'])
import modules.mod_read_files as m_rf
import modules.mod_objects as m_obj
import modules.mod_utils as m_util

from qcp_run_horton.execution.util  import process_mp2_and_cc_file



from qcp_run_horton.execution.run_horton import run_horton

def input_file_parser(inp_fi, printout=False):
    reader=m_rf.read_horton_wpart_file(inp_fi, printout=printout)
    dic=reader.value_dict
    dic.update({'out_name':reader.out_name})
    dic_keys=list(dic.keys())
    keys=[]
    for key in keys:
        key=key.upper()
        if not key in dic_keys:
            raise Exception(f"Could not find entry for {key}, available keys are {dic_keys}")
    return dic
def setup_partitioning(inp_dic):
    """ Setup calculation, generate supplementary tags and objects """
    method=inp_dic['METHOD']
    basis_type=inp_dic['BASIS']
    if method in ['LISA']:
        ### Setup
        if type(basis_type)==type(None):
            basis=None
        elif isinstance(basis_type, str):
            camcasp_options=['set2','avqz','set2-11-avqz']
            from qcp_run_horton.basis.load_basis import load_basis
            basis=load_basis(basis_tag=basis_type)
        else:
            raise Exception(f"Invalid type for basis: {type(basis_type)}\n{basis_type}")
        solver='sc'
    elif method in ['MBIS']:
        solver='MBIS'
        basis=None
    else:
        raise Exception(f"Provided method \'{method}\', but is not implemented yet")
    if type(basis)==type(None):
        basis_key='GISA'
    else:
        basis_key=basis
    print(f"Using basis of type: {basis_key}")
    return {'solver':solver, 'basis':basis, 'method':method}

def main(inp_fi):
    """ Takes dictionary with all information about the run 
    1. Process and check the information
    2. Run horton
    """
    # In case no input has been provided, print a dummy input file, otherwise read it
    if type(inp_fi)==type(None):
        print(f"No input file provided, will printout a dummy options file (and do nothing)")
        printout=True
    else:
        assert os.path.isfile(inp_fi), f"Provided file {inp_fi} is not a file!"
        printout=False
    
    # Read the input file
    inp_dic=input_file_parser(inp_fi, printout=printout)
    
    if printout:
        quit(f"Printout was saved under {inp_dic['out_name']}")
    else:

        def process_information(inp_dic):
            wfn_fi,=[ inp_dic[k] for k in ['WAVEFUNCTION'] ]
            wfn_fi=m_util.process_file(wfn_fi)
            try:
                process_mp2_and_cc_file(wfn_fi, test=True)
            except Exception as ex:
                raise Exception(f"Test failed for {process_mp2_and_cc_file}: {ex}")
            wfn_fi=process_mp2_and_cc_file(wfn_fi)
            ang_grid_dens=inp_dic['ANG_GRID_DENS']
            setup_di=setup_partitioning(inp_dic)
            method, solver, basis = [ setup_di[k] for k in ['method','solver','basis' ] ]

            args=[ wfn_fi, method, basis ]
            kwargs=dict(
                solver=solver,
                ang_grid_dens=ang_grid_dens,
            )
            return args, kwargs
        def delete_tmp_files():
            for the_file in glob.glob('*'):
                if the_file.startswith('tmp.'):
                    os.popen(f"rm {the_file}")
                    print(f"Deleted temportary file \'{the_file}\'")
        
        args,kwargs=process_information(inp_dic)
        wfn_fi=args[0]
        try:
            run_horton(inp_dic, *args, **kwargs)
            delete_tmp_files()
        except Exception as ex:
            delete_tmp_files()
            raise Exception(ex)
        # Remove temporary file


if __name__=='__main__':
    
    
    # ARGPARSE
    description='DESCRIPTION:\nThis script runs partitioning according to the HORTON wpart extension'
    epilog=f"RUN INSTRUCTION:\nJust get a dummy input file by running:\n\t{__file__}\nChange the dummy input file and run\n\t"
    f"{__file__} -inp <*.inp>"
    import argparse
    par=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description=description, epilog=epilog,
    )
    # Add the arguments
    adar=par.add_argument
    adar('-inp', help='Input file')
    # Parse the args
    args=par.parse_args()
    inp_fi=args.inp

    main(inp_fi)

