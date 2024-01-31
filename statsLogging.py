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


    session_assistant = SessionAssistant(IpAddress=apiServerIp, 
                            RestPort=None, 
                            UserName=apiServerUsername, 
                            Password=apiServerPassword, 
                            SessionName=sessionName, 
                            SessionId=None, 
                            ApiKey=None,
                            ClearConfig=False, 
                            LogLevel='info', 
                            LogFilename='restpy.log')

def enable_csv_logging():
    session_assistant = get_session_assistant()
    ixnetwork = session_assistant.Ixnetwork

    # assumes that the view exists and it sets up csv logging for the view
    ixnetwork.Statistics.find().EnableCsvLogging = True 
    ixnetwork.Statistics.find().PollInterval = 30
    

def download_csv_poll():
    session_assistant = get_session_assistant()
    ixnetwork = session_assistant.Ixnetwork
    csvFilePath = ixnetwork.Statistics.find().CsvFilePath
    # setup a local path
    local_csv_filename = "local.csv"

    # Hard coding for Flow Statistics. You can change this as per your use case
    session_assistant.Session.DownloadFile(f"{csvFilePath}/Flow Statistics.csv", local_csv_filename )

def disable_csv_logging():
    session_assistant = get_session_assistant()
    ixnetwork = session_assistant.Ixnetwork
    ixnetwork.Statistics.EnableCsvLogging = False

with open("config.toml", mode="rb") as fp:
        CONFIG = tomli.load(fp)