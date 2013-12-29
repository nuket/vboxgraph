#
# Visualize the relationships between VirtualBox VMs.
# How do the virtual disk images derive from one another?
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

# Based on vboxshell.py

# def listMediaCmd(ctx, args):
#     if len(args) > 1:
#         verbose = int(args[1])
#     else:
#         verbose = False
        
#     hdds = ctx['global'].getArray(ctx['vb'], 'hardDisks')
#     print colCat(ctx, "Hard disks:")
#     for hdd in hdds:
#         if hdd.state != ctx['global'].constants.MediumState_Created:
#             hdd.refreshState()
#         print "   %s (%s)%s %s [logical %s]" % (colPath(ctx, hdd.location), hdd.format, optId(verbose, hdd.id), colSizeM(ctx, asSize(hdd.size, True)), colSizeM(ctx, asSize(hdd.logicalSize, True)))

#     dvds = ctx['global'].getArray(ctx['vb'], 'DVDImages')
#     print colCat(ctx, "CD/DVD disks:")
#     for dvd in dvds:
#         if dvd.state != ctx['global'].constants.MediumState_Created:
#             dvd.refreshState()
#         print "   %s (%s)%s %s" % (colPath(ctx, dvd.location), dvd.format, optId(verbose, dvd.id), colSizeM(ctx, asSize(dvd.size, True)))

#     floppys = ctx['global'].getArray(ctx['vb'], 'floppyImages')
#     print colCat(ctx, "Floppy disks:")
#     for floppy in floppys:
#         if floppy.state != ctx['global'].constants.MediumState_Created:
#             floppy.refreshState()
#         print "   %s (%s)%s %s" % (colPath(ctx, floppy.location), floppy.format, optId(verbose, floppy.id), colSizeM(ctx, asSize(floppy.size, True)))

#     return 0

def visualizeHdds(manager):
    # Returns a list of <win32com.gen_py.VirtualBox Type Library.IMedium instance at 0x62921096> objects.
    # 
    # It is a list of "base" disks, i.e. non-snapshot, which should be 
    # walkable down through their "differencing" children.
    hdds = manager.getArray(manager.vbox, 'hardDisks')

    for hdd in hdds:
        if hdd.state != manager.constants.MediumState_Created:
            hdd.refreshState()
        
        print "({format:4}) {id} {size:>5}MB {logicalSize:>5}MB {location}".format(location=hdd.location,
                                                                                   format=hdd.format,
                                                                                   id=hdd.id,
                                                                                   size=int(hdd.size) / (1024 * 1024),
                                                                                   logicalSize=int(hdd.logicalSize) / (1024 * 1024))

        #    %s (%s)%s %s [logical %s]" % hdd.location, hdd.format, hdd.id, hdd.size, hdd.logicalSize

    
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
