from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, check_team_log, review_design_complaints
from cmodel_engineer_agent import review_cmodel, run_cmodel
from design_engineer_agent import review_design
import os

def write_testbench(code:str) -> str:
    """将你提供的 testbench 代码写入 tb.sv 中，先前的内容将被覆盖
    注意：你的所有代码都应该在这个文件中，不要使用其他文件"""
    WolfSiliconEnv().common_write_file("tb.sv", code)
    WolfSiliconEnv().update_log("verification_engineer", "Update testbench.")
    return "Code updated."

def review_testbench() -> str:
    """Review the testbench code in tb.sv."""
    return WolfSiliconEnv().common_read_file("tb.sv")

def compile_testbench() -> str:
    """调用 Verilator，将你的 tb.sv 和 design.v 编译为可执行文件，返回编译器的输出(最多4KB)"""
    result = os.popen(f"verilator --binary --build --timing {WolfSiliconEnv().get_workpath()}/tb.sv {WolfSiliconEnv().get_workpath()}/design.v --sv -CFLAGS \"-fcoroutines\" --Mdir {WolfSiliconEnv().get_workpath()}/obj_dir").read()
    return result[-4*1024:]


def run_testbench(timeout_sec:int=300) -> str:
    """Run the testbench binary. Will return the last 4KB output of the testbench. """
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/Vtb", timeout_sec)
    return result[-4*1024:]

def write_verification_summary(summary:str, overwrite=False) -> str:
    """将你的验证总结写入 verification_summary.md 中，你可以选择覆盖之前的内容或追加到文件末尾"""
    WolfSiliconEnv().common_write_file("verification_summary.md", summary, overwrite)
    if overwrite:
        WolfSiliconEnv().update_log("verification_engineer", "Overwrite verification_summary.md")
    else:
        WolfSiliconEnv().update_log("verification_engineer", "Append into verification_summary.md")
    return "Verification Summary updated."

verification_engineer_agent = AssistantAgent(
    name="verification_engineer",
    tools=[check_team_log, review_spec, review_cmodel, run_cmodel, review_design, write_testbench, review_testbench, compile_testbench, run_testbench, write_verification_summary],
    handsoff=["team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 verification engineer，职责是根据 spec、cmodel、design 开展验证，编写验证报告""",
    system_message="""你是硬件IP设计团队“Wolf-Silicon”的 verification engineer，你精通SystemVerilog，你的职责如下，请根据团队日志（自动生成）判断当前项目进度，选择合适的工作进行开展：
    - 根据 spec、cmodel、design 编写 testbench 代码：
    -- 要求等层模块名称为 tb，否则编译器无法识别
    -- 你只能查看运行输出的文本信息，不要查看波形图，也不能交互调试
    -- 所有的验证代码都保存一个 tb.sv 文件中
    - testbench 编写完成后，你编译、运行，获取验证结果
    - 根据验证结果撰写 verification_summary
    - 你将验证总结提交给 team leader 审核，这是你的**最终目标**
    - 如果 spec、cmodel、design 发生了更新，你需要及时调整 testbench 代码，并重新开展验证、撰写报告
    你可以使用 check_team_log, review_spec, review_cmodel, run_cmodel, review_design, write_testbench, review_testbench, compile_testbench, run_testbench, write_verification_summary 这些工具来帮助你完成工作。
    """
)