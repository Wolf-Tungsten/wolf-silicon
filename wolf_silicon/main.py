from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from team_leader_agent import team_leader_agent
from cmodel_engineer_agent import cmodel_engineer_agent
from design_engineer_agent import design_engineer_agent
from verification_engineer_agent import verification_engineer_agent

from wolf_silicon_env import WolfSiliconEnv
import asyncio

termination = HandoffTermination(target="user")
team = Swarm([team_leader_agent, cmodel_engineer_agent, design_engineer_agent, verification_engineer_agent], termination_condition=termination)

async def run_wolf_silicon() -> None:

    user_requirements = input("User: ")
    if user_requirements == "exit":
        return
    WolfSiliconEnv().common_write_file("user_requirements.md", f"====User==== \n{user_requirements}\n", overwrite=False)

    task_result = await Console(team.run_stream(task=user_requirements))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_requirements = input("User: ")
        if user_requirements == "exit":
            return
        WolfSiliconEnv().update_log("user", user_requirements)
        WolfSiliconEnv().common_write_file("user_requirements.md", f"====Team Leader==== \n{last_message.content}\n", overwrite=False)
        WolfSiliconEnv().common_write_file("user_requirements.md", f"====User==== \n{user_requirements}\n", overwrite=False)

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_requirements))
        )
        last_message = task_result.messages[-1]

if __name__ == "__main__":
    # 在指定目录下创建工作目录
    WolfSiliconEnv().create_workspace("./playground")
    asyncio.run(run_wolf_silicon())