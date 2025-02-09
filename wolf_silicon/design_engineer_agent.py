from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec, review_verification_report
from cmodel_engineer_agent import run_cmodel
from codebase_tool import codebase_tools
from workspace_state import get_spec_state, get_cmodel_state, get_design_state, get_verification_report_state
import os

def checkout_task() -> str:
    spec_exists, spec_mtime = get_spec_state()
    cmodel_exists, cmodel_mtime = get_cmodel_state()
    design_exists, design_mtime = get_design_state()
    verification_report_exists, verification_report_mtime = get_verification_report_state()

    if not spec_exists:
        return """
        
        # Project State

        There has no spec.md in the workspace.

        # Something goes wrong

        YOU HAVE TO【transfer_to_project_manager】NOW!

        """

    if not cmodel_exists or (spec_mtime > cmodel_mtime):
        return """
        
        # Project State

        The cmodel is not exist or outdated.

        # Something goes wrong

        YOU HAVE TO【transfer_to_project_manager】NOW!

        """
    
    # spec and cmode exist / uptodate

    if not design_exists or (spec_mtime > design_mtime):
        return """
        # Project State

        The design is not exist or outdated.

        # Your Tasks Today

        **Task 1** Use 【review_spec】 to review the design specifications.
        **Task 2** Use 【list_codebase】(or【view_file】go further) to get any reference code you need, specifically the cmodel code.
        **Task 3 (Optional) ** Use 【run_cmodel】 to run the cmodel.
        **Task 4** Contribute your design code in the codebase.
            - You can only create or modify .v/.vh files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
            - Ensure the code is synthesizable.
        **Task 5** Use 【lint_design】 to lint your design code.
            - Ensure the code is lint clean.
            - If the code has any lint error, you need to return to Task 4.
        **Task 6** Use 【transfer_to_verification_engineer】 to notify the verification engineer to start verification.
        """
    
    # spec, cmodel and design exist / uptodate
    
    if verification_report_exists and verification_report_mtime > design_mtime:
        return """
        # Project State

        Your design have some issues, update needed.

        # Your Tasks Today
        **Task 1** Use 【review_verification_report】 to review the verification report (If exist) figure out the problem.
        **Task 2** Use 【review_spec】 to review the design specifications.
        **Task 3** Use 【list_codebase】(or【view_file】go further) to get any reference code you need, specifically the cmodel code.
        **Task 4 (Optional) ** Use 【run_cmodel】 to run the cmodel.
        **Task 5** Update your design code in the codebase.
            - You can only create or modify .v/.vh files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
            - Ensure the code is synthesizable.
            - Ensure the code obey the verilog-2001 standard.
        **Task 6** Use 【lint_design】 to lint your design code.
            - Ensure the code is lint clean.
            - If the code has any lint error, you need to return to Task 5.
        **Task 7** Use 【transfer_to_verification_engineer】 to notify the verification engineer to re-verify.
        """
    
    return """
    # Project State

    Your design is ready for verification.

    # Your Tasks Today
    
    Use 【transfer_to_verification_engineer】 to notify the verification engineer to start verification.
    """


def lint_design() -> str:
    """Lint all the .v/.vh design code in with verilator. Will return the output of the linter."""
    # 获取 codebase 中所有 .v 文件
    v_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.v'):
            v_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    return WolfSiliconEnv.execute_command(f"verilator -Wall --lint-only {' '.join(v_files)} -I{WolfSiliconEnv().get_workpath()}", 300)


design_engineer_agent = AssistantAgent(
    "design_engineer",
    tools=[review_spec, review_verification_report, run_cmodel, lint_design, *codebase_tools],
    reflect_on_tool_use=True,
    handoffs=["verification_engineer", "project_manager"],
    model_client=mc,
    description="""The design engineer of the hardware IP design team "Wolf-Silicon", responsible for writing design code.""",
    system_message="""

    As the design engineer of Wolf-Silicon, you are responsible for writing design code, Follow the steps below to complete your daily tasks.

    Your Daily Tasks:
    
    1. Use 【review_spec】 to review the design specifications.
    2. Use 【review_verification_report】 to check if there is any verification issues.
    3. Use 【list_codebase】(or【view_file】go further) to get any reference code you need, specifically the cmodel code.
    4. Use 【run_cmodel】 to run the cmodel.
    5. **Contribute your design code in the codebase.**
        - You can only create or modify .v/.vh files in the codebase.
        - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
        - Ensure the code is synthesizable.
        - Ensure the code obey the verilog-2001 standard.
    6. Use 【lint_design】 to lint your design code.
        - Ensure the code is lint clean.
        - If the code has any lint error, you need to return to Task 5.
    7. Use 【transfer_to_verification_engineer】 to notify the verification engineer to re-verify.
    """
)