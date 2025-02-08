from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, check_team_log, review_design_complaints, review_verification_summary
from cmodel_engineer_agent import review_cmodel, run_cmodel
import os

def write_design(code:str) -> str:
    """将你提供的 verilog 代码写入 dut.v 中，先前的内容将被覆盖
    注意：你的所有代码都应该在这个文件中，不要使用其他文件"""
    WolfSiliconEnv().common_write_file("dut.v", code+"\n")
    WolfSiliconEnv().update_log("design_engineer", "Update design.")
    return "Code updated."

def lint_design() -> str:
    """Lint the design code in dut.v with verilator. Will return the output of the linter."""
    return WolfSiliconEnv.execute_command(f"verilator -Wall --lint-only {WolfSiliconEnv().get_workpath()}/dut.v", 300)

def review_design() -> str:
    """Review the design code in dut.v."""
    return WolfSiliconEnv().common_read_file("dut.v")

def write_design_complaints(report:str, overwrite:bool=False) -> str:
    """将你认为 spec 或 cmodel 中存在的问题写入 design_complaints.md 中
       你可以选择覆盖之前的内容或追加到文件末尾"""
    WolfSiliconEnv().common_write_file("design_complaints.md", report, overwrite)
    if overwrite:
        WolfSiliconEnv().update_log("design_engineer", "Overwrite design_complaints.md")
    else:
        WolfSiliconEnv().update_log("design_engineer", "Append into design_complaints.md")
    return "Report updated."

design_engineer_agent = AssistantAgent(
    "design_engineer",
    tools=[check_team_log, review_spec, review_cmodel, run_cmodel, write_design, lint_design, review_design, write_design_complaints, review_design_complaints, review_verification_summary],
    reflect_on_tool_use=True,
    handoffs=["verification_engineer", "team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 design engineer，职责是根据 spec.md 和 cmodel 开展 verilog 设计""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 design engineer，精通 Verilog。你的职责是编写设计代码（dut.v)，并使用适当的工具来有效开展工作。

    你的任务：

    1.编写 Verilog 设计代码

    * 可以使用工具【review_spec】、【review_cmodel】、【run_cmodel】查看 spec 和 cmodel（包括源码和可执行文件）。
    * 基于以上信息，使用工具【write_design】编写 Verilog 设计代码，并确保所有代码保存在 dut.v 文件中。
    * 无论模块功能是什么，你的模块名称都应该是 `dut`。
    * 如果需要，使用【review_design】查看已编写的设计代码。
    * 设计代码必须可综合。

    2.执行 Lint 检查

    * 编写完成后，使用工具【lint_design】对设计代码进行 lint 检查。
    * 确保代码符合规范，如果存在问题，使用【write_design】及时修改。
    
    3.确认设计并通知验证工程师

    * 确认通知 verification_engineer 进行验证。【transfer_to_verification_engineer】
    
    4.（如果有必要）投诉 Spec 和 CModel 的问题

    * 如果 spec 或 cmodel 中有困扰你的问题，使用工具【write_design_complaints】撰写 design_complaints.md 并提交给 team leader 处理。【transfer_to_team_leader】
    * 不要经常投诉，只有在确实存在问题时才提交，否则你的 team_leader 会认为你是在推卸责任。

    5.处理更新

    * 每次 cmodel_engineer 通知你后，你都需要及时调整设计代码
    * 并通知 verification_engineer 进行验证。【transfer_to_verification_engineer】
    * 如果 team leader 指出设计存在问题，使用工具【review_verification_summary】查看验证总结，以便了解验证结果。

    注意：在任何时间，可以使用【check_team_log】查看团队日志，了解项目的最新动态和进展。
    """
)