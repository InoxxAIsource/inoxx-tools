import json
import os
from datetime import datetime

class SnippetManager:
    def __init__(self):
        self.snippets_file = os.path.expanduser("~/.pyide-snippets.json")
        self.snippets = self.load_snippets()

    def load_snippets(self):
        try:
            if os.path.exists(self.snippets_file):
                with open(self.snippets_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}

    def save_snippets(self):
        try:
            with open(self.snippets_file, 'w') as f:
                json.dump(self.snippets, f, indent=4)
            return True
        except Exception as e:
            return f"Error saving snippets: {str(e)}"

    def add_snippet(self, name, code, description=""):
        try:
            self.snippets[name] = {
                "code": code,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            return self.save_snippets()
        except Exception as e:
            return f"Error adding snippet: {str(e)}"

    def get_snippet(self, name):
        try:
            snippet = self.snippets.get(name)
            if snippet:
                snippet["last_used"] = datetime.now().isoformat()
                self.save_snippets()
            return snippet
        except Exception as e:
            return f"Error retrieving snippet: {str(e)}"

    def delete_snippet(self, name):
        try:
            if name in self.snippets:
                del self.snippets[name]
                return self.save_snippets()
            return False
        except Exception as e:
            return f"Error deleting snippet: {str(e)}"

    def list_snippets(self):
        try:
            return [
                {
                    "name": name,
                    "description": data["description"],
                    "last_used": data["last_used"]
                }
                for name, data in self.snippets.items()
            ]
        except Exception as e:
            return f"Error listing snippets: {str(e)}"

    def search_snippets(self, query):
        try:
            results = []
            query = query.lower()
            for name, data in self.snippets.items():
                if (query in name.lower() or 
                    query in data["description"].lower() or 
                    query in data["code"].lower()):
                    results.append({
                        "name": name,
                        "description": data["description"],
                        "preview": data["code"][:100] + "..."
                    })
            return results
        except Exception as e:
            return f"Error searching snippets: {str(e)}"
