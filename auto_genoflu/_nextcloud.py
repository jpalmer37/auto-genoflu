#%%
import os 
import requests
from requests.auth import HTTPBasicAuth
import json
import logging 

def load_credentials():
    AUTH_USER = os.getenv('NEXTCLOUD_API_USERNAME')  # You can change this token as needed
    AUTH_PASSWORD = os.getenv('NEXTCLOUD_API_PASSWORD')  # You can change this token as needed
    URL = os.getenv('NEXTCLOUD_API_URL')

    if not all([AUTH_USER, AUTH_PASSWORD, URL]):
        logging.error(json.dumps({"event_type": "missing_required_environment_variables", "url": URL, "user": AUTH_USER}))
        raise ValueError
    
    return { "USERNAME": AUTH_USER,  "PASSWORD": AUTH_PASSWORD, "URL": URL}


def convert_nextcloud_path_to_local(path: str, nc_mount_path: str) -> str:
    if not path.startswith("nc://"):
        return path

    credentials = load_credentials()
    # Remove "nc://" prefix and construct full URL
    remote_file_path = path.replace("nc://", "")
    remote_file_path = os.path.join(nc_mount_path, credentials['USERNAME'], 'files', remote_file_path)
    return remote_file_path

def nc_upload_file(local_file_path, remote_file_path):
    """
    Upload a local file to Nextcloud using HTTP PUT.
    
    Args:
        local_file_path (str): Path to the local file to be uploaded
        remote_file_path (str): Target path on Nextcloud where the file should be stored
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    # Check if local file exists

    credentials = load_credentials()

    if not os.path.exists(local_file_path):
        logging.error(json.dumps({"event_type": "upload_failed_local_file_not_found", "local_file_path": local_file_path}))
        raise FileNotFoundError
    
    # Handle Nextcloud destination
    if not remote_file_path.startswith("nc://"):
        logging.error(json.dumps({"event_type": "upload_failed_invalid_remote_path", "remote_file_path": remote_file_path}))
        raise ValueError
    
    # Remove "nc://" prefix and construct full URL
    remote_file_path = remote_file_path.replace("nc://", "")
    remote_url_path = os.path.join(credentials['URL'], remote_file_path)
    
    try:
        # Get file size for progress reporting
        file_size = os.path.getsize(local_file_path)
        logging.info(json.dumps({"event_type": "upload_start", "file_size_kb": round(file_size / 1024, 2), "remote_file_path": remote_file_path}))
        
        # Open the file in binary mode and stream it to avoid loading large files into memory
        with open(local_file_path, 'rb') as file:
            # PUT request with file content as body
            response = requests.put(
                remote_url_path,
                auth=HTTPBasicAuth(credentials['USERNAME'], credentials['PASSWORD']),
                data=file,  # Stream file content
                headers={
                    'Content-Type': 'application/octet-stream',
                }
            )
            
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        if response.status_code in [200, 201, 204]:
            logging.info(json.dumps({"event_type": "upload_success", "remote_file_path": remote_file_path}))
            return True
        else:
            logging.error(json.dumps({"event_type": "upload_failed_unexpected_response", "status_code": response.status_code }))
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(json.dumps({"event_type": "upload_failed_exception", "error": str(e), "remote_file_path": remote_file_path}))
        return False

def nc_make_folder(remote_folder_path):
    """
    Create a folder on Nextcloud using WebDAV MKCOL method.
    
    Args:
        remote_folder_path (str): Path of the folder to be created on Nextcloud
    
    Returns:
        bool: True if folder creation was successful, False otherwise
    """
    credentials = load_credentials()

    # Handle Nextcloud destination
    if not remote_folder_path.startswith("nc://"):
        logging.error(json.dumps({"event_type": "folder_creation_failed_invalid_remote_path", "remote_folder_path": remote_folder_path}))
        raise ValueError
    
    # Remove "nc://" prefix and construct full URL
    remote_folder_path = remote_folder_path.replace("nc://", "")
    remote_url_path = os.path.join(credentials['URL'], remote_folder_path)
    
    try:
        response = requests.request(
            "MKCOL",
            remote_url_path,
            auth=HTTPBasicAuth(credentials['USERNAME'], credentials['PASSWORD']),
        )
        
        if response.status_code in [201, 405, 409]:  # 201 Created, 405 Method Not Allowed (folder already exists)
            logging.info(json.dumps({"event_type": "folder_creation_success", "remote_folder_path": remote_folder_path}))
            return True
        else:
            logging.error(json.dumps({"event_type": "folder_creation_failed", "status_code": response.status_code, "remote_folder_path": remote_folder_path}))
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(json.dumps({"event_type": "folder_creation_exception", "error": str(e), "remote_folder_path": remote_folder_path}))
        return False
