#
# Visualize the relationships between VirtualBox VMs.
#
# How do the virtual disk images derive from one another?
# How are the disks attached to the various VMs?
# 
# (c) 2013 Max Vilimpoc
#
# Pull in the VirtualBox Python API module.
#

import os, sys

# Pull in environment variables.

VBOX_INSTALL_PATH = os.environ.get('VBOX_INSTALL_PATH', None)
VBOX_API_PATH     = os.path.join(VBOX_INSTALL_PATH, 'sdk', 'install')

# If there's no install path, we can't proceed.

if VBOX_INSTALL_PATH is None:       
    raise Exception("No VBOX_INSTALL_PATH defined, exiting.")

# Make sure VirtualBox Python API is on the path.

sys.path.append(VBOX_API_PATH)

# Other constants

NO_MACHINE = 'NOT ATTACHED'

def constantValueToName(manager, value, valueType):
    values = manager.constants.all_values(valueType)

    for k, v in values.iteritems():
        if v == value:
            return k

    return None

def hddTypeName(manager, hddTypeInt):
    return constantValueToName(manager, hddTypeInt, 'MediumType')

def hddStateName(manager, hddStateInt):
    return constantValueToName(manager, hddStateInt, 'MediumState')

def hddVariantName(manager, hddVariantInt):
    return constantValueToName(manager, hddVariantInt, 'MediumVariant')

def hddInfo(manager, hdd):
    return "({format:4}) {type:12} {state:12} {id} {size:>5}MB {logicalSize:>5}MB {location}".format(
        location=hdd.location,
        format=hdd.format,
        id=hdd.id,
        size=int(hdd.size) / (1024 * 1024),
        logicalSize=int(hdd.logicalSize) / (1024 * 1024),
        type=hddTypeName(manager, hdd.type),
        state=hddStateName(manager, hdd.state))

def hddIsDifferencing(manager, hdd):
    if hdd.parent is not None:
        # print "Differencing: {0}".format(hdd.name)
        return True

    return False

def hddIsMultiAttach(manager, hdd):
    TYPES = manager.constants.all_values('MediumType')

    print "Hdd Type: {0}".format(hdd.type)

    if hdd.type == TYPES['MultiAttach']:
        return True

    return False

def stripBrackets(name):
    return name.replace('{', '').replace('}', '')


def hddMachineMapping(hddName, machineName, indent):
    INDENTATION = '\t' * indent

    return '{indentation}"{hddName}" -> "[{machineName}]";'.format(indentation=INDENTATION,
                                                                   hddName=hddName,
                                                                   machineName=machineName)

def hddName(manager, hdd):
    if hddIsDifferencing(manager, hdd):
        return stripBrackets(hdd.name)
    else:
        return stripBrackets('{hddName} ({hddId})'.format(hddName=hdd.name,
                                                          hddId=hdd.id[0:8]))

#
# Maps disks to machines.
#
def graphDiskMachineIds(manager, hdd, indent, output=[]):
    machineIds = hdd.machineIds

    # If the disk is a differencing disk, don't 
    # map it to a machine (makes the graph too noisy).
    if hddIsDifferencing(manager, hdd):
        return

    if machineIds is None:
        output.append(hddMachineMapping(hddName(manager, hdd), NO_MACHINE, indent))
        return

    for machineId in machineIds:
        machine = manager.vbox.FindMachine(machineId)

        machineName = stripBrackets(machine.name)

        output.append(hddMachineMapping(hddName(manager, hdd), machineName, indent))

#
# Recursively descend into the virtual disk tree.
#
def graphDiskChildren(manager, hdd, indent, output=[]):
    INDENTATION = '\t' * indent

    for hdd in hdd.children:
        parentName = hddName(manager, hdd.parent)
        childName  = hddName(manager, hdd)

        # if hddIsMultiAttach(manager, hdd):
        #     hddType = 'MultiAttach'
        # else:
        #     hddType = ''

        output.append('{indentation}"{child}" -> "{parent}";'.format(indentation=INDENTATION,
                                                                     parent=parentName,
                                                                     child=childName))
                                                             

        graphDiskMachineIds(manager, hdd, indent, output)
        graphDiskChildren(manager, hdd, indent + 1, output)

# Returns a list of <win32com.gen_py.VirtualBox Type Library.IMedium instance> objects.
# 
# It is a list of "base" disks, i.e. non-snapshot, which should be 
# walkable down through their "differencing" children.
def visualizeHdds(manager, output=[]):
    hdds = manager.getArray(manager.vbox, 'hardDisks')

    for hdd in hdds:
        if hdd.state != manager.constants.MediumState_Created:
            hdd.refreshState()
        
        graphDiskMachineIds(manager, hdd, 0, output)
        graphDiskChildren(manager, hdd, 0, output)

    # return hdds

# def listMachines():
#     # Returns a list of <win32com.gen_py.VirtualBox Type Library.IMachine instance> objects.
#     # machines = manager.getArray(manager.vbox, 'machines')
#     machines = manager.vbox.machines

#     return machines


def formatMachineName(name):
    INDENTATION = '\t'

    return '{indentation}"[{name}]";'.format(indentation=INDENTATION,
                                             name=name)


def graphMachineCluster(manager, output=[]):
    # print 'subgraph cluster_machines {'

    names = [formatMachineName(machine.name) for machine in manager.vbox.machines]
    names.append(formatMachineName(NO_MACHINE))

    output.extend(names)
    
    # print '\n'.join(sorted(names))

    # for machine in manager.vbox.machines:
    #     print formatMachineName(machine.name)

    # print formatMachineName(NO_MACHINE)

    # print '}'        

def isHardDisk(manager, deviceType):
    TYPES = manager.constants.all_values('DeviceType')

    # print "Device Type: {0}".format(deviceType)

    if deviceType == TYPES['HardDisk']:
        return True

    return False

def machineHddMapping(machineName, hddName, indent):
    INDENTATION = '\t' * indent

    return '{indentation}"[{machineName}]" -> "{hddName}";'.format(indentation=INDENTATION,
                                                                   hddName=hddName,
                                                                   machineName=machineName)


def graphLatestVdi(manager, output=[]):
    for machine in manager.vbox.machines:
        attachments = machine.mediumAttachments

        if len(attachments):
            for A in attachments:
                try:
                    if isHardDisk(manager, A.medium.deviceType):
                        output.append('edge [color=red];')
                        # output.append(machineHddMapping(machine.name, stripBrackets(hddName), 0))
                        output.append(hddMachineMapping(hddName(manager, A.medium), machine.name, 0))

                except AttributeError:
                    continue

def graphDriveCluster(manager, output=[]):
    hdds = manager.getArray(manager.vbox, 'hardDisks')

    for hdd in hdds:
        if hdd.state != manager.constants.MediumState_Created:
            hdd.refreshState()

        output.append('"{hddName}"'.format(hddName=stripBrackets(hdd.name)))

def outputEverything(manager, renderables={}):
    from jinja2 import Template
    
    template = Template(open('index.template.html', 'r').read())
    return template.render(renderables)


    
if __name__ == '__main__':
    from vboxapi import VirtualBoxManager
    manager = VirtualBoxManager(None, None)

    # print "Running VirtualBox version %s" %(manager.vbox.version)

    hddGraph = []
    visualizeHdds(manager, hddGraph)
    
    machineCluster = []
    graphMachineCluster(manager, machineCluster)

    latestAttachedDisks = []
    graphLatestVdi(manager, latestAttachedDisks)

    driveCluster = []
    graphDriveCluster(manager, driveCluster)

    # Plug the variables into the template and print
    everything = outputEverything(manager, {'cluster_machines':       '\n'.join(machineCluster),
                                            'disk_hierarchy':         '\n'.join(hddGraph),
                                            'current_attachment_map': '\n'.join(latestAttachedDisks)})
                                            # 'cluster_root_drives':    '\n'.join(driveCluster)})
    
