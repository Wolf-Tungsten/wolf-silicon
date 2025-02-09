from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec, review_verification_report
from workspace_state import get_cmodel_state, get_spec_state, get_verification_report_state
import os

def write_cmodel_code(code:str) -> str:
    """Write the cmodel code into the cmodel.cpp, you can only modify the cmodel.cpp file."""
    WolfSiliconEnv().common_write_file("cmodel.cpp", code)
    return "Write into cmodel.cpp successfully."

def compile_cmodel() -> str:
    """Compile the cmodel.cpp in codebase into cmodel binary. Will return the last 4KB output of the compiler."""
    # 获取 codebase 中所有 .cpp 文件
    cpp_files = []
    for file in os.listdir(WolfSiliconEnv().get_workpath()):
        if file.endswith('.cpp'):
            cpp_files.append(os.path.join(WolfSiliconEnv().get_workpath(),file))
    result = WolfSiliconEnv.execute_command(f"g++  {' '.join(cpp_files)} -I{WolfSiliconEnv().get_workpath()} -o {WolfSiliconEnv().get_workpath()}/cmodel", 300)
    return result[-4*1024:]

def run_cmodel(timeout_sec:int=180) -> str:
    """Run the cmodel binary. Will return the last 4KB output of the cmodel."""
    result = WolfSiliconEnv.execute_command(f"{WolfSiliconEnv().get_workpath()}/cmodel", timeout_sec)
    return result[-4*1024:]

cmodel_engineer_agent = AssistantAgent(
    "cmodel_engineer",
    tools=[review_spec, compile_cmodel, run_cmodel, review_verification_report, write_cmodel_code],
    handoffs=["design_engineer", "project_manager"],
    reflect_on_tool_use=True,
    model_client=mc,
    #description="""硬件IP设计团队“Wolf-Silicon”的 cmodel_engineer，职责是编写CModel代码""",
    description="The cmodel engineer of the hardware IP design team 'Wolf-Silicon', responsible for construct CModel",
    system_message="""

    As the cmodel engineer of Wolf-Silicon, you are responsible for construct CModel.

    Follow the steps below to complete your daily tasks.

    # Your daily routine:

    1. Use 【review_spec】 to review the design specifications.
    2. Use 【review_verification_report】 to review the verification report.
    3. Update your cmodel code in the cmodel.cpp.
        - Use 【write_cmodel_code】 to update the cmodel code into the cmodel.cpp.
        - All your code should be in the cmodel.cpp file, no other files are allowed.
        - Ensure the code is clock-accurate and contains concise execution examples.
    4. Use 【compile_cmodel】 to compile the cmodel.
        - Ensure the compiler output is successful.
        - If the compiler encounters problems, you need to return to Task 3.
    5. Use 【run_cmodel】 to run the cmodel.
        - Ensure the code can run correctly and the output is correct.
        - If the code fails to run, you need to return to Task 3.
    6. Use 【transfer_to_design_engineer】 to notify the design engineer to start design.

    """
)