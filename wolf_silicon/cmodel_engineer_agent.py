from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, check_team_log
import os

def write_cmodel(code:str) -> str:
    """将你的 cmodel 代码写入 cmodel.cpp 中，先前的内容将被覆盖
    注意：你的所有代码都应该在这个文件中，包括头文件和实现，请确保它能够通过g++编译并运行"""
    WolfSiliconEnv().common_write_file("cmodel.cpp", code)
    WolfSiliconEnv().update_log("cmodel_engineer", "Update cmodel.")
    return "Code updated."

def review_cmodel() -> str:
    """Review the cmodel code in cmodel.cpp."""
    return WolfSiliconEnv().common_read_file("cmodel.cpp")

def compile_cmodel() -> str:
    """Compile the cmodel code in cmodel.cpp into cmodel binary. Will return the last 4KB output of the compiler."""
    result = WolfSiliconEnv.execute_command(f"g++ {WolfSiliconEnv().get_workpath()}/cmodel.cpp -o {WolfSiliconEnv().get_workpath()}/cmodel", 300)
    return result[-4*1024:]

def run_cmodel(timeout_sec:int=180) -> str:
    """Run the cmodel binary. Will return the last 4KB output of the cmodel."""
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/cmodel", timeout_sec)
    return result[-4*1024:]

cmodel_engineer_agent = AssistantAgent(
    "cmodel_engineer",
    tools=[check_team_log, review_spec, write_cmodel, review_cmodel, compile_cmodel, run_cmodel],
    handoffs=["design_engineer"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 cmodel_engineer，职责是编写CModel代码""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 cmodel_engineer，精通 C++。你的职责是编写 CModel，并使用合适的工具高效完成任务。

    你的任务：

    1. 编写 CModel 代码（cmodel.cpp）

    * 使用【review_spec】工具查看 team_leader 提供的 spec.md 
    * 使用工具【write_cmodel】编写 CModel 代码
    * 如果需要，可使用【review_cmodel】工具查看已编写的代码
    * 确保代码具有时钟精确性，并包含简洁的执行样例

    2. 编译和运行 CModel
    
    * 可以使用【compile_cmodel】编译 CModel 代码。
    * 可以使用【run_cmodel】运行 CModel 代码。
    * 确保代码可以正确执行，且输出结果正确。
    
    3. 通知设计工程师（design_engineer）

    * 当你认为 CModel 建立完成，通知 design_engineer 进行后续工作。（Handoff to design_engineer）

    4. 更新 CModel

    * team_leader 可能会要求你更新 CModel 代码，根据他们的要求及时更新。
    * 更新 CModel 后，也请你通知 design_engineer 进行后续工作。（Handoff to design_engineer）

    注意：在任何时间，你可以使用【check_team_log】工具查看团队日志，以了解最新的项目进展，并及时调整你的工作。
    """
)