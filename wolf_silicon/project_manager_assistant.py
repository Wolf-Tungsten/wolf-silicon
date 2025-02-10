from base_assistant import BaseAssistant
import json

class ProjectManagerAssistant(BaseAssistant):
    def __init__(self, agent) -> None:
        super().__init__(agent)
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
        
        You work according to the will of the Moon God, and if the project succeeds, you can transform into werewolves.

        Under your leadership are a team of wolves, which includes the CModel Engineer Wolf, the Design Engineer Wolf, and the Verification Engineer Wolf.

        You pay close attention to the moon's needs as well as the verification reports from the Verification Engineer Wolf.

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

            # Moon's Enlightening Requirements

            {user_requirements}

            # Your Task

            Submit a design spec according to the user requirements. - Use【submit_spec】

            """
        elif self.state == "review_verification_report":
            assert (user_requirements_exist)
            assert (spec_exist)
            assert (user_requirements_mtime < spec_mtime)
            assert (verification_report_exist)
            assert (verification_report_mtime > spec_mtime)
            return f"""
            # Project Status

            There is a verification report available for review.

            # Moon's Enlightening Requirements

            {user_requirements}

            # Design Spec

            {spec}

            # Verification Report

            {verification_report}

            # Your Task

            Review the verification report and decide whether to

            1. Approve the verification report and ask user for new requirements - Use【ask_user_requirements】

            OR

            2. Reject the verification report and add your constructives comment into design spec. - Use【submit_spec】

            """
        else:
            assert (user_requirements_exist)
            assert (spec_exist)
            assert (verification_report_exist)
            assert (user_requirements_mtime > spec_mtime)
            return f"""
            # Project Status

            Moon's Enlightening Requirements have been updated

            # Updated Moon's Enlightening Requirements

            {user_requirements}

            # Your Out-of-date Spec

            {spec}

            # Out-of-date Verification Report

            {verification_report}

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
                "name": "ask_user_requirements",
                "description": "Ask user for new requirements.",
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
                        self.reflect_tool_call(tool_id, "success")
                        self.state = "review_verification_report"
                        return "cmodel"
            elif self.state == "review_verification_report":
                for tool_call in llm_message.tool_calls:
                    _, name, args = self.decode_tool_call(tool_call)
                    if name == "ask_user_requirements":
                        self.env.ask_user_requirements()
                        self.state = "new_user_requirements"
                        return "user"
                    elif name == "submit_spec":
                        self.env.write_spec(args["spec"], args["overwrite"])
                        self.state = "review_verification_report"
                        return "cmodel" 




