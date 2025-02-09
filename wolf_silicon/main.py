from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from project_manager_agent import project_manager_agent
from cmodel_engineer_agent import cmodel_engineer_agent
from design_engineer_agent import design_engineer_agent
from verification_engineer_agent import verification_engineer_agent

from wolf_silicon_env import WolfSiliconEnv
import asyncio
import argparse

termination = HandoffTermination(target="user")
team = Swarm([project_manager_agent, cmodel_engineer_agent, design_engineer_agent, verification_engineer_agent], termination_condition=termination)

async def run_wolf_silicon(user_requirements) -> None:

    if user_requirements is None:
        user_requirements = input("User Requirements: ")
    if user_requirements == "exit":
        return
    WolfSiliconEnv().common_write_file("user_requirements.md", f"====User==== \n{user_requirements}\n", overwrite=False)

    task_result = await Console(team.run_stream(task=user_requirements))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_requirements = input("User (new requirments or exit): ")
        if user_requirements == "exit":
            return
        WolfSiliconEnv().common_write_file("user_requirements.md", f"====Team Leader==== \n{last_message.content}\n", overwrite=False)
        WolfSiliconEnv().common_write_file("user_requirements.md", f"====User==== \n{user_requirements}\n", overwrite=False)

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_requirements))
        )
        last_message = task_result.messages[-1]

if __name__ == "__main__":
    # 设置可选参数 --req 
    parser = argparse.ArgumentParser()
    parser.add_argument("--req", type=str, help="User requirements file path")
    args = parser.parse_args()
    if args.req is not None:
        with open(args.req, "r") as f:
            args.req = f.read()
    # 在指定目录下创建工作目录
    WolfSiliconEnv().create_workspace("./playground")
    asyncio.run(run_wolf_silicon(args.req))