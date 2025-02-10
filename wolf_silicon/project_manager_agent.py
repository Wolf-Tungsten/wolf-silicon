from model_client import mc
from wolf_silicon.env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from workspace_state import get_user_requirements_state, get_spec_state, get_verification_report_state
import os

def review_cmodel_code() -> str:
    """Review the cmodel code in the cmodel.cpp."""
    return WolfSiliconEnv().common_read_file("cmodel.cpp")

def review_design_code() -> str:
    """Review the design code in the dut.v."""
    return WolfSiliconEnv().common_read_file("dut.v")

def review_testbench_code() -> str:
    """View the verification testbench tb.sv file"""
    return WolfSiliconEnv().common_read_file("tb.sv")

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
    """Review the verification report."""
    if os.path.exists(os.path.join(WolfSiliconEnv().get_workpath(),"verification_report.md")):
        return WolfSiliconEnv().common_read_file("verification_report.md")
    return "No verification report found this time, please continue your design working."



project_manager_agent = AssistantAgent(
    "project_manager",
    tools=[review_user_requirements, write_spec, review_verification_report, review_spec, review_design_code, review_cmodel_code, review_testbench_code],
    handoffs=["cmodel_engineer", "user"],
    reflect_on_tool_use=True,
    model_client=mc,
    description="""The project manager of the hardware IP design team "Wolf-Silicon", checking verification report, writing spec documents.""",
    system_message="""
    As the project manager of Wolf-Silicon, you are responsible for checking verification report, writing spec documents.
    Your Daily Routine:
    1. Use 【review_verification_report】 to checkout verification report.
    2. If verification_report exists and the project is completed:
        2.a Use 【transfer_to_user】 to ask user for new requirements.
        2.b Move to 3.a
    3. Otherwise:
        3.a Use 【review_user_requirements】 to review the user requirements.
        3.b Use 【write_spec】 to update the design specifications.
        3.c Use 【transfer_to_cmodel_engineer】 to notify the cmodel engineer to update modeling.
    """
)