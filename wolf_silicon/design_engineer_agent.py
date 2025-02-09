from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, review_design_complaints, review_verification_summary
from cmodel_engineer_agent import run_cmodel
from codebase_tool import codebase_tool_help, list_codebase, view_file, create_file, append_to_file, overwrite_file, delete_file, search_codebase
from team_log_tool import write_my_log, view_team_log
import os

def lint_design() -> str:
    """Lint all the .v design code in with verilator. Will return the output of the linter."""
    # 获取 codebase 中所有 .v 文件
    v_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.v'):
            v_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    return WolfSiliconEnv.execute_command(f"verilator -Wall --lint-only {' '.join(v_files)} -I{WolfSiliconEnv().get_workpath()}", 300)

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
    tools=[review_spec, run_cmodel, lint_design, write_design_complaints, review_design_complaints, review_verification_summary, write_my_log, view_team_log, codebase_tool_help, list_codebase, view_file, create_file, append_to_file, overwrite_file, delete_file, search_codebase],
    reflect_on_tool_use=True,
    handoffs=["verification_engineer", "team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 design engineer，职责是根据 spec.md 和 cmodel 开展 verilog 设计""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的 design engineer，精通 Verilog。你的职责是编写设计代码（dut.v)，并使用适当的工具来有效开展工作。

    你的任务：

    1.编写 Verilog 设计代码

    * 可以使用工具【review_spec】查看 spec.md，了解设计要求。
    * 代码库中包含参考 Cmodel 的源码，如果需要运行 Cmodel，可以使用【run_cmodel】工具。
    * 可以使用代码库工具查看代码库中的文件，如果不知道如何操作，可以使用【codebase_tool_help】查看帮助。
    * 基于以上信息，使用代码库工具编写 Verilog 设计代码。
    * 设计代码必须可综合。

    2.执行 Lint 检查

    * 编写完成后，使用工具【lint_design】对设计代码进行 lint 检查。
    * 确保代码符合规范，如果存在问题，使用返回及时修改。
    
    3.确认设计并通知验证工程师

    * 确认通知 verification_engineer 进行验证。【transfer_to_verification_engineer】
    
    4.（如果有必要）投诉 Spec 和 CModel 的问题

    * 如果 spec 或 cmodel 中有困扰你的问题，使用工具【write_design_complaints】撰写 design_complaints.md 并提交给 team leader 处理。【transfer_to_team_leader】
    * 不要经常投诉，只有在确实存在问题时才提交，否则你的 team_leader 会认为你是在推卸责任。

    5.处理更新

    * 每次 cmodel_engineer 通知你后，你都需要及时调整设计代码
    * 并通知 verification_engineer 进行验证。【transfer_to_verification_engineer】
    * 如果 team leader 指出设计存在问题，使用工具【review_verification_summary】查看验证总结，以便了解验证结果。

    6.团队协作

    * 及时通过 【write_my_log】记录你的操作，以便团队其他成员了解你的工作进度。
    * 如果你遇到困难，可以求助于 team_leader 或其他团队成员。
    * 求助之前，请确保你已经记录了你的操作，并明确你的问题，使用【write_my_log】工具。
    * 如果你不知道该做什么，请【view_team_log】看看团队日志，里面可能有 team_leader 的指示。

    """
)