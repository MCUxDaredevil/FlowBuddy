from __future__ import annotations
from types import ModuleType
from typing import Callable, Optional
from importlib import import_module
import os

from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QKeySequence

from FileSystem import exists, ADDONS_FOLDER, ADDONS_NAME
from utils import HotKeys


add_ons: dict[str, ModuleType] = {}
add_on_paths: dict[str, ModuleType] = {}

currently_loading_module = None


def load_addons() -> None:
    """Loads all the modules from the ADDONs folder."""
    global add_ons, add_on_paths, currently_loading_module
    if exists(ADDONS_FOLDER):
        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(ADDONS_FOLDER):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                file_path = os.path.join(dir_path, f"{dir}.py")
                if os.path.isfile(file_path):  # If the .py file with same name as directory exists
                    # Import the module
                    module_name = f'{ADDONS_NAME}.{dir}.{dir}'
                    currently_loading_module = module_name
                    module = import_module(module_name)
                    currently_loading_module = None
                    add_ons[module_name] = module
                    add_on_paths[module_name] = file_path


class AddOnBase:
    system_tray_icon: QSystemTrayIcon = None # instance of QSystemTrayIcon will be assigned after initializing it
    instances: dict[str, AddOnBase] = {}
    
    def __new__(cls, name: Optional[str] = None):
        # returns the instance of currently loading addon module if available.
        # if not, returns the AddOnBase instance of module of given addon name.
        if currently_loading_module is not None:
            if name is not None:
                print("WARNING: name should not be specified when creating new instace from addon module.",
                      f"name of this instance is '{currently_loading_module}'.")
                
            if currently_loading_module in AddOnBase.instances:
                return AddOnBase.instances[currently_loading_module]
            new_instance = super().__new__(cls)
            new_instance._init()
            AddOnBase.instances[currently_loading_module] = new_instance
            return new_instance
        
        if name in AddOnBase.instances:
            return AddOnBase.instances[name]
        else: raise ValueError(f"'{name}' AddOn instance not found.")
    
    def _init(self):
        AddOnBase.instances[currently_loading_module] = self
        self.name = currently_loading_module
        self.activate_shortcut = None
        
    def activate(self):
        """Override this method to call when desktop widget is activated."""
        pass
    
    def set_activate_shortcut(self, key: QKeySequence) -> None:
        """Adds a global shortcut key to call the activate method."""
        self.activate_shortcut: QKeySequence = key
        HotKeys.add_global_shortcut(HotKeys.format_shortcut_string(key.toString()), self.activate)
    
    @staticmethod
    def set_shortcut(key: QKeySequence, function: Callable) -> None:
        """Adds a global shortcut"""
        HotKeys.add_global_shortcut(HotKeys.format_shortcut_string(key.toString()), function)
    
