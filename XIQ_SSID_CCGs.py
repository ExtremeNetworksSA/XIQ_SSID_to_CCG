#!/usr/bin/env python3
import logging
import os
import time
import inspect
import getpass
from app.logger import logger
from app.xiq_api import XIQ, APICallFailedException
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger('SSID-CCG.Main')


VERSION = "v1.0"


XIQ_API_token = ''

csv_file_name = 'SSID-Device.csv'

def prgood(content):
    print(f"[\033[0;32mOK\033[0m] {content}")

def prbad(content):
    print(f"[\033[0;91mXX\033[0m] {content}")

def exitOnEnter(errCode = 0):
    input("[--] Press Enter to exit...")
    exit(errCode)
    # 1 - user failed to log in
    # 2 - failed to collect SSID list
    # 3 - failed to collect CCG list
    # 4 - failed to create CSV
    # 5 - failed to update CCG
    # 6 - failed to create CCG
    
def yesNoLoop(question):
    validResponse = False
    while validResponse != True:
        response = input(f"{question} (y/n) ").lower()
        if response =='n' or response == 'no':
            response = 'n'
            validResponse = True
        elif response == 'y' or response == 'yes':
            response = 'y'
            validResponse = True
        elif response == 'q' or response == 'quit':
            print("[--]script is exiting....")
            exitOnEnter(errCode=0)
    return response

def login():
    ## Login 
    global x
    XIQ_username = input('Email: ')
    XIQ_password = getpass.getpass('Password: ')
    if XIQ_username and XIQ_password:
        x = XIQ(user_name=XIQ_username, password=XIQ_password)
    else:
        print("username or password was not entered")
        exitOnEnter(errCode=1)
    prgood(f"User {XIQ_username} logged in")
    time.sleep(2)

def checkDeviceList(ccg_device_ids, device_ids):
    return set(ccg_device_ids) == set(device_ids)

def createCSV(ssid_list):
    with open(csv_file_name, 'w') as f:
        f.write("Device Name,Radio,SSID,BSSID\n")
        for line in ssid_list:
            f.write(f"{line['device_name']},{line['radio']},{line['ssid']},{line['bssid']}\n")

### MAIN ###

logger.info("Starting Serial-CCG")
# log into XIQ
if not XIQ_API_token:
    print('Enter your XIQ login credentials for the account')
    login()
    logger.info("Logged in with credentials")
else:
    x = XIQ(token=XIQ_API_token)
    logger.info("Logged in with token")

# Get the list of device/SSIDs
## ssid_list for CSV
## SSID_data for JSON
try:
    ssid_list, ssid_data = x.collectSSIDDeviceList()
except APICallFailedException as e:
    logger.error(f"Failed to collect SSID list. {e}")
    prbad("Failed to collect SSID list")
    exitOnEnter(2)
logger.info(f"SSID list collected. {len(ssid_list)} BSSIDs found")

# Create CSV file from ssid_list
try:
    createCSV(ssid_list)
except APICallFailedException as e:
    logger.error(f"Failed to create CSV file. {e}")
    prbad("Failed to create CSV file")
    exitOnEnter(4)
logger.info("CSV file created")
prgood("CSV file created")

# Ask user if they want to continue with creating CCGs
response = yesNoLoop("Would you like to continue with creating/updating CCGs?")
if response == 'n':
    exitOnEnter(0)

# Create CCGs for each ssid from ssid_data
try:
    ccg_list = x.collectCCG()
except APICallFailedException as e:
    logger.error(f"Failed to collect CCGs. {e}")
    prbad("Failed to collect CCGs")
    exitOnEnter(3)
logger.info(f"CCGs collected. {len(ccg_list)} CCGs found")

for CCG_name in ssid_data:
    device_ids = ssid_data[CCG_name]
    ccg_exists = False
    for ccg in ccg_list:
        if ccg['name'] == CCG_name:
            logger.info(f"CCG {CCG_name} already exists")
            ccg_exists = True
            device_ids_match = checkDeviceList(ccg['device_ids'], device_ids)
            if not device_ids_match:
                logger.info(f"Device list in CCG {CCG_name} does not match the current list")
                logger.info(f"Updating device list in CCG {CCG_name}")
                try:
                    x.updateCCG(ccg['id'],CCG_name, ccg['description'], device_ids)
                except APICallFailedException as e:
                    logger.error(f"Failed to update CCG {CCG_name}. {e}")
                    prbad(f"Failed to update CCG {CCG_name}")
                    exitOnEnter(5)
                logger.info(f"Device list in CCG {CCG_name} updated with {len(device_ids)} devices")
                prgood(f"Device list in CCG {CCG_name} updated")
            else:
                logger.info(f"Device list in CCG {CCG_name} matches the current list")
            break

    if not ccg_exists:
        logger.info(f"Creating CCG {CCG_name}")
        try:
            x.createCCG(CCG_name, description=f"CCG for SSID {CCG_name}", device_ids=device_ids)
        except APICallFailedException as e:
            logger.error(f"Failed to create CCG {CCG_name}. {e}")
            prbad(f"Failed to create CCG {CCG_name}")
            exitOnEnter(6)
        logger.info(f"CCG {CCG_name} created with {len(device_ids)} devices")
        prgood(f"CCG {CCG_name} created.")

