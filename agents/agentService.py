from agents.base_agent import BaseAgent


class AgentService():
    def __init__(self):
        pass

    def send_message(sender: BaseAgent, receiver:BaseAgent, message:str):
        sender.send_message(receiver, message)