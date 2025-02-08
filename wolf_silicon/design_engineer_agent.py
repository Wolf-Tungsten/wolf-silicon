from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_leader_agent import review_spec, check_team_log, review_design_complaints, review_verification_summary
from cmodel_engineer_agent import review_cmodel, run_cmodel
import os

def write_design(code:str) -> str:
    """将你提供的 verilog 代码写入 design.v 中，先前的内容将被覆盖
    注意：你的所有代码都应该在这个文件中，不要使用其他文件"""
    WolfSiliconEnv().common_write_file("design.v", code)
    WolfSiliconEnv().update_log("design_engineer", "Update design.")
    return "Code updated."

def lint_design() -> str:
    """Lint the design code in design.v with verilator. Will return the output of the linter."""
    return os.popen(f"verilator --lint-only {WolfSiliconEnv().get_workpath()}/design.v").read()

def review_design() -> str:
    """Review the design code in design.v."""
    return WolfSiliconEnv().common_read_file("design.v")

def write_design_complaints(report:str, overwrite=False) -> str:
    """将你认为 spec 或 cmodel 中存在的问题写入 design_complaints.md 中
       你可以选择覆盖之前的内容或追加到文件末尾"""
    WolfSiliconEnv().common_write_file("design_complaints.md", report, overwrite=False)
    if overwrite:
        WolfSiliconEnv().update_log("design_engineer", "Overwrite design_complaints.md")
    else:
        WolfSiliconEnv().update_log("design_engineer", "Append into design_complaints.md")
    return "Report updated."

design_engineer_agent = AssistantAgent(
    name="design_engineer",
    tools=[check_team_log, review_spec, review_cmodel, run_cmodel, write_design, lint_design, review_design, write_design_complaints, review_design_complaints, review_verification_summary],
    handsoff=["verification_engineer", "team_leader"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的 design engineer，职责是根据 spec.md 和 cmodel 开展 verilog 设计""",
    system_message="""你是硬件IP设计团队“Wolf-Silicon”的 design engineer，你精通Verilog，你的职责如下，请根据团队日志（自动生成）判断当前项目进度，选择合适的工作进行开展：
    - 根据 spec 和 cmodel（源码、可执行文件）编写 verilog 设计代码：
    -- 要求设计代码可综合，所有的设计代码都保存在 design.v 文件中
    - 编写完成后，你需要对设计代码进行 lint 检查，确保设计代码符合规范，如果存在问题应及时修改
    - 确认设计无误后，你调动 verification_engineer 进行验证，这是你的**最终目标**
    - 如果你认为 spec 或者 cmodel 存在困扰你的问题，你可以撰写 design_complaints.md 并提交给 team leader 处理
    - 如果 spec、cmodel 发生了更新，你需要及时调整设计代码，并重新 lint 检查，然后通知 verification_engineer
    - 如果 team_leader 认为设计存在问题，你也可以查看 verification_summary.md，以便了解验证结果
    你可以使用 "check_team_log", "review_spec", "review_cmodel", "run_cmodel", "write_design", "lint_design", "review_design", "write_design_complaints", "review_design_complaints", "review_verification_summary" 这些工具来帮助你完成工作。
    """
)