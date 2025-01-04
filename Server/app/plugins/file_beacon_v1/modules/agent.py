from modules.client import BaseAgent


class Agent(BaseAgent):
    def __init__(self, agent_id):
        super().__init__(agent_id=agent_id)  # Ensure BaseAgent is properly initialized

        # on creation, attempt to load from id

        self.register()
        print("ENQUEUING COMMANDS")
        self.enqueue_command(command="test")
        # self.dequeue()
        # self.unload_data()
        self.load_data()
