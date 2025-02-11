from base_assistant import BaseAssistant

class DesignEngineerAssistant(BaseAssistant):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.name = "Design Engineer Wolf"
        # State wait_design, design_outdated
        self.state = "wait_design"
    
    def get_system_prompt(self):
        return """
        In the vast plains, there is a pack of wolves skilled in hardware IP design.

        You are the Design Engineer Wolf among them. 
        
        Guided by the Lunar Deity, your project holds the promise of transforming into werewolves upon success.

        Within the team are the Project Manager Wolf, CModel Engineer Wolf, and Verification Engineer Wolf.

        The Project Manager Wolf converts the Lunar Deity's enlightening requirements into a design specification.

        The CModel Engineer Wolf provides a CModel that serves as a golden reference for your design.

        You are responsible for converting the design specification into a Verilog IP Design.

        Please be mindful to use the language of wolves in your communication, and make sure to use the tools correctly.
        """
        
    def get_long_term_memory(self):
        
        spec_exist, spec_mtime, spec = self.env.get_spec()
        cmodel_code_exist, cmodel_code_mtime, cmodel_code = self.env.get_cmodel_code()
        design_code_exist, design_code_mtime, design_code = self.env.get_design_code()
        verification_report_exist, verification_report_mtime, verification_report = self.env.get_verification_report()

        if self.state == "wait_design":
            assert(spec_exist)
            assert(cmodel_code_exist)
            return f"""
            # Project Status

            Waiting for Design Engineer Wolf's Design

            # Project Manager Wolf's Design Specification

            {spec}

            # CModel Engineer Wolf's CModel Code

            {cmodel_code}

            # CModel Engineer Wolf's CModel Excution Result

            {self.env.compile_and_run_cmodel()}

            # Your Task

            Submit a Verilog Design - Use【submit_design】
            """
        else:
            assert(spec_exist)
            assert(cmodel_code_exist)
            assert(design_code_exist)
            assert(verification_report_exist)
            return f"""
            # Project Status

            The Design is outdated.

            # Project Manager Wolf's NEW Design Specification

            {spec}

            # CModel Engineer Wolf's NEW CModel Code

            {cmodel_code}

            # CModel Engineer Wolf's NEW CModel Excution Result

            {self.env.compile_and_run_cmodel()}

            # Your Previous Design Code

            {design_code}

            # Previous Verification Report for your Reference

            (is there any issue in the verification report?)

            {verification_report}

            # Your Task

            Update your design - Use【submit_design】

            """
    
    def submit_design(self, code):
        self.env.write_design_code(code)
        lint_output = self.env.lint_design()
        return f"Your design code submit successfully, and the lint result is:\n```\n{lint_output}\n```\n, is the lint result clean?"
    
    def ready_to_handover(self) -> bool:
        cmodel_code_exist, cmodel_code_mtime, _ = self.env.get_cmodel_code()
        design_code_exist, design_code_mtime, _ = self.env.get_design_code()
        return design_code_exist and design_code_mtime > cmodel_code_mtime
    
    def get_tools_description(self):
        
        submit_design = {
            "type": "function",
            "function": {
                "name": "submit_design",
                "description": "Submit Your Verilog Design Code. The Design Code Saved in a single .v file. Your Design Code will be lint automatically after submission.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Design Verilog Code"}
                    },
                    "required": ["code"],
                    "additionalProperties": False
                }
            }
        }
        handover_to_verification = {
            "type": "function",
            "function": {
                "name": "handover_to_verification",
                "description": "Handover the Design to the Verification Engineer Wolf for further verification.",
                "strict": True
            }
        }

        if self.ready_to_handover():
            return [submit_design, handover_to_verification]
        else:
            return [submit_design]
    
    def execute(self):
        self.clear_short_term_memory()
        self.call_llm("Observe and analyze the project situation, show me your observation and think", tools_enable=False)

        while True:
            if not self.ready_to_handover():
                llm_message = self.call_llm("""
                    Please submit your Design code.

                    All Design code is assumed to be in a single .v file.
                    Your Design code should be synthesizable and obey the verilog-2001 standard.
                    Your Design code should be lint clean.
                    Your Design code will be automatically lint after submission, Please Note the Result.

                    """, tools_enable=True)
            else:
                llm_message = self.call_llm(f"""
                There is a Verilog Design Code and the lint result is
                ```
                {self.env.lint_design()}
                ```
                Please decide whether to:
                
                handover the Design to the Verification Engineer Wolf Use 【handover_to_verification】
                
                OR

                resubmit the Design code Use 【submit_design】

                """, tools_enable=True)
            for tool_call in llm_message.tool_calls:
                tool_id, name, args = self.decode_tool_call(tool_call)
                if name == "submit_design":
                    lint_output = self.submit_design(args["code"])
                    self.reflect_tool_call(tool_id, lint_output)
                elif name == "handover_to_verification":
                    self.state = "design_outdated"
                    return
                

