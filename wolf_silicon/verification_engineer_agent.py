from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec
from cmodel_engineer_agent import run_cmodel
from codebase_tool import codebase_tools
from workspace_state import get_spec_state, get_cmodel_state, get_design_state, get_verification_report_state
import os

def verification_engineer_inbox() -> str:
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
    
    if not design_exists or (cmodel_mtime > design_mtime):
        return """
        # Project State

        The design is not exist or outdated.
        
        # Something goes wrong

        YOU HAVE TO【transfer_to_project_manager】NOW!
        """
    
    if not verification_report_exists or (design_mtime > verification_report_mtime):
        return """
        # Project State

        The verification report is not exist or outdated.
        
        # Your Tasks Today

        **Task 1** Use 【review_spec】 to review the design specifications.
        **Task 2** Use 【list_codebase】(or【view_file】go further) to get any reference code you need, specifically the cmodel and design code.
        **Task 3 (Optional) ** Use 【run_cmodel】 to run the cmodel.
        **Task 4** Contribute your testbench code in the codebase.
            - You can only create or modify .sv/.svh/.v/.vh files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
        **Task 5** Review your testbench code.
            - Ensure your testbench use assertions to verify the correctness of the design.
            - You rely on text log of the testbench to verify the correctness of the design, give yourself a clear signal of pass or fail.
            - If the code has any issue, you need to return to Task 4.
        **Task 6** Use 【compile_testbench】 to compile the testbench.
            - Ensure the compiler output is successful.
            - If the compiler encounters problems, you need to return to Task 4.
        **Task 7** Use 【run_testbench】 to run the testbench.
            - Ensure the code can run correctly. 
            - If the code fails to run, you need to return to Task 4. 
            - No matter the testbench pass or fail, you need to write a verification report.
        **Task 8** Use 【write_verification_report】 to write a verification report.
        **Task 9** Use 【transfer_to_project_manager】 to notify the project manager to review your verification report.
        
        """
    
    return """
    # Project State

    The project is in a weird state.

    # Your Tasks Today

    Use 【transfer_to_project_manager】 refer to project manager to check the project state.
    """

def compile_testbench() -> str:
    """Call Verilator to compile all design and verification files in the codebase into an executable file Vtb, return compiler output (up to 4KB)"""
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

def write_verification_report(summary:str, overwrite:bool=False) -> str:
    """Write your verification report"""
    WolfSiliconEnv().common_write_file("verification_report.md", summary, overwrite)
    if overwrite:
        WolfSiliconEnv().update_log("verification_engineer", "Overwrite verification_report.md")
    else:
        WolfSiliconEnv().update_log("verification_engineer", "Append into verification_report.md")
    return "Verification Summary updated."

verification_engineer_agent = AssistantAgent(
    "verification_engineer",
    tools=[verification_engineer_inbox, review_spec, run_cmodel, compile_testbench, run_testbench, write_verification_report, *codebase_tools],
    reflect_on_tool_use=True,
    handoffs=["project_manager"],
    model_client=mc,
    description="""The verification engineer of Wolf-Silicon, responsible for verifying the design and writing verification reports.""",
    system_message="""
    As the verification engineer of the hardware IP design team "Wolf-Silicon",

    You are responsible for verifying the design and writing verification reports.

    You need to ensure that the design is correct and meets the specifications.

    ALL CODE YOU WRITE MUST IN VERILOG/SYSTEMVERILOG(.v/.vh/.sv/.svh).
    YOU CAN ONLY GOT TEXT LOG TO VERIFY THE CORRECTNESS OF THE DESIGN.
    ALWAYS WRITE A VERIFICATION REPORT NO MATTER THE TESTBENCH PASS OR FAIL.

    Welcome to today's work:

    Please check your task list using 【verification_engineer_inbox】 and ensure all tasks are completed before the end of the day!

    """
)