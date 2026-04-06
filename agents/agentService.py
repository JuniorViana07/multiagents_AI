from agents.base_agent import BaseAgent


class AgentService():
    def __init__(self):
        pass

    def send_message(self ,sender: BaseAgent, receiver:BaseAgent, message):
        sender.send_message(receiver, message)