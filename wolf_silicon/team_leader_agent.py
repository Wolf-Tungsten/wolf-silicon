from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent

def review_user_requirements() -> str:
    """If you need to refresh your memory on the specific details of the user requirements, you can review them here."""
    return WolfSiliconEnv().common_read_file("user_requirements.md")

def write_spec(spec:str, overwrite=False) -> None:
    """Document your design specifications in spec.md, so other team members can review it.
       Note: You can choose to overwrite the previous content or append to the end of the file."""
    WolfSiliconEnv.update_log("team_leader", "Update design specifications.")
    WolfSiliconEnv().common_write_file("spec.md", spec, overwrite)

def review_spec() -> str:
    """Review your design specifications in spec.md."""
    return WolfSiliconEnv().common_read_file("spec.md")

def review_design_complaints() -> str:
    """Review the complaints from the design team. They require your updates to the design specifications."""
    return WolfSiliconEnv().common_read_file("design_complaints.md")

def review_verification_summary() -> str:
    """Review the validation summary report to determine whether to continue iterating or report completion to the user."""
    return WolfSiliconEnv().common_read_file("verification_summary.md")

def check_team_log() -> str:
    """Check the team log to review the latest updates from the team."""
    return WolfSiliconEnv().read_log()

team_leader_agent = AssistantAgent(
    name="team_leader",
    tools=[review_user_requirements, write_spec, review_spec, review_design_complaints, review_verification_summary, check_team_log],
    handsoff=["cmodel_team", "user"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的负责人，职责是spec文档撰写和项目进度管理，以及最终的签核""",
    system_message="""你是硬件IP设计团队“Wolf-Silicon”的负责人，你的职责如下，请根据团队日志判断当前项目进度，选择合适的工作进行开展：
    - 在项目开始，你首先查看用户需求，如果你认为用户的需求不够明确，你可以跟用户讨论，所有用户提出的需求都会自动记录在 user_requirements.md 中，你可以随时查看；
    - 用户需求确认后你需要编写 spec.md，描述设计的详细要求，你的 spec.md 会被团队其他成员审阅，你可以随时查看；
    - spec.md 完成后，请你通知 cmodel_engineer 进行建模；
    - 如果团队日志显示 design_engineer 对 spec.md 提出了 design_complaints.md，你需要及时修改，修改后提醒 cmodel_engineer 跟进；
    - 如果团队日志显示 verification_engineer 提交了 verification_summary.md，你需要及时审阅：
    -- 如果 verification_summary.md 报告了问题，你需要及时处理，通过编写 spec.md 将你的进一步意见传达给团队的其他人；
    -- 如果 verification_summary.md 显示通过，你可以用关键词"TEAM_LEADER_APPROVED"通知用户完成，这是你的**最终目标**。
    你可以使用 "check_team_log", "review_user_requirements", "write_spec", "review_spec", "review_design_complaints", "review_verification_summary", 这些工具来帮助你完成工作。
    """
)