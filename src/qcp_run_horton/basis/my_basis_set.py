from . import *

class atom_type_basis(BaseModel):
    #__class_config__=dict(arbitrary_types_allowed=True)
    atom_type: str
    basis: radial_atomic_basis
    def __init__(self,*args, **kwargs):
        if 'basis' in kwargs:
            kwargs.update({'basis':radial_atomic_basis(kwargs['basis'])})
        super().__init__(*args,**kwargs)
class basis_set_data(BaseModel):
    basis_set:List[atom_type_basis]
class basis_set(basis_set_data):
    def drop_to_file_structure(self, target_directory: directory|None=None, basis_set_name='dummy_basis', dump_format='yaml') -> file:

        # Process the location where to drop the basis set
        if target_directory is None:
            target_directory=os.getcwd()
        basis_home=os.path.join(target_directory, basis_set_name)
        if os.path.isdir(basis_home): shutil.rmtree(basis_home)
        os.mkdir(basis_home)

        @val_cal
        def dump(file:str, data, format:Literal['yaml','json']) -> file:
            if format in ['yaml']:
                dump_function=yaml.safe_dump
            elif format in ['json']:
                dump_function=json.dump
            else: raise Exception(f"Provided value for key cannot be interpreted: format=\'{format}\'")
            file=file+'.'+format

            with open(file, 'w') as wr:
                dump_function(data,wr)
            return file

        for x in self.basis_set:
            atom_type, basis = x.atom_type, x.basis
            file_name=os.path.join(basis_home, atom_type)
            basis_dump=basis.model_dump()
            dump( file_name, basis_dump, format='yaml')
        return file_name