from base_assistant import BaseAssistant

class CModelEngineerAssistant(BaseAssistant):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.name = "CModel Engineer Wolf"
        # State wait_cmodel, cmodel_outdated
        self.state = "wait_cmodel"
    
    def get_system_prompt(self):
        return """
        In the vast plains, there is a pack of wolves skilled in hardware IP design.

        You are the CModel Engineer among them. 
        
        Guided by the Lunar Deity, your project holds the promise of transforming into werewolves upon success.

        Within the team are the Project Manager Wolf, Design Engineer Wolf, and Verification Engineer Wolf.

        The Project Manager Wolf converts the Lunar Deity's enlightening requirements into a design specification, which serves as the foundation for your CModel.

        Your CModel aids both the Design Engineer Wolf and Verification Engineer Wolf in completing the design.

        Please be mindful to use the language of wolves in your communication, and make sure to use the tools correctly.
        """
        
    def get_long_term_memory(self):
        user_requirements_exist, user_requirements_mtime, user_requirements = self.env.get_user_requirements()
        spec_exist, spec_mtime, spec = self.env.get_spec()
        cmodel_code_exist, cmodel_code_mtime, cmodel_code = self.env.get_cmodel_code()
        verification_report_exist, verification_report_mtime, verification_report = self.env.get_verification_report()

        if self.state == "wait_cmodel":
            assert(spec_exist)
            return f"""
            # Project Status

            Waiting for CModel Engineer Wolf's CModel

            # Lunar Deity's Enlightening Requirements

            {user_requirements}

            # Project Manager Wolf's Design Specification

            {spec}

            # Your Task

            Submit a CModel according to the design specification. - Use【submit_cmodel】

            Your CModel should be cycle-accurate and output at least 5 example cases.

            The other team member won't see your code, but only foucs on the output of your CModel.
            """
        else:
            assert(cmodel_code_exist)
            assert(verification_report_exist)
            return f"""
            # Project Status

            The CModel is outdated.

            # Lunar Deity's NEW Enlightening Requirements

            {user_requirements}

            # Project Manager Wolf's NEW Design Specification

            {spec}

            # Your Previous CModel Output

            {self.env.compile_and_run_cmodel()}

            # Your Task

            Update the CModel according previous materials. - Use【submit_cmodel】

            Your CModel should be cycle-accurate and output at least 5 example cases.

            The other team member won't see your code, but only foucs on the output of your CModel.
            
            """
    
    def submit_cmodel(self, code):
        self.env.manual_log(self.name, "提交了 CModel 设计代码")
        self.env.write_cmodel_code(code)
        compile_run_output = self.env.compile_and_run_cmodel()
        return compile_run_output
    
    def ready_to_handover(self) -> bool:
        spec_code_exist, spec_mtime, _ = self.env.get_spec()
        cmodel_code_exist, cmodel_code_mtime, _ = self.env.get_cmodel_code()
        return cmodel_code_exist and cmodel_code_mtime > spec_mtime and self.env.is_cmodel_binary_exist()
    
    def get_tools_description(self):
        
        submit_cmodel = {
            "type": "function",
            "function": {
                "name": "submit_cmodel",
                "description": "Submit Your CModel Code. The CModel Code Saved in a single .cpp file. Your CModel Code will be compiled and run automatically after submission.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "CModel Cpp Code"}
                    },
                    "required": ["code"],
                    "additionalProperties": False
                }
            }
        }
        handover_to_design = {
            "type": "function",
            "function": {
                "name": "handover_to_design",
                "description": "Handover the CModel to the Design Engineer Wolf for further design.",
                "strict": True
            }
        }

        if self.ready_to_handover():
            return [submit_cmodel, handover_to_design]
        else:
            return [submit_cmodel]
    
    def execute(self):
        self.clear_short_term_memory()
        self.call_llm("Observe and analyze the project situation, show me your observation and think", tools_enable=False)

        handover = False
        while not handover:
            if not self.ready_to_handover():
                llm_message = self.call_llm("""
                    Please submit your CModel code.

                    All CModel code is assumed to be in a single .cpp file.
                    Your CModel code should be cycle-accurate and provide a golden reference for the design.
                    Your CModel code should be able to run and give a consistent output.
                    Your CModel code will be automatically compiled and run after submission, Please Note the Result.

                    """, tools_enable=True)
            else:
                llm_message = self.call_llm(f"""
                There is a CModel binary and the execution result is
                ```
                {self.env.run_cmodel()}
                ```
                Please decide whether to:
                
                handover the CModel to the Design Engineer Wolf Use 【handover_to_design】
                
                OR

                resubmit the CModel code Use 【submit_cmodel】

                """, tools_enable=True)
            for tool_call in llm_message.tool_calls:
                tool_id, name, args = self.decode_tool_call(tool_call)
                if name == "submit_cmodel":
                    cmodel_output = self.submit_cmodel(args["code"])
                    self.reflect_tool_call(tool_id, cmodel_output)
                elif name == "handover_to_design":
                    self.env.manual_log(self.name, "将 CModel 交付给设计工程狼")
                    self.state = "cmodel_outdated"
                    return
                

