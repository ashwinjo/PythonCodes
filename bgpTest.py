from ixnetwork_restpy import SessionAssistant, Files, BatchUpdate
from tabulate import tabulate
import tomli
import time


def get_session_assistant():
    """_summary_

    Returns:
        _type_: _description_
    """
    apiServerIp= CONFIG["dev"]["apiserver"]["ip"]
    apiServerUsername= CONFIG["dev"]["apiserver"]["username"]
    apiServerPassword = CONFIG["dev"]["apiserver"]["password"]
    sessionName = CONFIG["dev"]["apiserver"]["sessionname"]


    return SessionAssistant(IpAddress=apiServerIp, 
                            RestPort=None, 
                            UserName=apiServerUsername, 
                            Password=apiServerPassword, 
                            SessionName=sessionName, 
                            SessionId=None, 
                            ApiKey=None,
                            ClearConfig=False, 
                            LogLevel='info', 
                            LogFilename='restpy.log')

def start_protocols():
    IXNETWORK.StartAllProtocols(Arg1='sync')
    IXNETWORK.info('Verify protocol sessions\n')
    protocolSummary = SESSION_ASSISTANT.StatViewAssistant('Protocols Summary')
    protocolSummary.CheckCondition('Sessions Not Started', protocolSummary.EQUAL, 0)
    protocolSummary.CheckCondition('Sessions Down', protocolSummary.EQUAL, 0)
    IXNETWORK.info(protocolSummary)
    return f"Protocols Started and All Session Up"

def start_traffic():
    #Gets all configured Traffic Items
    IXNETWORK.Traffic.TrafficItem.find()
    IXNETWORK.Traffic.Apply()
    IXNETWORK.Traffic.StartStatelessTrafficBlocking()
    return "Traffic Running in session"

def stop_protocols():
    IXNETWORK.StopAllProtocols(Arg1='sync')
    return "All Protocols Stopped"

def stop_traffic():
    IXNETWORK.Traffic.StopStatelessTrafficBlocking()
    return "Traffic Stopped"

def connect_physical_ports_to_logical_ports():
    forceTakeOwnership = True
    portMap = SESSION_ASSISTANT.PortMapAssistant()
    portList = CONFIG["dev"]["ixiachassisports"]["ixiachassisports"]
    IXNETWORK.info(portList)

    for index,port in enumerate(portList):
        # Mapping physical ports to ports in the configuration
        portName = IXNETWORK.Vport.find()[index].Name
        portMap.Map(IpAddress=port[0], CardId=port[1], PortId=port[2], Name=portName)

    IXNETWORK.info(portList)
    # This true indicates
    portMap.Connect(forceTakeOwnership)

    return f"{portList} connected"

def load_config_file():
    ixiaconfigfilepath = CONFIG["dev"]["configFilePath"]
    IXNETWORK.info('Loading config file: {0}'.format(ixiaconfigfilepath))
    IXNETWORK.LoadConfig(Files(ixiaconfigfilepath, local_file=True))
    return f"{ixiaconfigfilepath} file loaded successfully"

def show_traffic_statistics():
    data = []
    flowStatistics = SESSION_ASSISTANT.StatViewAssistant('Flow Statistics')
    headers = ['Tx Port', 'Rx Port', 'Loss %', 'TxFrames', 'Rx Frames']
    for rowNumber,flowStat in enumerate(flowStatistics.Rows):
        data.append([flowStat['Tx Port'], flowStat['Rx Port'], flowStat['Loss %'], flowStat['Tx Frames'], flowStat['Rx Frames']])
    IXNETWORK.info(tabulate(data, headers=headers, tablefmt='grid'))
    
def deleteSession():
    SESSION_ASSISTANT.Session.remove()
    return f'Session {CONFIG["dev"]["apiserver"]["sessionname"]} Deleted'

def releasePorts():
    for vport in IXNETWORK.Vport.find():
        vport.ReleasePort()

def modify_traffic_framesize(typeOfTraffic=None):
    # FIXED , IMIX and RFC
    frameSize = IXNETWORK.Traffic.TrafficItem.find().ConfigElement.find().FrameSize.find()
    if typeOfTraffic.lower() == "fixed":
        frameSize.update(Type="fixed",  FixedSize=CONFIG["dev"]["test"]["fixedFrameSize"])
        IXNETWORK.Traffic.TrafficItem.find().Generate()
        IXNETWORK.info(f"Running {typeOfTraffic} Traffic of {CONFIG['dev']['test']['fixedFrameSize']}")
    if typeOfTraffic.lower() == "imix":
        frameSize.update(Type="presetDistribution",  PresetDistribution="imix")
        IXNETWORK.Traffic.TrafficItem.find().Generate()
        IXNETWORK.info(f"Running {typeOfTraffic} Traffic")

if __name__ == "__main__":
    with open("config.toml", mode="rb") as fp:
        CONFIG = tomli.load(fp)

    SESSION_ASSISTANT = get_session_assistant()
    IXNETWORK = SESSION_ASSISTANT.Ixnetwork

    load_config_file()
    connect_physical_ports_to_logical_ports()
    start_protocols()

    modify_traffic_framesize(typeOfTraffic="fixed")
    start_traffic()
    time.sleep(30)
    stop_traffic()
    show_traffic_statistics()

    modify_traffic_framesize(typeOfTraffic="imix")
    start_traffic()
    time.sleep(30)
    stop_traffic()
    show_traffic_statistics()









