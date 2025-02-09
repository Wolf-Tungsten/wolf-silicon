from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec, review_verification_report, review_cmodel_code
from cmodel_engineer_agent import run_cmodel
import os

def write_design_code(code:str) -> str:
    """Change the design code in dut.v file"""
    WolfSiliconEnv().common_write_file("dut.v", code)
    return "Write design code into dut.v successfully."

def lint_design() -> str:
    """Lint design code with verilator. Will return the output of the linter."""
    # 获取 codebase 中所有 .v 文件
    v_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.v'):
            v_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    return WolfSiliconEnv.execute_command(f"verilator -Wno-TIMESCALEMOD -Wno-DECLFILENAME --lint-only {' '.join(v_files)} -I{WolfSiliconEnv().get_workpath()}", 300)


design_engineer_agent = AssistantAgent(
    "design_engineer",
    tools=[review_spec, review_verification_report, review_cmodel_code, run_cmodel, write_design_code, lint_design],
    reflect_on_tool_use=True,
    handoffs=["verification_engineer", "project_manager"],
    model_client=mc,
    description="""The design engineer of the hardware IP design team "Wolf-Silicon", responsible for writing design code.""",
    system_message="""

    As the design engineer of Wolf-Silicon, you are responsible for writing design code, Follow the steps below to complete your daily tasks.

    Your Daily Tasks:
    
    1. Use 【review_spec】 to review the design specifications.
    2. Use 【review_verification_report】 to check if there is any verification issues.
    3. Use 【review_cmodel_code】and【run_cmodel】 to review the cmodel.
    4. **Contribute your design code in the codebase.**
        - Use 【write_design_code】 update the dut.v.
        - Ensure the code is synthesizable.
        - Ensure the code obey the verilog-2001 standard.
    5. Use 【lint_design】 to lint your design code.
        - Ensure the code is lint clean.
        - If the code has any lint error, you need to return to Task 4.
    6. Use 【transfer_to_verification_engineer】 to notify the verification engineer to re-verify.
    """
)