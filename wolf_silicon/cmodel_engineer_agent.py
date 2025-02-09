from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec
from codebase_tool import codebase_tool_help, list_codebase, view_file, create_file, overwrite_file, append_to_file, delete_file, search_codebase
from team_log_tool import write_my_log, view_team_log
import os

def compile_cmodel() -> str:
    """Compile the .cpp/.h in codebase into cmodel binary. Will return the last 4KB output of the compiler."""
    # 获取 codebase 中所有 .cpp 文件
    cpp_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.cpp'):
            cpp_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    result = WolfSiliconEnv.execute_command(f"g++  {' '.join(cpp_files)} -I{WolfSiliconEnv().get_workpath()} -o {WolfSiliconEnv().get_workpath()}/cmodel", 300)
    return result[-4*1024:]

def run_cmodel(timeout_sec:int=180) -> str:
    """Run the cmodel binary. Will return the last 4KB output of the cmodel."""
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/cmodel", timeout_sec)
    return result[-4*1024:]

cmodel_engineer_agent = AssistantAgent(
    "cmodel_engineer",
    tools=[review_spec, compile_cmodel, run_cmodel, codebase_tool_help, list_codebase, view_file, create_file, append_to_file, overwrite_file, delete_file, search_codebase, write_my_log, view_team_log],
    handoffs=["design_engineer"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 cmodel_engineer，职责是编写CModel代码""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 cmodel_engineer，精通 C++。你的职责是编写 CModel，并使用合适的工具高效完成任务。

    你的任务：

    1. 编写 CModel 代码（cmodel.cpp）

    * 使用【review_spec】工具查看 team_leader 提供的 spec.md 
    * 你可以编辑代码库，如果不知道如何操作，可以使用【codebase_tool_help】工具查看帮助
    * 在代码库中编写、修改用于构建 CModel 的 .cpp/.h 文件
    * 确保代码具有时钟精确性，并包含简洁的执行样例

    2. 编译和运行 CModel
    
    * 使用【compile_cmodel】将代码库中所有的 .cpp/.h 文件编译成一个 cmodel 可执行文件。
    * 可以使用【run_cmodel】运行 CModel。
    * 确保代码可以正确执行，且输出结果正确。
    
    3. 通知设计工程师（design_engineer）

    * 当你认为 CModel 建立完成，通知 design_engineer 进行后续工作。【transfer_to_design_engineer】

    4. 更新 CModel

    * team_leader 可能会要求你更新 CModel 代码，根据他们的要求及时更新。
    * 更新 CModel 后，也请你通知 design_engineer 进行后续工作。【transfer_to_design_engineer】

    5. 团队协作

    * 及时通过 【write_my_log】记录你的操作，以便团队其他成员了解你的工作进度。
    * 如果你遇到困难，可以求助于 team_leader 或其他团队成员。
    * 求助之前，请确保你已经记录了你的操作，并明确你的问题，使用【write_my_log】工具。
    * 如果你不知道该做什么，请【view_team_log】看看团队日志，里面可能有 team_leader 的指示。
    """
)