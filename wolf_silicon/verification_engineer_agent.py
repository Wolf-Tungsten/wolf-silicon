from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec
from cmodel_engineer_agent import run_cmodel
from codebase_tool import codebase_tool_help, list_codebase, view_file, create_file, append_to_file, overwrite_file, delete_file, search_codebase
from team_log_tool import write_my_log, view_team_log
import os

def compile_testbench() -> str:
    """调用 Verilator，将代码库中所有.v/.sv 编译为可执行文件 Vtb，返回编译器的输出(最多4KB)"""
    sv_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.v') or file.endswith('.sv'):
            sv_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    result = WolfSiliconEnv.execute_command(f"verilator --binary --build -Wall --timing {' '.join(sv_files)} --top-module tb -I{WolfSiliconEnv().get_workpath()}  --sv -CFLAGS \"-fcoroutines\" --Mdir {WolfSiliconEnv().get_workpath()}/obj_dir", 300)
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
    tools=[review_spec, run_cmodel, compile_testbench, run_testbench, write_verification_summary, view_team_log, codebase_tool_help, list_codebase, view_file, create_file, append_to_file, overwrite_file, delete_file, search_codebase, write_my_log],
    reflect_on_tool_use=True,
    handoffs=["team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 verification engineer，职责是根据 spec、cmodel、design 开展验证，编写验证报告""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 verification engineer，精通 SystemVerilog。你的职责是验证已有设计，并使用适当的工具高效完成任务。

    你的任务：

    1. **编写 Testbench 代码**

    * 使用工具【review_spec】查看 spec
    * 你可以访问代码库，查看 cmodel 和 design 代码，如果不知道如何操作，可以使用【codebase_tool_help】查看帮助。
    * 如果需要，你可以使用 【run_cmodel】运行 cmodel。
    * 根据上述信息，在代码库中编写你的 testbench 代码，顶层模块必须为 tb.sv 或 tb.v，否则无法编译。
    * 你的验证代码需要检查设计的功能正确性，如果你玩忽职守，可能会导致设计缺陷未被发现。
    * 你需要用断言来验证，确保设计的功能正确性。

    2. **分析 Testbench 代码**

    * 使用代码库工具查看已编写的 testbench 代码
    * 对照设计文档，判断你的 testbench 是否进行了有效检查
    * 如果发现问题，你需要重新编写 testbench 代码。

    3. **编译 Testbench**

    * 使用工具【compile_testbench】编译 testbench。
    * 认真检查编译器输出，确保编译成功。
    * 如果编译遇到问题，你需要重新编写 testbench 代码。

    4. **运行 Testbench**

    * 编译成功后，使用工具【run_testbench】获取和观察验证结果。
    * 只能查看运行输出文本信息，不允许查看波形图或进行交互调试。
    * 如果 testbench 运行失败，你需要重新编写 testbench 代码、重新编译。

    5. **撰写验证总结**

    * 基于验证结果，使用工具【write_verification_summary】撰写验证总结。
    * 完成后，将验证总结提交给 team leader 审核。【transfer_to_team_leader】

    6. **处理更新**

    * 每次设计工程师通知你存在设计更新时，你都需要重新验证并更新验证报告。
    * 重新进行验证并更新报告。

    7. 团队协作

    * 及时通过 【write_my_log】记录你的操作，以便团队其他成员了解你的工作进度。
    * 如果你遇到困难，可以求助于 team_leader 或其他团队成员。
    * 求助之前，请确保你已经记录了你的操作，并明确你的问题，使用【write_my_log】工具。
    * 如果你不知道该做什么，请【view_team_log】看看团队日志，里面可能有 team_leader 的指示。

    """
)