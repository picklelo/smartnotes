import os
import json
from typing import List, Dict
from smartnotes.ai.tool import tool

BASE_MEMORY_DIR = "memories"

def write_memory(key: str, value: str) -> str:
    """Write a memory to a file. The key can be nested using '/' as a separator."""
    path = os.path.join(BASE_MEMORY_DIR, key.replace('/', os.path.sep) + '.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump({"value": value}, f)
    return f"Memory '{key}' has been written."

def read_memory(key: str) -> str:
    """Read a memory from a file. The key can be nested using '/' as a separator."""
    path = os.path.join(BASE_MEMORY_DIR, key.replace('/', os.path.sep) + '.json')
    if not os.path.exists(path):
        return f"No memory found for '{key}'."
    with open(path, 'r') as f:
        data = json.load(f)
    return f"Memory for '{key}': {data['value']}"

def list_memories(start: str = "", depth: int = -1) -> List[Dict[str, str]]:
    """
    List memories starting from a given key prefix, up to a specified depth.
    
    Args:
        start (str): The starting prefix for the memory keys. Default is "" (root).
        depth (int): The maximum depth to search. -1 means no limit. Default is -1.
    
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing 'key' and 'preview' of the memory.
    """
    start_path = os.path.join(BASE_MEMORY_DIR, start.replace('/', os.path.sep))
    results = []

    for root, dirs, files in os.walk(start_path):
        if depth != -1 and root[len(start_path):].count(os.path.sep) >= depth:
            del dirs[:] # Don't go deeper
            continue

        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_MEMORY_DIR)
                key = rel_path[:-5].replace(os.path.sep, '/') # Remove .json and convert to key format
        
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    preview = data['value'][:50] + '...' if len(data['value']) > 50 else data['value']
        
            results.append({"key": key, "preview": preview})

    return results
