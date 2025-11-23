import os
import json
import appdirs
import shutil

APP_NAME = "RandomWheelSpinner"
APP_AUTHOR = "User"

def get_data_dir():
    data_dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_config_path(name):
    safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
    return os.path.join(get_data_dir(), f"{safe_name}.json")

def save_config(name, entries):
    """
    Entries is a list of dicts: [{'label': 'Option 1', 'weight': 1, 'color': '#FF0000'}, ...]
    """
    path = get_config_path(name)
    data = {
        "name": name,
        "entries": entries
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_config(name):
    path = get_config_path(name)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)

def list_configs():
    data_dir = get_data_dir()
    configs = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            # We could read the file to get the real name, or just use the filename
            # Let's try to read the 'name' field from json, fallback to filename
            try:
                with open(os.path.join(data_dir, filename), 'r') as f:
                    data = json.load(f)
                    configs.append(data.get("name", filename[:-5]))
            except:
                configs.append(filename[:-5])
    return configs

def delete_config(name):
    path = get_config_path(name)
    if os.path.exists(path):
        os.remove(path)

def rename_config(old_name, new_name):
    old_path = get_config_path(old_name)
    new_path = get_config_path(new_name)
    
    if os.path.exists(old_path):
        # Load data to update the internal name
        with open(old_path, 'r') as f:
            data = json.load(f)
        
        data['name'] = new_name
        
        # Save to new path
        with open(new_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        # Remove old file if paths are different (case sensitivity might matter on some OS, but usually fine on Windows to just write then delete)
        if old_path != new_path:
            os.remove(old_path)
