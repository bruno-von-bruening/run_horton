#!/usr/bin/env python
from qcp_run_horton.basis.load_camcasp_basis import load_camcasp_basis

def main(TYPE, basis_name):
    if TYPE=='CAMCASP':
        load_camcasp_basis(basis_type=basis_name)
    else:
        raise Exception(f"Unkown TYPE: {TYPE}")

basis_flag=f"basis_name"
type_choices=['CAMCASP']
def parser():
    import argparse; par=argparse.ArgumentParser(
        description=None,
        epilog=None,
        prog=None,
    )
    par.add_argument('TYPE', help=f"Type of basis", choices=type_choices)
    par.add_argument(f"--{basis_flag}", help=f"Name of basis, if CamCASP basis this specifies which basis to read", default='set2-11-avqz')

    args=par.parse_args()
    def get_arg(tag):
        return vars(args)[tag]

    TYPE=args.TYPE
    basis_name=get_arg(basis_flag)
    main(TYPE,basis_name=basis_name)

if __name__=='__main__':
    parser()
