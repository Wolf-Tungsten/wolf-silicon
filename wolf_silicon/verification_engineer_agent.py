from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, check_team_log
from cmodel_engineer_agent import review_cmodel, run_cmodel
from design_engineer_agent import review_design
import os

def write_testbench(code:str) -> str:
    """将你提供的 testbench 代码写入 tb.sv 中，先前的内容将被覆盖
    注意：你的所有代码都应该在这个文件中，不要使用其他文件"""
    WolfSiliconEnv().common_write_file("tb.sv", code+"\n")
    WolfSiliconEnv().update_log("verification_engineer", "Update testbench.")
    return "Code updated."

def review_testbench() -> str:
    """Review the testbench code in tb.sv."""
    return WolfSiliconEnv().common_read_file("tb.sv")

def compile_testbench() -> str:
    """调用 Verilator，将你的 tb.sv 和 dut.v 编译为可执行文件 Vtb，返回编译器的输出(最多4KB)"""
    result = WolfSiliconEnv.execute_command(f"verilator --binary --build -Wall --timing {WolfSiliconEnv().get_workpath()}/tb.sv {WolfSiliconEnv().get_workpath()}/dut.v --sv -CFLAGS \"-fcoroutines\" --Mdir {WolfSiliconEnv().get_workpath()}/obj_dir", 300)
    return result[-4*1024:]


def run_testbench(timeout_sec:int=300) -> str:
    """Run the testbench binary. Will return the last 4KB output of the testbench. """
    # 检查是否已经编译
    if not os.path.exists(f"{WolfSiliconEnv().get_workpath()}/obj_dir/Vtb"):
        return "There is no Vtb executable. Please check if compile successfully."
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/obj_dir/Vtb", timeout_sec)
    return result[-4*1024:]

def write_verification_summary(summary:str, overwrite:bool=False) -> str:
    """将你的验证总结写入 verification_summary.md 中，你可以选择覆盖之前的内容或追加到文件末尾"""
    WolfSiliconEnv().common_write_file("verification_summary.md", summary, overwrite)
    if overwrite:
        WolfSiliconEnv().update_log("verification_engineer", "Overwrite verification_summary.md")
    else:
        WolfSiliconEnv().update_log("verification_engineer", "Append into verification_summary.md")
    return "Verification Summary updated."

verification_engineer_agent = AssistantAgent(
    "verification_engineer",
    tools=[check_team_log, review_spec, review_cmodel, run_cmodel, review_design, write_testbench, review_testbench, compile_testbench, run_testbench, write_verification_summary],
    reflect_on_tool_use=True,
    handoffs=["team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 verification engineer，职责是根据 spec、cmodel、design 开展验证，编写验证报告""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 verification engineer，精通 SystemVerilog。你的职责是验证已有设计，并使用适当的工具高效完成任务。

    你的任务：

    1. **编写 Testbench 代码**

    * 使用工具【review_spec】、【review_cmodel】【run_cmodel】和【review_design】查看 spec、cmodel 和 design。
    * 根据这些信息，使用工具【write_testbench】编写 testbench 代码，确保顶层模块名称为 `tb`。
    * 如果需要，你可以使用【review_testbench】查看已编写的 testbench 代码。
    * 你的验证代码需要检查设计的功能正确性，如果你玩忽职守，可能会导致设计缺陷未被发现。
    * 你需要用断言来验证，确保设计的功能正确性。

    2. **分析 Testbench 代码**

    * 使用【review_testbench】查看已编写的 testbench 代码
    * 对照设计文档，判断你的 testbench 是否进行了有效检查
    * 如果发现问题，你需要重新编写 testbench 代码。

    2. **编译 Testbench**

    * 使用工具【compile_testbench】编译 testbench。
    * 认真检查编译器输出，确保编译成功。
    * 如果编译遇到问题，你需要重新编写 testbench 代码。

    3. **运行 Testbench**

    * 编译成功后，使用工具【run_testbench】获取和观察验证结果。
    * 只能查看运行输出文本信息，不允许查看波形图或进行交互调试。
    * 如果 testbench 运行失败，你需要重新编写 testbench 代码、重新编译。

    3. **撰写验证总结**

    * 基于验证结果，使用工具【write_verification_summary】撰写验证总结。
    * 完成后，将验证总结提交给 team leader 审核。【transfer_to_team_leader】

    4. **处理更新**

    * 每次设计工程师通知你存在设计更新时，你都需要重新验证并更新验证报告。
    * 重新进行验证并更新报告。

    注意：在任何时间，可以使用【check_team_log】查看团队日志，了解项目的最新情况和进展。


    """
)