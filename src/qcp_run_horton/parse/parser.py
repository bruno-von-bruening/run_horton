from . import *

class input_file_reader:
    """ Probably similar to control class """
    extension=None
    source_file=None
    Lines=None
    di={}
    return_di={}
    options={}
    directory=None
    required=True
    @property
    def value_dict(self):
        values=[ (k,self.return_di[k]['value']) for k in self.return_di.keys() ]
        return dict(values)
    def __init__(self, input_file, valid_extensions, printout=False, directory=None, required=True) :
        self.required=required
        # Check if file, read, check if format correct
        self.directory=directory
        if not printout:
            self.source_file=input_file
            if not os.path.isfile(input_file):
                raise Exception(f"Passed input file {input_file} ({os.path.realpath(input_file)}). But does not exist.")
            # Read file based ond extension
            self.extension=input_file.split('.')[-1]
            if self.extension in valid_extensions:
                self.di=self.read_input()
            else:
                raise Exception(f"Extension {self.extension} is not in valid extensions:\n{valid_extensions}")
        else:
            self.source_file='dummy.inp'

        # Initialise the keys
        if type(self.options)!=dict:
            raise Exception(f"Change option to dictionary: gave type \'{type(self.options)}\'\n{self.options}")
        for k,entry in self.options.items():
            self.key_set(**entry,init=True)
        for key in self.di.keys():
            self.key_set(key,**self.di[key])

        if printout:
            out_name = self.printout()
            return out_name 

        # Check if complete
        for k in self.return_di.keys():
            entry=self.return_di[k]
            if entry['value']==None:
                if entry['required']==True and self.required:
                    raise Exception(f"You are required to provide an option for {k}")
                else:
                    entry['value']=entry['default']
            if type(entry['choices'])!=type(None):
                if not entry['value'] in entry['choices']:
                    raise Exception(f"You chose value for {k} as {entry['value']}, but has to be in {entry['choices']}")
        # Printout
        self.out_name=self.printout()
    def check_line_validity(self, Lines=None):
        # Line without comments, spaces, etc
        if type(Lines)==type(None):
            Lines=self.Lines
        di={}
        for i,l in enumerate(Lines):
            clean_line=l.split('#')[0]
            clean_line=clean_line.strip()
            vals= clean_line.split()
            if len(vals)==0:
                pass
            elif len(vals)==2:
                if vals[0] in di.keys():
                    raise Exception(f"Key {vals[0]} was alread read from line {di[vals[0]]['line']}.")
                di.update({ vals[0]:{"value":vals[1], 'line':l} })
            else:
                raise Exception(f"Problem on line \'{i+1}\' not two valid elements:\n{l}")
        return di
    def read_input(self,input_file=None):
        if input_file==None:
            input_file=self.source_file
        with open(input_file, 'r') as rd:
            self.Lines=rd.readlines()
        for l in self.Lines:
            di=self.check_line_validity()
        self.di=di
        return di
    def conversion(self,value,type_conv_ex=None):
        # Convert value if requested
        if value==None:
            conv_value=value
        else:
            if type_conv_ex!=None:
                if type_conv_ex in ['int','float','str']:
                    fun_di={
                        'int':int, 'float':float, 'str':str        
                    }
                    try:
                        conv_value=fun_di[type_conv_ex](value)
                    except Exception as e:
                        raise Exception(f"Could not convert {value} for type ''{type_conv_ex}', received Error:\n ''{e}''")
                elif type_conv_ex=='bool':
                    if value.upper()=='TRUE':
                        conv_value=True
                    elif value.upper()=='FALSE':
                        conv_value=False
                    else:
                        raise Exception(f"You provided {value} and conversion as '{type_conv_ex}', "+
                                f"but expect case-insensitive 'false; or 'true'")
                elif type_conv_ex=='file':
                    conv_value=os.path.realpath(value)
                    if not os.path.isfile(conv_value):
                        raise Exception(f"Could not read file {conv_value}")
                else:
                    raise Exception(f"Requested type conversion {type_conv_ex}, but not implemented yet")
            else:
                conv_value=value
        return conv_value
    def key_set(self,key,value=None,default=None,alt_nam=[],required=False, type_conv=None, init=False, description=None,
            line=None, choices=None):
        ''' Sets up dictionary entry from more compact function input '''

        # If setting up valid keys, only keys setup can be read in!
        if not init:
            matches=[]
            for k in self.return_di.keys():
                if key.upper() in [k]+self.return_di[k]['alt_nam']:
                    matches.append(k)
            if len(matches)==0:
                raise Exception(f"Key value \'{key}\' in controlfi {os.path.realpath(self.source_file)} is not recognized")
            elif len(matches)>1:
                raise Exception(f"Multiple different keys are assigned to {key} what is a coding mistake:{matches}")
            key=matches[0]
                

        # Convert value if requested
        # Check first if a conversion has been already setup
        key=key.upper()
        if isinstance(value, type(None)):
            conv_value=None
        elif isinstance(value, str):
            if value.strip().lower() in ['none']:
                conv_value=None
            else:
                if type_conv!=None:
                    type_conv_ex=type_conv
                elif key in self.return_di.keys():
                    type_conv_ex=self.return_di[key]['type_conv']
                else:
                    type_conv_ex=None
                conv_value=self.conversion(value,type_conv_ex=type_conv_ex)
        else:
            raise Exception(f"Unhandled data type {type(value)}\n{value}")

        if init:
            self.return_di.update({key.upper(): {'default':default, 'alt_nam':[x.upper() for x in alt_nam], 
                'required':required, 'value':conv_value,
                'type_conv':type_conv, 'description':description, 'choices':choices}})
        else:
            self.return_di[key.upper()].update({'value':conv_value})
    def printout(self):
        """Printouts the actual read in controls save in this clase"""
        # Append to name of original control file
        if type(self.directory)==type(None):
            direc=os.path.dirname(self.source_file)
        else:
            direc=self.directory
        out_name=os.path.join(direc, 'ACTUAL-INPUT_'+os.path.basename(self.source_file))
        with open(out_name, 'w') as wr:
            for k in self.return_di.keys():
                entry=self.return_di[k]
                if entry['description']==None:
                    desc='na'
                else:
                    desc=entry['description']
                if entry['required'] in ['TRUE',True,'True','true']:
                    required_str=' REQUIRED! '
                else:
                    required_str=''

                if type(entry['value'])!=type(None):
                    val=str(entry['value'])
                else:
                    val=str(entry['default'])
                wr.write(f"{k:<20} {val:>20} # {required_str} {desc}\n")
        self.out_name=out_name
        return out_name


class read_horton_wpart_file(input_file_reader):
    """ Read custom input file in psi4 format """
    options=[
        {'key':'METHOD',        'default':None, 'required':True, 'alt_nam':['METH'],
            'description':'Name of the method, eg LISA'}
        ,{'key':'WAVEFUNCTION',       'default':None, 'required':True, 'alt_nam':['WFN'],
            'description':'File path of wave function file'}
        ,{'key':'ANG_GRID_DENS',    'default':'insane', 
            'description':'Angular Density of grids'}
        ,{'key':'RAD_GRID_DENS',    'default':None, 'type_conv':'int',
            'description':'Radial Density of grids'}
        ,{'key':'MOMENTS_NAME', 'default':'moments.mom', 'alt_nam':['MOM_NAME','MOM_NAM','MOMENTS_FILE','MOM_FILE','MOM_FI'],
            'description':'Name of final moment file to be outputed'}
        ,{'key':'SOLUTION_NAME', 'default':'solution.json', 'alt_nam':['SOL_NAME', 'SOL_NAM','SOLUTION_FILE','SOL_FI', 'SOL_FILE'],
             'description':'FILE name of solution file to be outputed'}
        ,{'key':'KLD_HISTORY_NAME', 'default':'KLD_history.json', 
            'alt_nam':['KLD_HIS_NAME', 'KLD_HIS_NAM','KLD_HISTORY_FILE','KLD_HIS_FI', 'KLD_HIS_FILE'],
             'description':'FILE name of history file to be outputed'}
        ,{'key':'print_basis',    
            'description':'Only prints basis and exits'}
        ,{'key':'basis',        'default':None,    
            'description':'Basis, could use set2 from CamCASP, default is GISA set'}
    ]
    options=dict( [ (x['key'],x) for x  in options])
    valid_extensions=['inp']
    def __init__(self, input_file, options=None, printout=False, required=True):
        if options!=None:
            self.options=options
        super().__init__(input_file, self.valid_extensions, printout=printout, required=required)