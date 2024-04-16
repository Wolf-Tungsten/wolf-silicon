import os
from typing_extensions import ParamSpecArgs

# 我们需要给 Albert 提供一个文字版的代码编辑器，这样他才能看到&编辑我们的代码
class AlbertCodeEditor(object):
    def __init__(self, project_root_path, window_height=47):
        self.project_root_path = os.path.realpath(project_root_path)
        self.window_height = window_height
        self.opened_file = None
        self.line_number = None
        self.editor_buffer = []

    def open_and_view(self, file_path, start_line_number=0):
        # 检查文件是否存在
        self._check_file_exist(file_path)
        # 将文件装载到缓冲区
        self.opened_file = file_path
        with open(self._get_realpath(file_path), "r") as f:
            self.editor_buffer = f.readlines()
        # 显示文件内容
        return self.view(start_line_number)

    def view(self, start_line_number):
        # 检查是否已经打开了文件
        if self.opened_file is None:
            raise ValueError("No file opened.")
        # 检查行号是否合法
        if start_line_number < 0 or start_line_number >= len(self.editor_buffer):
            raise ValueError("Invalid start line number.")
        self.line_number = start_line_number
        end_line_number = min(len(self.editor_buffer), start_line_number + self.window_height)
        self.line_number = start_line_number
        output_buffer = [f"- {self.opened_file} - line {self.line_number}~{end_line_number} of {len(self.editor_buffer)}\n\n"]
        for i in range(start_line_number, end_line_number):
            output_buffer.append(f"{i+1}: {self.editor_buffer[i]}")
        return output_buffer.join("")

    def search(self, keyword, enable_regex=False):
        pass

    def edit(self, start_line_number, end_line_number, new_code):
        pass

    def save(self):
        pass

    def list_dir_tree(self, start_path=None):
        pass

    def search_in_tree(self, keyword, enable_regex=False, start_path=None):
        pass

    def create_file(self, file_path):
        pass

    def _get_realpath(self, file_path):
        return os.path.realpath(os.path.join(self.project_root_path, file_path))

    def _check_path_in_project(self, request_path):
        # 检查两个路径的公共前缀是否为项目根路径
        common_prefix = os.path.commonprefix([self.project_root_path, self._get_realpath(request_path)])
        if common_prefix != self.project_root_path:
            raise PermissionError("Requested path not in project.")
    
    def _check_file_exist(self, request_file_path):
        self._check_path_in_project(request_file_path)
        realpath = self._get_realpath(request_file_path) 
        if os.path.exists(realpath):
            if os.path.isdir(realpath):
                raise IsADirectoryError("Requested path is a directory.")
        else:
            raise FileNotFoundError("File not found")
    