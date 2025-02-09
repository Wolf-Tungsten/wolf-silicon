from model_client import mc
from wolf_silicon_env import WolfSiliconEnv
from autogen_agentchat.agents import AssistantAgent
from project_manager_agent import review_spec, review_verification_report
from codebase_tool import codebase_tools
from workspace_state import get_cmodel_state, get_spec_state, get_verification_report_state
import os

def checkout_task() -> str:
    """Checkout your task list."""
    spec_exist, spec_mtime = get_spec_state()
    cmodel_exist, cmodel_mtime = get_cmodel_state()
    verification_report_exist, verification_report_mtime = get_verification_report_state()
    
    if not spec_exist:
        return """
        # Project State

        There has no spec.md in the workspace.

        # Something goes wrong

        YOU HAVE TO【transfer_to_project_manager】NOW!

        """
    
    # spec exits below
    
    if not cmodel_exist:
        return """
        # Project State

        The cmodel is not exist.
        
        # Your Tasks Today

        **Task 1** Use 【review_spec】 to review the design specifications.
        **Task 2** Write your cmodel code in the codebase.
            - You can only create or modify .cpp/.h files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
            - Ensure the code is clock-accurate and contains concise execution examples.
        **Task 3** Use 【compile_cmodel】 to compile the cmodel.
            - Ensure the compiler output is successful.
            - If the compiler encounters problems, you need to return to Task 2.
        **Task 4** Use 【run_cmodel】 to run the cmodel.
            - Ensure the code can run correctly and the output is correct.
            - If the code fails to run, you need to return to Task 2.
        **Task 5** Use 【transfer_to_design_engineer】 to notify the design engineer to start design.
        """
    
    # spec and cmodel exist below

    if spec_mtime > cmodel_mtime:
        return """
        # Project State

        The cmodel is outdated.
        
        # Your Tasks Today

        **Task 1** Use 【review_spec】 to review the design specifications.
        **Task 2** Update your cmodel code in the codebase.
            - You can only create or modify .cpp/.h files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
            - Ensure the code is clock-accurate and contains concise execution examples.
        **Task 3** Use 【compile_cmodel】 to compile the cmodel.
            - Ensure the compiler output is successful.
            - If the compiler encounters problems, you need to return to Task 2.
        **Task 4** Use 【run_cmodel】 to run the cmodel.
            - Ensure the code can run correctly and the output is correct.
            - If the code fails to run, you need to return to Task 2.
        **Task 5** Use 【transfer_to_design_engineer】 to notify the design engineer to start design.
        """
    
    if verification_report_exist and (verification_report_mtime > cmodel_mtime):

        return """
        # Project State

        The cmodel is outdated, please refer to the verification report for the latest information.

        # Your Tasks Today

        **Task 1** Use 【review_spec】 to review the design specifications.
        **Task 2** Use 【review_verification_report】 to review the verification report.
        **Task 3** Update your cmodel code in the codebase.
            - You can only create or modify .cpp/.h files in the codebase.
            - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
            - Ensure the code is clock-accurate and contains concise execution examples.
        **Task 4** Use 【compile_cmodel】 to compile the cmodel.
            - Ensure the compiler output is successful.
            - If the compiler encounters problems, you need to return to Task 3.
        **Task 5** Use 【run_cmodel】 to run the cmodel.
            - Ensure the code can run correctly and the output is correct.
            - If the code fails to run, you need to return to Task 3.
        **Task 6** Use 【transfer_to_design_engineer】 to notify the design engineer to start design.
        """

    return """
    # Project State

    The cmodel is up-to-date.
    This project is still in progress.

    # Your Tasks Today

    - 【transfer_to_design_engineer】 to notify the design engineer to start design.
    """

def compile_cmodel() -> str:
    """Compile the .cpp/.h in codebase into cmodel binary. Will return the last 4KB output of the compiler."""
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
    tools=[review_spec, compile_cmodel, run_cmodel, review_verification_report, *codebase_tools],
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
    3. Update your cmodel code in the codebase.
        - You can only create or modify .cpp/.h files in the codebase.
        - Use codebase tools to edit code, if you don't know how to, Use【codebase_tool_help】.
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