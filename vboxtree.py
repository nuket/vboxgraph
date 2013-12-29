#
# Visualize the relationships between VirtualBox VMs.
#
# How do the virtual disk images derive from one another?
# How are the disks attached to the various VMs?
# 
# (c) 2013 Max Vilimpoc
#
# Pull in the VirtualBox Python API module.

import os, sys

# Pull in environment variables.

VBOX_INSTALL_PATH = os.environ.get('VBOX_INSTALL_PATH', None)
VBOX_API_PATH     = os.path.join(VBOX_INSTALL_PATH, 'sdk', 'install')

# If there's no install path, we can't proceed.

if VBOX_INSTALL_PATH is None:       
    raise Exception("No VBOX_INSTALL_PATH defined, exiting.")

# Make sure VirtualBox Python API is on the path.

sys.path.append(VBOX_API_PATH)

# Based on vboxapisetup.py

def cleanupComCache():
    import shutil
    from distutils.sysconfig import get_python_lib
    comCache1 = os.path.join(get_python_lib(),'win32com', 'gen_py')
    comCache2 = os.path.join(os.environ.get("TEMP", "c:\\tmp"), 'gen_py')
    print "Cleaning COM cache at",comCache1,"and",comCache2
    shutil.rmtree(comCache1, True)
    shutil.rmtree(comCache2, True)

def constantValueToName(manager, value, valueType):
    values = manager.constants.all_values(valueType)

    for k, v in values.iteritems():
        if v == value:
            return k

    return None

def hddTypeName(manager, hddTypeInt):
    # types = manager.constants.all_values('MediumType')

    # for k, v in types.iteritems():
    #     if v == hddTypeInt:
    #         return k

    # return None

    return constantValueToName(manager, hddTypeInt, 'MediumType')

def hddStateName(manager, hddStateInt):
    # states = manager.constants.all_values('MediumState')

    # for k, v in states.iteritems():
    #     if v == hddStateInt:
    #         return k

    # return None

    return constantValueToName(manager, hddStateInt, 'MediumState')

def hddVariantName(manager, hddVariantInt):
    return constantValueToName(manager, hddVariantInt, 'MediumVariant')

def visualizeHdds(manager):
    # Returns a list of <win32com.gen_py.VirtualBox Type Library.IMedium instance> objects.
    # 
    # It is a list of "base" disks, i.e. non-snapshot, which should be 
    # walkable down through their "differencing" children.
    hdds = manager.getArray(manager.vbox, 'hardDisks')

    for hdd in hdds:
        if hdd.state != manager.constants.MediumState_Created:
            hdd.refreshState()
        
        print "({format:4}) {type:12} {state:12} {id} {size:>5}MB {logicalSize:>5}MB {location}".format(
            location=hdd.location,
            format=hdd.format,
            id=hdd.id,
            size=int(hdd.size) / (1024 * 1024),
            logicalSize=int(hdd.logicalSize) / (1024 * 1024),
            type=hddTypeName(manager, hdd.type),
            state=hddStateName(manager, hdd.state))
            # variant=hdd.variant) # hddVariantName(manager, hdd.variant))

    return hdds

def listMachines():
    # Returns a list of <win32com.gen_py.VirtualBox Type Library.IMachine instance> objects.
    # machines = manager.getArray(manager.vbox, 'machines')
    machines = manager.vbox.machines

    return machines

    
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
    from vboxapi import VirtualBoxManager
    manager = VirtualBoxManager(None, None)

    main(sys.argv)
