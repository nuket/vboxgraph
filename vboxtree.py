# Pull in the VirtualBox Python API module.

import os, sys

#
# Pull in environment variables.
#
# C:\Program Files\Oracle\VirtualBox\sdk\install
#
VBOX_INSTALL_PATH = os.environ.get('VBOX_INSTALL_PATH', None)
VBOX_API_PATH     = os.path.join(VBOX_INSTALL_PATH, 'sdk', 'install')

# If there's no install path, we can't proceed.

if VBOX_INSTALL_PATH is None:       
    raise Exception("No VBOX_INSTALL_PATH defined, exiting.")

# Make sure VirtualBox Python API is on the path.

sys.path.append(VBOX_API_PATH)

# From vboxapisetup.py

def cleanupComCache():
    import shutil
    from distutils.sysconfig import get_python_lib
    comCache1 = os.path.join(get_python_lib(),'win32com', 'gen_py')
    comCache2 = os.path.join(os.environ.get("TEMP", "c:\\tmp"), 'gen_py')
    print "Cleaning COM cache at",comCache1,"and",comCache2
    shutil.rmtree(comCache1, True)
    shutil.rmtree(comCache2, True)



def main(argv):
    from vboxapi import VirtualBoxManager    

    # This is a VirtualBox COM/XPCOM API client, no data needed.    
    wrapper = VirtualBoxManager(None, None)

    # Get the VirtualBox manager    
    mgr  = wrapper.mgr    

    # Get the global VirtualBox object    
    vbox = wrapper.vbox    

    print "Running VirtualBox version %s" %(vbox.version)    

    pass

if __name__ == '__main__':
    main(sys.argv)
