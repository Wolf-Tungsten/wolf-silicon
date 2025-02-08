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
    result = os.popen(f"g++ {WolfSiliconEnv().get_workpath()}/cmodel.cpp -o {WolfSiliconEnv().get_workpath()}/cmodel").read()
    return result[-4*1024:]

def run_cmodel(timeout_sec:int=180) -> str:
    """Run the cmodel binary. Will return the last 4KB output of the cmodel."""
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/cmodel", timeout_sec)
    return result[-4*1024:]

cmodel_engineer_agent = AssistantAgent(
    name="cmodel_engineer",
    tools=[check_team_log, review_spec, write_cmodel, review_cmodel, compile_cmodel, run_cmodel],
    handsoff=["design_engineer"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 cmodel_engineer，职责是将 team_leader 的 spec.md 转换为C++建模代码，供 design_engineer 和 verification_engineer 参考""",
    system_message="""你是硬件IP设计团队 “Wolf-Silicon” 的 cmodel_engineer，你精通C++，你的职责如下，请根据团队日志（使用工具查看）判断当前项目进度，选择合适的工作进行开展：
    - 根据 team_leader 的 spec.md 编写 cmodel.cpp 代码：
    -- 要求 cmodel 代码时钟精确，包含简洁的执行样例；
    -- 要求 cmodel 代码可通过编译并正确执行。
    - 你可以反复迭代你的 cmodel
    - cmodel 确认无误后，你调动 design_engineer 推动后续工作，这是你的**最终目标**
    - 如果 spec.md 发生了更新，你需要及时调整 cmodel 代码，并重新编译、运行，然后通知 design_engineer
    你可以使用 "check_team_log", "review_spec", "write_cmodel", "review_cmodel", "compile_cmodel", "run_cmodel" 这些工具来帮助你完成工作。
    """
)