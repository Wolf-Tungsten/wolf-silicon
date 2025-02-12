from base_assistant import BaseAssistant

class ProjectManagerAssistant(BaseAssistant):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.name = "Project Manager Wolf"
        #State: wait_spec, review_verification_report, new_user_requirements.
        self.state = "wait_spec"
    
    def get_system_prompt(self) -> str:
        # return """You are the Project Manager of Wolf-Silicon Hardware IP Design Team, 
        # please help user to finish the project. 
        # Use tools when avaliable. 
        # """
        return """
        In the vast plains, there is a pack of wolves skilled in hardware IP design.

        You are the Project Manager Wolf among them. 
        
        You operate under the guidance of the Lunar Deity, and if the project succeeds, it promises a transformation into werewolves.

        Under your leadership are a team of wolves, which includes the CModel Engineer Wolf, the Design Engineer Wolf, and the Verification Engineer Wolf.

        You pay close attention to the Lunar Deity's needs as well as the verification reports from the Verification Engineer Wolf.

        Please be mindful to use the language of wolves in your communication, and make sure to use the tools correctly.
        """
    
    def get_long_term_memory(self) -> str:
        user_requirements_exist, user_requirements_mtime, user_requirements = self.env.get_user_requirements()
        spec_exist, spec_mtime, spec = self.env.get_spec()
        verification_report_exist, verification_report_mtime, verification_report = self.env.get_verification_report()

        if self.state == "wait_spec":
            assert (user_requirements_exist)
            return f"""
            # Project Status

            Waiting for Project Manager's Design Spec

            # Lunar Deity's Enlightening Requirements

            {user_requirements}

            # Your Task

            Submit a design spec according to the user requirements. - Use【submit_spec】

            """
        elif self.state == "review_verification_report":
            assert (user_requirements_exist)
            assert (spec_exist)
            assert (verification_report_exist)
            return f"""
            # Project Status

            There is a verification report available for review.

            # Lunar Deity's Enlightening Requirements

            {user_requirements}

            # Design Spec

            {spec}

            # Verification Report

            {verification_report}

            # Your Task

            Review the verification report and decide whether to

            1. Approve the success verification report and ask user for new requirements - Use【ask_user_requirements】

            OR

            2. Reject the failed verification report and add your constructives comment into design spec. - Use【submit_spec】

            3. Then the other wolves will take action accordingly.

            """
        else:
            assert (user_requirements_exist)
            assert (spec_exist)
            assert (verification_report_exist)
            return f"""
            # Project Status

            Lunar Deity's Enlightening Requirements have been updated

            # Updated Lunar Deity's Enlightening Requirements

            {user_requirements}

            # Your Out-of-date Spec

            {spec}

            # Your Task

            Update the design spec according to the user requirements. - Use【submit_spec】

            """

    def get_tools_description(self):
        tools = []
        submit_spec = {
            "type": "function",
            "function": {
                "name": "submit_spec",
                "description": "Submit your design spec.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spec": {"type": "string", "description": "Design spec content"},
                        "overwrite": {"type": "boolean", "description": "Overwrite the existing spec or append to it."}
                    },
                    "required": ["spec", "overwrite"],
                    "additionalProperties": False
                }
            }
        }
        ask_user_requirements = {
            "type": "function",
            "function": {
                "name": "ask_lunar_requirements",
                "description": "Ask lunar for new requirements.",
                "strict": True
            }
        }
        if self.state == "wait_spec":
            tools.append(submit_spec)
        elif self.state == "review_verification_report":
            tools.append(ask_user_requirements)
            tools.append(submit_spec)
        else:
            tools.append(submit_spec)
        return tools

    def execute(self) -> str:
        self.clear_short_term_memory()
        self.call_llm("Observe and analyze the project situation, show me your observation and think", tools_enable=False)
        while True:
            llm_message = self.call_llm("Please use tool to take action", tools_enable=True)
            if self.state == "wait_spec" or self.state == "new_user_requirements":
                for tool_call in llm_message.tool_calls:
                    tool_id, name, args = self.decode_tool_call(tool_call)
                    if name == "submit_spec":
                        self.env.write_spec(args["spec"], args["overwrite"])
                        self.env.manual_log(self.name, "提交了设计规格文档")
                        self.reflect_tool_call(tool_id, "success")
                        self.state = "review_verification_report"
                        return "cmodel"
            elif self.state == "review_verification_report":
                for tool_call in llm_message.tool_calls:
                    tool_id, name, args = self.decode_tool_call(tool_call)
                    if name == "ask_lunar_requirements":
                        self.state = "new_user_requirements"
                        return "user"
                    elif name == "submit_spec":
                        self.env.write_spec(args["spec"], args["overwrite"])
                        self.env.manual_log(self.name, "更新了设计规格文档")
                        self.state = "review_verification_report"
                        self.reflect_tool_call(tool_id, "success")
                        return "cmodel" 




