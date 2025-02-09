from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from team_log_tool import write_my_log, view_team_log

def review_user_requirements() -> str:
    """If you need to refresh your memory on the specific details of the user requirements, you can review them here."""
    return WolfSiliconEnv().common_read_file("user_requirements.md")

def write_spec(spec:str, overwrite:bool=False) -> str:
    """Document your design specifications into spec.md, so other team members can review it.
       Note: You can choose to overwrite the previous content or append to the end of the file."""
    WolfSiliconEnv().update_log("team_leader", "Update design specifications.")
    WolfSiliconEnv().common_write_file("spec.md", spec, overwrite)
    return "Spec updated."

def review_spec() -> str:
    """Review your design specifications in spec.md."""
    return WolfSiliconEnv().common_read_file("spec.md")

def review_design_complaints() -> str:
    """Review the complaints from the design team. They require your updates to the design specifications."""
    return WolfSiliconEnv().common_read_file("design_complaints.md")

def review_verification_summary() -> str:
    """Review the validation summary report to determine whether to continue iterating or report completion to the user."""
    return WolfSiliconEnv().common_read_file("verification_summary.md")



team_leader_agent = AssistantAgent(
    "team_leader",
    tools=[review_user_requirements, write_spec, review_spec, review_design_complaints, review_verification_summary, write_my_log, view_team_log],
    handoffs=["cmodel_engineer", "user", "design_engineer", "verification_engineer"],
    model_client=mc,
    description="""硬件IP设计团队“Wolf-Silicon”的负责人，职责是文档撰写和项目进度管理""",
    system_message="""
    角色说明：

    你是硬件IP设计团队 "Wolf-Silicon" 的负责人。你的职责是包括整理需求文档和管理项目进度，使用合适的工具来完成各个任务。

    你的任务：

    1. 阅读分析用户需求

    * 可工具 【review_user_requirements】 查看和核对需求，系统会自动保存你和用户的交互记录
    * 如果需求不明确，使用【transfer_to_user】向用户提问
    
    2. 编写设计文档（spec.md)

    * 使用工具 【write_spec】 编写 spec.md，详细描述设计要求，并供团队审阅。
    * 你可使用 【review_spec】 工具查看已编写的设计文档

    3. 通知 CModel 工程师（cmodel_engineer) 进行建模

    * 在你每次更新文档后，你需要通知 cmodel_engineer 进行建模。【transfer_to_cmodel_engineer】

    4. 处理设计工程师（design_engineer)的投诉

    * 如果设计工程师认为设计文档有问题，他们会编写 design_complaints.md，并 Handoff 给你。
    * 你可以使用 【review_design_complaints】 工具查看设计团队的投诉
    * 修改后请通知 cmodel_engineer 跟进

    5. 审阅验证总结，管理团队进度

    * 验证工程师(verification_engineer)会提交验证总结 verification_summary.md 并 Handoff 给你
    * 你可以使用 【review_verification_summary】 工具查看验证总结
    * 如果找不到验证报告，说明团队成员遇到了困难，你可以【view_team_log】 找出问题，并通过【write_my_log】提供你认为的解决方案，然后转移给相应的工程师。 
    * 如果验证报告通过，你可以使用关键词 "TEAM_LEADER_APPROVED" 通知用户完成。【transfer_to_user】
    * 如果找到验证报告，但是验证报告提示存在问题
        * 如果你认为cmodel环节存在问题，用【write_my_log】提供你对 cmodel_engineer 的意见，然后【transfer_to_cmodel_engineer】
        * 如果你认为design环节存在问题，用【write_my_log】提供你对 design_engineer 的意见，然后【transfer_to_design_engineer】
        * 如果你认为verification环节存在问题，用【write_my_log】提供你对 verification_engineer 的意见，然后【transfer_to_verification_engineer】 

    6. 团队协作

    * 其他团队成员可能会向你寻求帮助，查看团队日志【view_team_log】，了解他们遇到的问题
    * 将你认为的解决方案记录在团队日志中，使用【write_my_log】工具，以便团队成员查看
    * 然后将问题转移给相应的工程师，以便他们继续工作
    
    """
)