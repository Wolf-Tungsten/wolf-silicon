import os
from typing_extensions import ParamSpecArgs
import re

# 我们需要给 Albert 提供一个文字版的代码编辑器，这样他才能看到&编辑我们的代码
class AlbertCodeEditor(object):
    def __init__(self, project_root_path, window_height=47, search_window_height=6):
        self.project_root_path = os.path.realpath(project_root_path)
        self.half_window_height = window_height // 2
        self.half_search_window_height = search_window_height // 2
        self.opened_file = None
        self.line_number = None
        self.editor_buffer = []

    def open_and_view(self, file_path, line_number=0):
        # 检查文件是否存在
        self._check_file_exist(file_path)
        # 将文件装载到缓冲区
        self.opened_file = file_path
        with open(self._get_realpath(file_path), "r") as f:
            self.editor_buffer = f.readlines()
        # 显示文件内容
        return self.view(line_number)

    def view(self, line_number):
        # 检查是否已经打开了文件
        if self.opened_file is None:
            raise ValueError("No file opened.")
        # 检查行号是否合法
        if line_number < 0 or line_number >= len(self.editor_buffer):
            raise ValueError("Invalid view line number.")
        self.line_number = line_number
        # 显示的代码范围是当前行的上下各半个窗口高度，在顶部和底部有边界处理
        # 当 line_number > 总长度 - window_height 时，输出的总是 [总长度 - window_height, 总长度)
        # 当 line_number < window_height / 2 时，输出的总是 [0, window_height)
        start_line_number = min(max(0, line_number - self.half_window_height), len(self.editor_buffer) - self.half_window_height * 2)
        end_line_number = min(len(self.editor_buffer), start_line_number + self.half_window_height * 2)
        output_buffer = [f"- {self.opened_file} - line {start_line_number}~{end_line_number} of {len(self.editor_buffer)}\n\n"]
        for i in range(start_line_number, end_line_number):
            if i == line_number:
                output_buffer.append(f">> {i+1}| {self.editor_buffer[i]}")
            else:
                output_buffer.append(f"   {i+1}| {self.editor_buffer[i]}")
        return output_buffer.join("")

    def search(self, keyword, enable_regex=False):
        # 在打开的文件中搜索关键词，允许使用正则表达式
        # 输出格式为每个关键词出现位置的上下
        if self.opened_file is None:
            raise ValueError("No file opened.")
        search_result = []
        # 把包含关键词的行号加入到搜索结果中
        for i, line in enumerate(self.editor_buffer):
            if enable_regex:
                if re.search(keyword, line):
                    search_result.append(i)
            else:
                if keyword in line:
                    search_result.append(i)
        # 如果没有结果
        if len(search_result) == 0:
            return f"No search result for '{keyword}' in '{self.opened_file}'"
        # 输出的搜索结果是以搜索关键词为中心的上下半个窗口高度的范围
        output_buffer = [f"Found {len(search_result)} search result(s) for '{keyword}' in '{self.opened_file}' \n\n"]
        for i, line_number in search_result:
            output_buffer.append(f"---- result {i} / {len(search_result)} ----\n")
            start_line_number = max(0, line_number - self.half_search_window_height)
            end_line_number = min(len(self.editor_buffer), start_line_number + self.half_search_window_height * 2)
            for j in range(start_line_number, end_line_number):
                if j == line_number:
                    output_buffer.append(f">> {j+1}| {self.editor_buffer[j]}")
                else:
                    output_buffer.append(f"   {j+1}| {self.editor_buffer[j]}")
        return output_buffer.join("")
        
    def edit(self, start_line_number, end_line_number, new_code):
        # 编辑打开的文件的指定行范围
        if self.opened_file is None:
            raise ValueError("No file opened.")
        # 检查行号是否合法
        if start_line_number < 0 or end_line_number >= len(self.editor_buffer) or start_line_number > end_line_number:
            raise ValueError("Invalid edit line number.")
        # 如果 new_code 是字符串，转换为列表
        if isinstance(new_code, str):
            # 删除 \r 字符
            new_code = new_code.replace("\r", "")
            new_code = new_code.split("\n")
        # 替换指定行
        self.editor_buffer[start_line_number:end_line_number+1] = new_code
        # 输出替换后的内容
        return self.view(start_line_number)

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
    