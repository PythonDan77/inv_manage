import os

def asset_path(filename:str) -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "assets" , filename)