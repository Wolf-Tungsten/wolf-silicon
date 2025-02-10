import json

class BaseAssistant(object):

    def __init__(self, agent) -> None:
        self.env = agent.env
        self.name = "BaseAssistant"
        self.agent = agent
        self.short_term_memory = []

    def log(self, msg: str):
        self.env.log(f"[{self.name}] {msg}")

    def update_short_term_memory(self, msg: object):
        self.short_term_memory.append(msg)
        if len(self.short_term_memory) > self.agent.MAX_SHORT_TERM_MEMORY:
            self.short_term_memory.pop(0)

    def clear_short_term_memory(self):
        self.short_term_memory.clear()

    def get_short_term_memory(self):
        return self.short_term_memory

    def get_long_term_memory(self):
        raise NotImplementedError(
            "get_long_term_memory() method must be implemented by subclass.")

    def get_tools_description(self):
        raise NotImplementedError(
            "get_tools_description() method must be implemented by subclass.")

    def get_system_prompt(self):
        raise NotImplementedError(
            "get_system_prompt() method must be implemented by subclass.")
    
    def decode_tool_call(self, tool_call):
        return tool_call.id, tool_call.function.name, json.loads(tool_call.function.arguments)
    
    def reflect_tool_call(self, id, result):
        self.update_short_term_memory({
            "role":"tool",
            "tool_call_id":id,
            "content":result
        })
        messages = [
            {
                "role": "developer",
                "content": self.get_system_prompt()
            },
            {
                "role": "user",
                "content": self.get_long_term_memory()
            },
            *self.get_short_term_memory()
        ]
        completion = self.agent.model_client.chat.completions.create(
            model=self.agent.MODEL_NAME,
            messages=messages,
            tools=self.get_tools_description(),
            tool_choice="none"
        )
        self.update_short_term_memory(completion.choices[0].message)
        print(completion.choices[0].message)


    def call_llm(self, user_message, tools_enable):
        self.update_short_term_memory({
            "role": "user",
            "content": user_message
        })
        messages = [
            {
                "role": "developer",
                "content": self.get_system_prompt()
            },
            {
                "role": "user",
                "content": self.get_long_term_memory()
            },
            *self.get_short_term_memory()
        ]
        completion = self.agent.model_client.chat.completions.create(
            model=self.agent.MODEL_NAME,
            messages=messages,
            tools=self.get_tools_description(),
            tool_choice="required" if tools_enable else "none"
        )
        self.update_short_term_memory(completion.choices[0].message)
        print(completion.choices[0].message)
        return completion.choices[0].message
