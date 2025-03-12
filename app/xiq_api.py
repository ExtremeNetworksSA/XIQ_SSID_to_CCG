#!/usr/bin/env python3
import logging
import os
import inspect
import sys
import json
import requests
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from requests.exceptions import HTTPError
from app.logger import logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger('SSID-CCG.xiq_api')

PATH = current_dir

class APICallFailedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class XIQ:
    def __init__(self, user_name=None, password=None, token=None):
        self.URL = "https://api.extremecloudiq.com"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self.proxyDict = {
            "http": "",
            "https": ""
        }
        if token:
            self.headers["Authorization"] = "Bearer " + token
        else:
            try:
                self.__getAccessToken(user_name, password)
            except ValueError as e:
                print(e)
                raise SystemExit
            except HTTPError as e:
               print(e)
               raise SystemExit
            except:
                log_msg = "Unknown Error: Failed to generate token for XIQ"
                logger.error(log_msg)
                print(log_msg)
                raise SystemExit   
        self.pageSize = 50  # setting to 50 because the radio-info API call has a limit of 50

    #API CALLS
    def __get_api_call(self, url):
        try:
            rawResponse = requests.get(url, headers= self.headers, verify=False, proxies=self.proxyDict)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise APICallFailedException(f'HTTP error occurred: {http_err}') 
        try:
            response = self.__checkResponse(rawResponse, url)
        except APICallFailedException as err:
            raise APICallFailedException(err)
        return response
    
    def __put_api_call(self, url, payload):
        try:
            rawResponse = requests.put(url, headers= self.headers, data=payload, verify=False, proxies=self.proxyDict)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise APICallFailedException(f'HTTP error occurred: {http_err}') 
        try:
            response = self.__checkResponse(rawResponse, url)
        except APICallFailedException as err:
            raise APICallFailedException(err)
        return response

    def __post_api_call(self, url, payload):
        try:
            rawResponse = requests.post(url, headers= self.headers, data=payload, verify=False, proxies=self.proxyDict)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise APICallFailedException(f'HTTP error occurred: {http_err}') 
        response = self.__checkResponse(rawResponse, url)
        return response
        
    def __delete_api_call(self, url):
        try:
            rawResponse = requests.delete(url, headers= self.headers, verify=False, proxies=self.proxyDict)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise APICallFailedException(f'HTTP error occurred: {http_err}') 
        response = self.__checkResponse(rawResponse, url)
        return response
    
    def __checkResponse(self, rawResponse, url):
        if rawResponse is None:
            log_msg = "ERROR: No response received from XIQ!"
            logger.error(log_msg)
            raise APICallFailedException(log_msg)
        if rawResponse.status_code not in [200, 201]:
            log_msg = f"Error - HTTP Status Code: {str(rawResponse.status_code)}"
            logger.error(f"{log_msg}")
            try:
                data = rawResponse.json()
            except json.JSONDecodeError:
                logger.warning(f"\t\t{rawResponse.text}")
            else:
                if 'error_message' in data:
                    logger.warning(f"\t\t{data['error_message']}")
                else:
                    logger.warning(f"\n\n{data}")
            raise APICallFailedException(log_msg) 
        try:
            data = rawResponse.json()
        except json.JSONDecodeError:
            logger.error(f"Unable to parse json data - {url} - HTTP Status Code: {str(rawResponse.status_code)}")
            raise APICallFailedException("Unable to parse the data from json, script cannot proceed")
        return data

    def __getAccessToken(self, user_name, password):
        info = "get XIQ token"
        success = 0
        url = self.URL + "/login"
        payload = json.dumps({"username": user_name, "password": password})
        try:
            data = self.__post_api_call(url=url,payload=payload)
        except APICallFailedException as e:
            print(f"API to {info} failed with {e}")
            print('script is exiting...')
            raise SystemExit
        except:
            print(f"API to {info} failed with unknown API error")
        else:
            success = 1
        if success != 1:
            print("failed to get XIQ token. Cannot continue to import")
            print("exiting script...")
            raise SystemExit
        
        if "access_token" in data:
            #print("Logged in and Got access token: " + data["access_token"])
            self.headers["Authorization"] = "Bearer " + data["access_token"]
            return 0

        else:
            log_msg = "Unknown Error: Unable to gain access token for XIQ"
            logger.warning(log_msg)
            raise ValueError(log_msg)

    def __collectDevicesBatch(self, page, sim=False):
        url = self.URL + "/devices?page=" + str(page) + "&limit=" + str(self.pageSize) 
        AP_list = []
        if sim:
            url = url + "&deviceTypes=SIMULATED"
        try:
            rawList = self.__get_api_call(url)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        pageCount = rawList['total_pages']
        for device in rawList['data']:
            if 'device_function' in device and device["device_function"] == "AP":
                AP_list.append(device)
        return pageCount, AP_list
    
    def __collectRadioInfo(self, page, device_ids):
        url = self.URL + "/devices/radio-information?page=" + str(page) + "&limit=" + str(self.pageSize) + "&deviceIds=" + ",".join(map(str, device_ids))
        try:
            rawList = self.__get_api_call(url)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        return rawList['data']

    # External functions

    ## Account Switch
    def collectManagedAccount(self):
        url = f"{self.URL}/account/external"
        try:
            data = self.__get_api_call(url)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        return data
    
    def setExternalAccount(self, viq_id):
        url = f"{self.URL}/account/:switch?id={viq_id}"
        payload = ''
        try:
            data = self.__post_api_call(url, payload)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        if "access_token" in data:
            self.headers["Authorization"] = "Bearer " + data["access_token"]
            return 0
        else:
            log_msg = f"Unknown Error: Unable to gain access token for XIQ - {viq_id}"
            raise APICallFailedException(log_msg)

    ## SSIDs
    def collectSSIDDeviceList(self, sim=False):
        page = 1
        pageCount = 1
        records = []
        ssid_data = {}
        while page <= pageCount:
            try:
                pageCount, device_list = self.__collectDevicesBatch(page, sim=sim)
            except APICallFailedException as e:
                raise APICallFailedException(e)
            # Extract device name
            device_mapping = {d["id"]: d["hostname"] for d in device_list}
            # Get a list of IDs from device_mapping
            device_ids = list(device_mapping.keys())
            try:
                rawSSID = self.__collectRadioInfo(page, device_ids)
            except APICallFailedException as e:
                raise APICallFailedException(e)
            # Extract SSIDs
            for device in rawSSID:
                device_id = device["device_id"]
                device_name = device_mapping.get(device_id, "Unknown")
                for radio in device["radios"]:
                    radio_name = radio["name"]
                    for wlan in radio.get("wlans", []):
                        # build CSV data
                        ssid = wlan["ssid"]
                        if not sim:
                            if "bssid" in wlan:
                                bssid = wlan["bssid"]
                            else:
                                bssid = "Unknown"
                        else:
                            bssid = "Simulated"
                        records.append({'device_name': device_name, "radio": radio_name, 'ssid': ssid, 'bssid': bssid})
                        # build CCG data
                        if ssid not in ssid_data:
                            ssid_data[ssid] = [device_id]
                        elif device_id not in ssid_data[ssid]:
                            ssid_data[ssid].append(device_id)

            print(f"completed page {page} of {pageCount} collecting Devices")
            page += 1

        return records, ssid_data
        
    ## CCG
    def collectCCG(self):
        page = 1
        pageCount = 1
        firstCall = True

        ccg_info = []
        while page <= pageCount:
            url = self.URL + "/ccgs?page=" + str(page) + "&limit=" + str(self.pageSize)
            try:
                rawList = self.__get_api_call(url)
            except APICallFailedException as e:
                raise APICallFailedException(e)
            ccg_info = ccg_info + rawList['data']

            if firstCall == True:
                pageCount = rawList['total_pages']
            print(f"completed page {page} of {rawList['total_pages']} collecting ccg_info")
            page = rawList['page'] + 1 
        return ccg_info
    
    def createCCG(self, ccg_name, description, device_ids):
        url = self.URL + "/ccgs"
        payload = json.dumps({"name": ccg_name, "description": description, "device_ids": device_ids})
        try:
            data = self.__post_api_call(url, payload)
        except APICallFailedException as e:
            raise APICallFailedException
        return data
    
    def updateCCG(self, ccg_id, ccg_name, description, device_ids):
        url = self.URL + "/ccgs/" + str(ccg_id)
        payload = json.dumps({"name": ccg_name, "description": description, "device_ids": device_ids})
        try:
            data = self.__put_api_call(url, payload)
        except APICallFailedException as e: 
            raise APICallFailedException
        return data