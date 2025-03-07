import os
import json
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.current_project = None
        self.project_config = {}
        self.project_file = ".pyide-project"

    def create_project(self, name, path):
        try:
            project_dir = os.path.join(path, name)
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
            
            self.project_config = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "python_version": "3.x",
                "last_opened_files": [],
                "snippets": []
            }
            
            self.save_project_config(project_dir)
            self.current_project = project_dir
            return True
        except Exception as e:
            return f"Error creating project: {str(e)}"

    def open_project(self, path=None):
        if path is None:
            path = os.getcwd()
        
        try:
            config_path = os.path.join(path, self.project_file)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.project_config = json.load(f)
                self.current_project = path
                return True
            return False
        except Exception as e:
            return f"Error opening project: {str(e)}"

    def save_project_config(self, path=None):
        if path is None:
            path = self.current_project
        
        try:
            config_path = os.path.join(path, self.project_file)
            with open(config_path, 'w') as f:
                json.dump(self.project_config, f, indent=4)
            return True
        except Exception as e:
            return f"Error saving project config: {str(e)}"

    def add_recent_file(self, filepath):
        if not self.current_project:
            return False
        
        recent_files = self.project_config.get("last_opened_files", [])
        if filepath in recent_files:
            recent_files.remove(filepath)
        recent_files.insert(0, filepath)
        self.project_config["last_opened_files"] = recent_files[:10]
        self.save_project_config()
        return True

    def get_recent_files(self):
        return self.project_config.get("last_opened_files", [])
