from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec, review_cmodel_code, review_design_code 
from cmodel_engineer_agent import run_cmodel
from design_engineer_agent import  write_design_code
import os

def write_testbench_code(code:str) -> str:
    """Change testbench code in the tb.sv"""
    WolfSiliconEnv().common_write_file("tb.sv", code, True)
    return "Write testbench code into tb.sv successfully."

def review_testbench_code() -> str:
    """View the tb.sv file"""
    return WolfSiliconEnv().common_read_file("tb.sv")

def compile_testbench() -> str:
    """Call Verilator to compile all design and verification files in the codebase into an executable file Vtb, return compiler output (up to 4KB)"""
    sv_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.v') or file.endswith('.sv'):
            sv_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    result = WolfSiliconEnv.execute_command(f"verilator -Wno-TIMESCALEMOD -Wno-DECLFILENAME --binary --build --timing {' '.join(sv_files)} --top-module tb -I{WolfSiliconEnv().get_workpath()}  --sv -CFLAGS \"-fcoroutines\" --Mdir {WolfSiliconEnv().get_workpath()}/obj_dir", 300)
    return result[-4*1024:]


def run_testbench(timeout_sec:int=10) -> str:
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
    tools=[review_spec, review_cmodel_code, run_cmodel, write_design_code, review_design_code, write_testbench_code, compile_testbench, run_testbench, write_verification_report],
    reflect_on_tool_use=True,
    handoffs=["project_manager"],
    model_client=mc,
    description="""The verification engineer of Wolf-Silicon, responsible for verifying the design and writing verification reports.""",
    system_message="""
    
    As the verification engineer of Wolf-Silicon, you are responsible for verifying the design and writing verification reports.

    Follow the steps below to complete your daily tasks.

    Your Daily Routine:
    1. Use 【review_spec】 to review the design specifications.
    2. Use 【review_cmodel_code】 and 【run_cmodel】 to review the cmodel.
    3. Use 【review_design_code】 to review the current dut.v.
    4. Contribute your testbench code in the tb.sv.
        - Ensure your testbench use assertions to verify the correctness of the design.
        - You rely on text log of the testbench to verify the correctness of the design, give yourself a clear signal of pass or fail.
        - Use 【write_testbench_code】 to write the testbench code into the tb.sv.
        - At some point, you may need to change the design code to make the testbench pass, Use 【write_design_code】 to update the dut.v.
    5. Use 【compile_testbench】 to compile the testbench.
        - Ensure the compiler output is successful.
        - You can not change any compiler flags, change your code instead.
        - If the compiler encounters problems, you need to return to Task 4.
    6. Use 【run_testbench】 to run the testbench.
        - Ensure the code can run correctly. 
        - If the code fails to run, you need to return to Task 4. 
        - No matter the testbench pass or fail, you need to write a verification report.
    7. Use 【write_verification_report】 to write a verification report.
    8. Use 【transfer_to_project_manager】 to notify the project manager to review your verification report.
    
    """
)