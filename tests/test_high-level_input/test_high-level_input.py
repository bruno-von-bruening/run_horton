# conftest.py
import subprocess,os
from functools import partial


tests_dir=os.path.realpath( os.path.join( os.path.dirname(__file__), '../') )
assert os.path.basename(tests_dir).strip('/').endswith('tests'), f"{os.path.realpath('.')}"


def run_script(inp, env=None, cwd=None):
    return subprocess.run(
        inp, shell=True,
        capture_output=True,
        # text=True,
        #env=env,
        cwd=cwd,
    )
def check(the_script: callable, inp, *args, **kwargs):
    results=the_script(inp,*args)
    assert results.returncode==0, f"Process failed\n  STOUD={results.stdout}\n  STDERR={results.stderr}"

run=partial(run_script,env='run_horton')
check_runner=partial(check, run)

def test_envo():
    check(run, f"conda run -n run_horton python -c \"import qcp_run_horton\"")

def test_simple_run():
    """ Fixed defaults etc"""
    loc=os.path.join(tests_dir, 'test_high-level_input', "quick_run")
    wfn_file=os.path.join(tests_dir,'example_files/produce_example_files/SP_PBE0_aug-cc-pvtz_h2o_nist.fchk')
    assert os.path.isfile(wfn_file), f"wfn provided is not file: {wfn}"
    cmd=f"run_horton_wpart.py --exc --wfn {wfn_file}"
    check(run, f"conda run -n run_horton pwd", pwd=tests_dir)





