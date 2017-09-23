def mytestfunc(x, y):
    print x
    print y
    
def arrayArgs(*args):
    print args

import subprocess
print dir(subprocess)
subprocess.check_call('dir', shell=True)