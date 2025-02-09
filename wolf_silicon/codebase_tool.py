import os
from wolf_silicon_env import WolfSiliconEnv
def read_file_line_by_line(path):
    file_by_line = []
    with open(path, "r") as file:
        for line in file:
            # 去除行尾换行符
            line = line.rstrip()
            file_by_line.append(line)
    return file_by_line

def check_filename_security(file: str) -> bool:
    absolute_path = os.path.abspath(os.path.join(WolfSiliconEnv().get_workpath(), file))
    return os.path.commonpath([WolfSiliconEnv().get_workpath(), absolute_path]) == WolfSiliconEnv().get_workpath()

def get_absolute_path(file: str) -> str:
    return os.path.abspath(os.path.join(WolfSiliconEnv().get_workpath(), file))

def codebase_tool_help() -> str:
    """ Display the help message for codebase tools. """
    help_message = []
    help_message.append("# Codebase Tools")
    help_message.append("The codebase tools are designed to help you manage the codebase.")
    help_message.append("## List of Codebase Tools")
    help_message.append("* 【list_codebase】: List all files in the codebase and display the first 30 lines of each file.")
    help_message.append("* 【view_file】: View the specified range of lines in the file.")
    help_message.append("* 【create_file】: Create a new file with the specified content.")
    help_message.append("* 【overwrite_file】: Overwrite the specified file with the new content.")
    help_message.append("* 【append_to_file】: Append the new content to the end of the specified file.")
    help_message.append("* 【delete_file】: Delete the specified file.")
    help_message.append("* 【search_codebase】: Search the keyword in all files in the codebase and display the line containing the keyword.")
    return "\n".join(help_message)

def list_codebase() -> str:
    """ List all files in the codebase and display the first 30 lines of each file. """
    path = WolfSiliconEnv().get_workpath()
    codebase_view_list = []
    # 假设代码库是扁平的，没有文件夹
    # 获取 path 下所有的文件名，筛选出 .h、.cpp、.v、.sv、.vh、.svh、.md、.txt 文件
    roi_files = []
    for file in os.listdir(path):
        if file.endswith(('.h', '.cpp', '.v', '.sv', '.vh', '.svh')):
            roi_files.append(file)
    # 创建一个目录视图
    codebase_view_list.append("# List of Codebase Files")
    for file in roi_files:
        codebase_view_list.append(f"* {file}")
    # 逐个读取文件内容，每个文件创建一个章节，章节标题是文件名
    for file in roi_files:
        codebase_view_list.append(f"## {file}")
        file_by_line = read_file_line_by_line(os.path.join(path, file))
        amount_of_lines = len(file_by_line)
        # 提取前 30 行
        head_lines = file_by_line[:30]
        codebase_view_list.append(f"First {len(head_lines)} line(s) of {file} (Total: {amount_of_lines} lines):")
        codebase_view_list.append("\n```")
        codebase_view_list.extend(head_lines)
        codebase_view_list.append("```\n")
    # 为空提示
    if len(codebase_view_list) == 1:
        codebase_view_list[0] = "# No file in the codebase"
    return "\n".join(codebase_view_list)

def view_file(file: str, startline: int, endline: int) -> str:
    """ View the specified range [startline, endline) of lines in the file. (Note:linenumber start at 0) """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return f"File {file} not found."
    file_by_line = read_file_line_by_line(file_path)
    amount_of_lines = len(file_by_line)
    if startline < 0:
        startline = 0
    if endline > amount_of_lines:
        endline = amount_of_lines
    if startline >= endline:
        return f"Invalid line range, total line number of {file} is {amount_of_lines}."
    if endline - startline > 300:
        return f"Too many lines to display, please specify a range less than 300 lines in (0-{amount_of_lines})."
    # 提取指定行
    target_lines = file_by_line[startline:endline]
    file_list = []
    file_list.append(f"Lines {startline} to {endline} of {file} (Total: {amount_of_lines} lines):")
    file_list.append("\n```")
    file_list.extend(target_lines)
    file_list.append("```\n")
    return "\n".join(file_list)

def overwrite_file(file: str, content: str) -> str:
    """ Overwrite the specified file with the new content. """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    with open(os.path.join(file_path), "w") as f:
        f.write(content + "\n")
    return f"File {file} overwritten."

def create_file(file: str, content: str) -> str:
    """ Create a new file with the specified content. """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    with open(os.path.join(file_path), "w") as f:
        f.write(content + "\n")
    return "File created."

def insert_lines(file: str, linenumber: int, newlines: list[str]) -> str:
    """ Insert newlines start at linenumber (Note:linenumber start from 0) """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return f"File {file} not found."
    file_by_line = read_file_line_by_line(file_path)
    amount_of_lines = len(file_by_line)
    if linenumber < 0 or linenumber > amount_of_lines:
        return f"Invalid linenumber, total line number of {file} is {amount_of_lines}."
    #删除新行尾的回车
    newlines = [line.rstrip() for line in newlines]
    file_by_line = file_by_line[:linenumber] + newlines + file_by_line[linenumber:]
    with open(file_path, "w") as f:
        f.write("\n".join(file_by_line)+"\n")
    return f"After editing, please check contents surrounding your replacement\n" + view_file(file, linenumber-5, linenumber+len(newlines)+5)

def remove_lines(file: str, linenumber: int, count:int) -> str:
    """ Remove count lines start at linenumber (Note:linenumber start from 0) """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return f"File {file} not found."
    file_by_line = read_file_line_by_line(file_path)
    amount_of_lines = len(file_by_line)
    if linenumber < 0 or linenumber > amount_of_lines:
        return f"Invalid linenumber, total line number of {file} is {amount_of_lines}."
    if count < 0:
        return f"Invalid count, count should be positive."
    if linenumber + count > amount_of_lines:
        return f"Invalid count, count should be less than total line number of {file}."
    file_by_line = file_by_line[:linenumber] + file_by_line[linenumber+count:]
    with open(file_path, "w") as f:
        f.write("\n".join(file_by_line)+"\n")
    return f"After editing, please check contents surrounding your replacement\n" + view_file(file, linenumber-5, linenumber+5)

def append_to_file(file: str, content: str) -> str:
    """ Append the new content to the end of the specified file. """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    with open(os.path.join(file_path), "a") as f:
        f.write("\n" + content + "\n")
    return f"Content appended to file {file}."

def delete_file(file:str) -> str:
    """ Delete the specified file. """
    if not check_filename_security(file):
        return f"Illegal filename {file} out of codebase"
    file_path = get_absolute_path(file)
    os.remove(file_path)
    return f"File {file} deleted."
    
def search_codebase(keyword: str) -> str:
    """ Search the keyword in all files in the codebase and display the line containing the keyword. """
    path = WolfSiliconEnv().get_workpath()
    codebase_view_list = []
    # 假设代码库是扁平的，没有文件夹
    # 获取 path 下所有的文件名，筛选出 .h、.cpp、.v、.sv、.vh、.svh、.md、.txt 文件
    roi_files = []
    for file in os.listdir(path):
        if file.endswith(('.h', '.cpp', '.v', '.sv', '.vh', '.svh', '.md', '.txt')):
            roi_files.append(file)
    # 创建一个搜索结果视图
    codebase_view_list.append(f"# Search Result for keyword: {keyword}")
    for file in roi_files:
        file_by_line = read_file_line_by_line(os.path.join(path, file))
        # 获取行号和行内容（line_number, line_content）
        file_search_result = [(i, line) for i, line in enumerate(file_by_line) if keyword in line]
        if len(file_search_result) > 0:
            codebase_view_list.append(f"## In **{file}**")
            for line_number, line_content in file_search_result:
                codebase_view_list.append(f"* Line {line_number}: `{line_content}`")
    if len(codebase_view_list) == 1:
        codebase_view_list[0] = "# No search result found."
    return "\n".join(codebase_view_list)
