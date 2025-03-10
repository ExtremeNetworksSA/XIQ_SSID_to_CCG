# XIQ SSID to CCG Script
### XIQ_SSID_CCG.py

## <span style="color:purple"> Purpose </span>
This script is designed to interact with the ExtremeCloud IQ (XIQ) API to manage SSIDs and Client Connectivity Groups (CCGs). The script performs the following tasks:

1. Retrieves all devices and their radio information from the XIQ API.
2. Creates a CSV file containing the Access Points (APs), radio, SSID, and BSSID, allowing for filtering based on SSID.
3. Option to continue and add devices to CCG.
4. (optional) Ensures that a CCG exists for each SSID. If a CCG does not exist, the script creates it and adds all devices with the SSID to the new CCG.
5. (optional) If a CCG already exists, the script checks if any device with the SSID is not included in the CCG and adds it if necessary.

This process helps maintain accurate and up-to-date CCGs based on the SSIDs present on the devices.

## <span style="color:purple"> Needed Files </span>
The script uses other files. If these files are missing the script will not function. 
In the same folder as the script, there should be an ../app/ folder. This folder will contain 2 additional scripts, xiq_api.py and xiq_logger.py. After running the script a new file 'SSID_CCG_log.log' will be created.

- **XIQ_SSID_CCGs.py**: Main script to manage SSIDs and CCGs.
- **requirements.txt**: List of dependencies required for the script.
- **app/logger.py**: Logger module to handle logging.
- **app/xiq_api.py**: Module to interact with the XIQ API.

## <span style="color:purple"> Requirements </span>
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the 'pip install -r requirements.txt' if pip is used.

1. Clone the repository. Or download the zip file.
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## <span style="color:purple"> Usage </span>

Run the main script:
```sh
python XIQ_SSID_CCGs.py
```
This script will prompt for the VIQ username and password. The password will be hidden as you type. 
    - optionally you can add an API token to the script and bypass the login function.
After the CSV file is created, the script will ask if you would like to continue with creating/updating CCGs. You will need to enter y or yes to continue.