from env import WolfSiliconEnv
import os
from project_manager_assistant import ProjectManagerAssistant
from cmodel_engineer_assistant import CModelEngineerAssistant
from design_engineer_assistant import DesignEngineerAssistant
from model_client import mc

class WolfSiliconAgent(object):
    def __init__(self, workspace_path, user_requirements_path=None, 
                 user_cmodel_code_path=None, 
                 user_design_code_path=None,
                 user_verification_code_path=None) -> None:
        # config
        self.MODEL_NAME = "gpt-4o"
        self.MAX_SHORT_TERM_MEMORY = 10
        self.MAX_RETRY = 10
        # connect to model_client
        self.model_client = mc
        # 在 workspace 目录下创建doc、cmodel、design、verification文件夹
        self.workspace_path = workspace_path
        self.doc_path = os.path.join(workspace_path, "doc")
        self.cmodel_path = os.path.join(workspace_path, "cmodel")
        self.design_path = os.path.join(workspace_path, "design")
        self.verification_path = os.path.join(workspace_path, "verification")
        os.makedirs(self.doc_path, exist_ok=False)
        os.makedirs(self.cmodel_path, exist_ok=False)
        os.makedirs(self.design_path, exist_ok=False)
        os.makedirs(self.verification_path, exist_ok=False)
        self.env = WolfSiliconEnv(self.doc_path, self.cmodel_path, self.design_path, self.verification_path)
        # 初始化环境
        # 读取用户需求，写入user_requirements.md
        if user_requirements_path:
            with open(user_requirements_path, "r") as f:
                user_requirements = f.read()
                self.env.write_user_requirements(user_requirements)
        else: # 用户未提供输入文件，提示用户输入需求
            user_requirements = input("User Requirements: ")
            self.env.write_user_requirements(user_requirements)
        if user_cmodel_code_path:
            # 如果用户提供了 C++ CModel 代码路径，复制其中文件到 cmodel 文件夹
            for filename in os.listdir(user_cmodel_code_path):
                os.copy(os.path.join(user_cmodel_code_path, filename), self.cmodel_path)
        if user_design_code_path:
            # 如果用户提供了 Verilog 设计代码路径，复制其中文件到 design 文件夹
            for filename in os.listdir(user_design_code_path):
                os.copy(os.path.join(user_design_code_path, filename), self.design_path)
        if user_verification_code_path:
            # 如果用户提供了 SystemVerilog 验证代码路径，复制其中文件到 verification 文件夹
            for filename in os.listdir(user_verification_code_path):
                os.copy(os.path.join(user_verification_code_path, filename), self.verification_path)
        # 创建 AssistantAgent
        # TODO
        self.project_manager_assistent = ProjectManagerAssistant(self)
        self.cmodel_engineer_assistant = CModelEngineerAssistant(self)
        self.design_engineer_assistant = DesignEngineerAssistant(self)

    def run(self):
        res = self.project_manager_assistent.execute()
        if res == "cmodel":
            self.cmodel_engineer_assistant.execute()
            self.design_engineer_assistant.execute()