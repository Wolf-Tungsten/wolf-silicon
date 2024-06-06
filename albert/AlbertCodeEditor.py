import os
from typing_extensions import ParamSpecArgs
import re

# 我们需要给 Albert 提供一个文字版的代码编辑器，这样他才能看到&编辑我们的代码
class AlbertCodeEditor(object):
    def __init__(self, src_root_path, read_only=False, window_height=47, search_window_height=6):
        self.src_root_path = os.path.realpath(src_root_path)
        self.read_only = read_only
        self.half_window_height = window_height // 2
        self.half_search_window_height = search_window_height // 2
        self.opened_file = None
        self.line_number = None
        self.editor_buffer = []

    def open(self, file_path, line_number=0):
        # 检查文件是否存在
        try:
            self._check_file_exist(file_path)
        except Exception as e:
            # 指定的文件并不存在，提示错误，同时给出项目中文件列表
            return f"{e}\n I'll show you the file list here, please check your file_path. \n {self.list_project_file()}"
        # 将文件装载到缓冲区
        self.opened_file = file_path
        with open(self._get_realpath(file_path), "r") as f:
            self.editor_buffer = f.readlines()
        # 显示文件内容
        return self.view(line_number)

    def view(self, line_number):
        # 检查是否已经打开了文件
        if self.opened_file is None:
            raise ValueError("Please open a file before viewing.")
        # 检查行号是否合法
        if line_number < 0 or line_number >= len(self.editor_buffer):
            raise ValueError(f"Invalid view line number, should be in [0, {len(self.editor_buffer)-1}].")
        self.line_number = line_number
        # 显示的代码范围是当前行的上下各半个窗口高度，在顶部和底部有边界处理
        # 当 line_number > 总长度 - window_height 时，输出的总是 [总长度 - window_height, 总长度)
        # 当 line_number < window_height / 2 时，输出的总是 [0, window_height)
        start_line_number = min(max(0, line_number - self.half_window_height), len(self.editor_buffer) - self.half_window_height * 2)
        end_line_number = min(len(self.editor_buffer), start_line_number + self.half_window_height * 2)
        output_buffer = ["[Read-Only Mode]"] if self.read_only else []
        output_buffer.append(f"- {self.opened_file} - line {start_line_number}~{end_line_number} of {len(self.editor_buffer)}\n\n")
        for i in range(start_line_number, end_line_number):
            if i == line_number:
                output_buffer.append(f">> {i+1}| {self.editor_buffer[i]}")
            else:
                output_buffer.append(f"   {i+1}| {self.editor_buffer[i]}")
        return "".join(output_buffer)

    def search_in_file(self, keyword, enable_regex=False):
        # 在打开的文件中搜索关键词，允许使用正则表达式
        # 输出格式为每个关键词出现位置的上下
        if self.opened_file is None:
            raise ValueError("Please open a file before search_in_file, or you can use the search_in_project function.")
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
        return "".join(output_buffer)
        
    def edit(self, start_line_number, end_line_number, new_code):
        if self.read_only:
            raise PermissionError("This editor is read-only.")
        # 编辑打开的文件的指定行范围
        if self.opened_file is None:
            raise ValueError("Please open a file before editing.")
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
        # 保存到文件
        self._save_buffer()
        return self.view(start_line_number)

    def list_project_file(self, start_path=None):
        if start_path is None:
            start_path = ""
        self._check_path_in_project(start_path)
        all_file_list = self._recursion_list_dir(self._get_realpath(start_path))
        # 去除 project_root 的前缀
        all_file_list = [f"- {path[len(self.src_root_path)+1:]}" for path in all_file_list]
        all_file_list = [f"Filelist of '{start_path}' :"] + all_file_list
        return "\n".join(all_file_list)

    def search_in_project(self, keyword, enable_regex=False, start_path=None):
        result = []
        # 获取完整文件列表
        if start_path is None:
            start_path = ""
            result.append(f"Search result(s) {keyword} of in project:")
        else:
            result.append(f"Search result(s) {keyword} in {start_path}")
        self._check_path_in_project(start_path)
        file_list = self._recursion_list_dir(self._get_realpath(start_path))
        for file in file_list:
            file_result = self._simplified_search(file, keyword, enable_regex)
            if len(file_result) > 0:
                result.append(f"\nFound {len(file_result)} result(s) in '{file}'")
                for i, line in file_result:
                    result.append(f"- line {i}: {line}")
        if len(result) == 1:
            return "No search result found."
        return "\n".join(result)

    def create_file(self, file_path, new_code):
        self._check_path_in_project(file_path)
        # 检查当前编辑器是否为只读模式
        if self.read_only:
            raise PermissionError("This editor is read-only.")
        # 检查文件是否已经存在
        if os.path.exists(self._get_realpath(file_path)):
            raise FileExistsError("File already exists.")
        # 创建文件
        self.opened_file = file_path
        # 如果 new_code 是字符串，转换为列表
        if isinstance(new_code, str):
            # 删除 \r 字符
            new_code = new_code.replace("\r", "")
            new_code = new_code.split("\n")
        # 替换指定行
        self.editor_buffer = new_code
        self.line_number = 0
        # 保存到文件
        self._save_buffer()
        return self.view(0)
        
    def _get_realpath(self, file_path):
        return os.path.realpath(os.path.join(self.src_root_path, file_path))

    def _check_path_in_project(self, request_path):
        # 检查两个路径的公共前缀是否为项目根路径
        common_prefix = os.path.commonprefix([self.src_root_path, self._get_realpath(request_path)])
        if common_prefix != self.src_root_path:
            raise PermissionError("Requested path not in project.")
    
    def _check_file_exist(self, request_file_path):
        self._check_path_in_project(request_file_path)
        realpath = self._get_realpath(request_file_path) 
        if os.path.exists(realpath):
            if os.path.isdir(realpath):
                raise IsADirectoryError("Requested path is a directory.")
        else:
            raise FileNotFoundError("File not found")
    
    def _save_buffer(self):
        with open(self._get_realpath(self.opened_file), "w") as f:
            f.write("".join(self.editor_buffer))
    
    def _recursion_list_dir(self, current_path):
        result = []
        for item in os.listdir(current_path):
            if item.startswith("."):
                continue
            subpath = os.path.join(current_path, item)
            if os.path.isdir(subpath):
                result += self._recursion_list_dir(subpath)
            else:
                result.append(subpath)
        return result

    def _simplified_search(self, file_path, keyword, enable_regex=False):
        self._check_path_in_project(file_path)
        file_path = self._get_realpath(file_path)
        # 打开 file_path 指定的文件
        with open(file_path, "r") as f:
            try:
                file_content = f.readlines() # 按行装载到 file_content 中
                search_result = []
                for i, line in enumerate(file_content):
                    line = line.strip()
                    if enable_regex:
                        if re.search(keyword, line):
                            search_result.append((i, line)) # 保存行号和行内容
                    else:
                        if keyword in line:
                            search_result.append((i, line))
                return search_result
            except:
                return []

if __name__ == "__main__":
    editor = AlbertCodeEditor("/Users/wolf/Develop/weighted-regression")
    print(editor.search_in_project("glm"))