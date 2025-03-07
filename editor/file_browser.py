import os
from rich.tree import Tree
from rich.text import Text

class FileBrowser:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.selected_file = None

    def get_file_tree(self):
        try:
            tree = Tree(Text("📁 " + os.path.basename(self.current_dir), style="bold blue"))
            self._build_tree(self.current_dir, tree)
            return tree
        except Exception as e:
            return Text(f"Error creating file tree: {str(e)}", style="red")

    def _build_tree(self, directory, tree):
        try:
            items = sorted(os.listdir(directory))
            for item in items:
                if item.startswith('.'):
                    continue

                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    branch = tree.add(Text(f"📁 {item}", style="blue"))
                    self._build_tree(full_path, branch)
                else:
                    if item.endswith('.py'):
                        icon = "🐍"
                        style = "green"
                    else:
                        icon = "📄"
                        style = "yellow"
                    tree.add(Text(f"{icon} {item}", style=style))
        except Exception as e:
            tree.add(Text(f"Error reading {directory}: {str(e)}", style="red"))

    def get_python_files(self):
        python_files = []
        try:
            for root, _, files in os.walk(self.current_dir):
                python_files.extend(
                    os.path.join(root, file)
                    for file in files
                    if file.endswith('.py')
                )
        except Exception as e:
            print(f"Error scanning Python files: {str(e)}")
        return python_files

    def change_directory(self, path):
        try:
            os.chdir(path)
            self.current_dir = os.getcwd()
            return True
        except Exception:
            return False

    def select_file(self, filepath):
        if os.path.isfile(filepath):
            self.selected_file = filepath
            return True
        return False

    def render(self):
        return self.get_file_tree()