#!/usr/bin/env python
from qcp_run_horton.basis.load_camcasp_basis import load_camcasp_basis

def main(TYPE, basis_name):
    if TYPE=='CAMCASP':
        load_camcasp_basis(basis_type=basis_name)
    else:
        raise Exception(f"Unkown TYPE: {TYPE}")

if __name__=='__main__':
    import argparse; par=argparse.ArgumentParser(
        description=None,
        epilog=None,
        prog=None,
    )
    par.add_argument('TYPE', help=f"Type of basis, e.g. CAMCASP")
    par.add_argument('--basis_name', help=f"Name of basis, if CamCASP basis this specifies which basis to read")
    args=par.parse_args()

    TYPE=args.TYPE


    main(TYPE,basis_name='set2-11-avqz')
    #main(basis_type='set2')
