import os
from wolf_silicon_env import WolfSiliconEnv
from typing import Tuple, List

def get_filename_and_mtime_by_ext(ext: List[str]) -> List[Tuple[str, float]]:
    """Get all files in workspace with the specified extension and their modification time."""
    workspace_path = WolfSiliconEnv().get_workpath()
    # 假设工作区是扁平的，没有文件夹
    files_and_mtime = []
    for file in os.listdir(workspace_path):
        if file.endswith(tuple(ext)):
            files_and_mtime.append((file, os.path.getmtime(os.path.join(workspace_path, file))))
    return files_and_mtime

def get_user_requirements_state() -> tuple[bool, float]:
    """Check if user_requirements.md exists and return the modification time of user_requirements.md."""
    workspace_path = WolfSiliconEnv().get_workpath()
    user_requirements_path = os.path.join(workspace_path, "user_requirements.md")
    if os.path.exists(user_requirements_path):
        return (True, os.path.getmtime(user_requirements_path))
    return (False, 0)

def get_spec_state() -> tuple[bool, float]:
    """Check if spec.md exists and return the modification time of spec.md."""
    workspace_path = WolfSiliconEnv().get_workpath()
    spec_path = os.path.join(workspace_path, "spec.md")
    if os.path.exists(spec_path):
        return True, os.path.getmtime(spec_path)
    return False, 0

def get_cmodel_state() -> tuple[bool, float]:
    """Check if .cpp/.h exists and return the modification time of cmodel.sv."""
    files_and_mtime = get_filename_and_mtime_by_ext([".cpp", ".h"])
    if len(files_and_mtime) == 0:
        return False, 0
    # 选出最新的更新时间返回
    return True, max(files_and_mtime, key=lambda x: x[1])[1]

def get_design_state() -> tuple[bool, float]:
    """Check if .v/.vh exists and return the modification time of design.v."""
    files_and_mtime = get_filename_and_mtime_by_ext([".v", ".vh"])
    if len(files_and_mtime) == 0:
        return False, 0
    # 选出最新的更新时间返回
    return True, max(files_and_mtime, key=lambda x: x[1])[1]

def get_verification_report_state() -> tuple[bool, float]:
    """Check if verification_report.md exists and return the modification time of verification_report.md."""
    workspace_path = WolfSiliconEnv().get_workpath()
    verification_report_path = os.path.join(workspace_path, "verification_report.md")
    if os.path.exists(verification_report_path):
        return True, os.path.getmtime(verification_report_path)
    return False, 0