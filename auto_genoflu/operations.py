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


def move_file(source_path, dest_path, use_nextcloud=False):
    """
    Move or upload a file to a destination path.
    
    Args:
        source_path (str): Path to the source file
        dest_path (str): Destination path where the file should be moved/uploaded
        use_nextcloud (bool): If True, use Nextcloud API upload; if False, use local move
    
    Returns:
        bool: True if operation was successful, False otherwise
    """
    # Check if source file exists
    if not os.path.exists(source_path):
        event_type = "upload_failed_local_file_not_found" if use_nextcloud else "move_failed_local_file_not_found"
        logging.error(json.dumps({"event_type": event_type, "source_path": source_path}))
        raise FileNotFoundError
    
    # Get file size for progress reporting
    file_size = os.path.getsize(source_path)
    
    if use_nextcloud:
        credentials = load_credentials()
        
        # Remove any leading path to ensure correct upload path
        dest_path = re.sub(f'^.+/files/', '', dest_path)
        
        # Construct the full URL
        url_dest = f"{credentials['URL']}/{dest_path}"
        
        try:
            logging.info(json.dumps({"event_type": "upload_start", "file_size_mb": round(file_size / 1024 / 1024, 2), "dest_path": dest_path}))
            
            # Open the file in binary mode and stream it to avoid loading large files into memory
            with open(source_path, 'rb') as file:
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
                logging.info(json.dumps({"event_type": "upload_success", "dest_path": dest_path}))
                return True
            else:
                logging.error(json.dumps({"event_type": "upload_failed_unexpected_response", "status_code": response.status_code}))
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(json.dumps({"event_type": "upload_failed_exception", "error": str(e), "dest_path": dest_path}))
            return False
    else:
        try:
            logging.info(json.dumps({"event_type": "move_start", "file_size_mb": round(file_size / 1024 / 1024, 2), "dest_path": dest_path}))
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Move the file
            shutil.copy2(source_path, dest_path)
            
            logging.info(json.dumps({"event_type": "move_success", "dest_path": dest_path}))
            return True
                
        except Exception as e:
            logging.error(json.dumps({"event_type": "move_failed_exception", "error": str(e), "dest_path": dest_path}))
            return False

def make_folder(dir_path, use_nextcloud=False):
    """
    Create a folder either locally or on Nextcloud.
    
    Args:
        dir_path (str): Path of the folder to be created
        use_nextcloud (bool): If True, use Nextcloud API; if False, use local creation
    
    Returns:
        bool: True if folder creation was successful, False otherwise
    """
    if use_nextcloud:
        credentials = load_credentials()
        
        # Remove any leading path to ensure correct upload path
        remote_folder_path = re.sub(f'^.+/files/', '', dir_path)

        # Construct the full URL
        url_dest = f"{credentials['URL']}/{remote_folder_path}"
        
        try:
            response = requests.request(
                "MKCOL",
                url_dest,
                auth=HTTPBasicAuth(credentials['USERNAME'], credentials['PASSWORD']),
            )
            
            if response.status_code in [201, 405, 409]:  # 201 Created, 405 Method Not Allowed (folder already exists)
                logging.info(json.dumps({"event_type": "folder_creation_success", "dir_path": dir_path}))
                return True
            else:
                logging.error(json.dumps({"event_type": "folder_creation_failed", "status_code": response.status_code, "dir_path": dir_path}))
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(json.dumps({"event_type": "folder_creation_exception", "error": str(e), "dir_path": dir_path}))
            return False
    else:
        try:
            os.makedirs(dir_path, exist_ok=True)
            logging.info(json.dumps({"event_type": "folder_creation_success", "dir_path": dir_path}))
            return True
        except Exception as e:
            logging.error(json.dumps({"event_type": "folder_creation_exception", "error": str(e), "dir_path": dir_path}))
            return False
