#%%
import os 
import requests
from requests.auth import HTTPBasicAuth
import json
import logging 
import re 
import shutil 

def load_credentials(require_credentials=True):
    AUTH_USER = os.getenv('NEXTCLOUD_API_USERNAME')  # You can change this token as needed
    AUTH_PASSWORD = os.getenv('NEXTCLOUD_API_PASSWORD')  # You can change this token as needed
    BASE_URL = os.getenv('NEXTCLOUD_API_URL')

    if not all([AUTH_USER, AUTH_PASSWORD, BASE_URL]):
        if require_credentials:
            logging.error(json.dumps({"event_type": "missing_required_environment_variables", "url": BASE_URL, "user": AUTH_USER}))
            raise ValueError
        else:
            return None
    
    API_URL = f"{BASE_URL}/{AUTH_USER}"
    return { "USERNAME": AUTH_USER,  "PASSWORD": AUTH_PASSWORD, "URL": API_URL}


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
    
    remote_file_path = re.sub(f'^.+/files/', '', remote_file_path)  # Remove any leading path to ensure correct upload path
    
    # Construct the full URL
    url_dest = f"{credentials['URL']}/{remote_file_path}"
    
    try:
        # Get file size for progress reporting
        file_size = os.path.getsize(local_file_path)
        logging.info(json.dumps({"event_type": "upload_start", "file_size_mb": round(file_size / 1024 / 1024, 2), "remote_file_path": remote_file_path}))
        
        # Open the file in binary mode and stream it to avoid loading large files into memory
        with open(local_file_path, 'rb') as file:
            # PUT request with file content as body
            response = requests.put(
                url_dest,
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
    
    remote_folder_path = re.sub(f'^.+/files/', '', remote_folder_path)  # Remove any leading path to ensure correct upload path

    # Construct the full URL
    url_dest = f"{credentials['URL']}/{remote_folder_path}"
    
    try:
        response = requests.request(
            "MKCOL",
            url_dest,
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

def local_move_file(local_source_path, local_dest_path):
    """
    Move a local file to a destination path using shutil.move.
    
    Args:
        local_source_path (str): Path to the local source file
        local_dest_path (str): Destination path where the file should be moved
    
    Returns:
        bool: True if move was successful, False otherwise
    """
    # Check if local file exists
    if not os.path.exists(local_source_path):
        logging.error(json.dumps({"event_type": "move_failed_local_file_not_found", "local_source_path": local_source_path}))
        raise FileNotFoundError
    
    try:
        # Get file size for progress reporting
        file_size = os.path.getsize(local_source_path)
        logging.info(json.dumps({"event_type": "move_start", "file_size_mb": round(file_size / 1024 / 1024, 2), "local_dest_path": local_dest_path}))
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(local_dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        # Move the file
        shutil.copy2(local_source_path, local_dest_path)
        
        logging.info(json.dumps({"event_type": "move_success", "local_dest_path": local_dest_path}))
        return True
            
    except Exception as e:
        logging.error(json.dumps({"event_type": "move_failed_exception", "error": str(e), "local_dest_path": local_dest_path}))
        return False
