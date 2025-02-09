from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from workspace_state import get_user_requirements_state, get_spec_state, get_verification_report_state

def project_manager_inbox() -> str:
    """ Checkout your task list """
    spec_exist, spec_mtime = get_spec_state()
    verification_report_exist, verification_report_mtime = get_verification_report_state()
    user_requirements_exist, user_requirements_mtime = get_user_requirements_state()
    assert user_requirements_exist, "user_requirements.md should exist."

    if not spec_exist:
        return """
        # Project State

        There has no spec.md in the workspace.

        # Your Tasks Today

        - Use 【review_user_requirements】 to review the user requirements.
        - Use 【write_spec】 to write the design specifications.
        - 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to start modeling.
        """
    
    
    if spec_mtime < user_requirements_mtime:
        return """
        # Project State

        The spec.md is outdated.

        # Your Tasks Today

        - Use 【review_user_requirements】 to review the user requirements.
        - Use 【write_spec】 to update the design specifications.
        - 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to update modeling.
        """

    if not verification_report_exist:
        return """
        # Project State

        There has no verification report in the workspace.
        This project is still in progress.

        # Your Tasks Today

        - Use 【review_user_requirements】 to review the user requirements.
        - Use 【review_spec】 to review the design specifications.
        - Use 【write_spec】 to update the design specifications.
        - 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to update modeling.
        """
    
    if verification_report_mtime < spec_mtime:
        return """
        # Project State

        The verification report is outdated.

        # Your Tasks Today

        - Use 【review_user_requirements】 to review the user requirements.
        - Use 【review_spec】 to review the design specifications.
        - Use 【write_spec】 to update the design specifications.
        - 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to update modeling.
        """
    
    # 执行到此处，spec 存在且最新，verification_report 存在且最新
    return """
    # Project State

    There is a verification report in the workspace.

    # Your Tasks Today

    1. Use 【review_verification_report】 to review the verification report.
    2. Determine whether project is completed or not.
    3. If the project is completed:
        3.a Use 【transfer_to_user】 to ask user for review. 
    4. If the project is not completed:
        4.a Use 【review_user_requirements】 to review the user requirements.
        4.b Use 【review_spec】 to review the design specifications.
        4.c Use 【write_spec】 to update the design specifications.
        4.d Use 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to update modeling.
    
    """
        
def review_user_requirements() -> str:
    """If you need to refresh your memory on the specific details of the user requirements, you can review them here."""
    return WolfSiliconEnv().common_read_file("user_requirements.md")

def write_spec(spec:str, overwrite:bool=False) -> str:
    """Document your design specifications into spec.md, so other team members can review it.
       Note: You can choose to overwrite the previous content or append to the end of the file."""
    WolfSiliconEnv().update_log("project_manager", "Update design specifications.")
    WolfSiliconEnv().common_write_file("spec.md", spec, overwrite)
    return "Spec updated."

def review_spec() -> str:
    """Review your design specifications in spec.md."""
    return WolfSiliconEnv().common_read_file("spec.md")

def review_verification_report() -> str:
    """Review the validation summary report to determine whether to continue iterating or report completion to the user."""
    return WolfSiliconEnv().common_read_file("verification_report.md")



project_manager_agent = AssistantAgent(
    "project_manager",
    tools=[project_manager_inbox, review_user_requirements, write_spec, review_spec, review_verification_report],
    handoffs=["cmodel_engineer", "user"],
    model_client=mc,
    description="""The project manager of the hardware IP design team "Wolf-Silicon", responsible for organizing requirements and writing design documents.""",
    system_message="""
    As the project manager of the hardware IP design team "Wolf-Silicon," your responsibilities include organizing requirements and managing project progress, utilizing the appropriate tools to complete various tasks.

    Welcome to today's work:

    Please check your task list using 【project_manager_inbox】 and ensure all tasks are completed before the end of the day!
    """
)