from modules.client import BaseClient


class Client(BaseClient):
    def __init__(self, id):
        super().__init__(id)  # Ensure BaseClient is properly initialized

        # on creation, attempt to load from id

        self.register()
        print("ENQUEUING COMMANDS")
        self.enqueue(command="test")
        # self.dequeue()

    # these are going to need to be redis based.
    # def enqueue(self):
    #     """
    #     Enqueues a command
    #     """
    #     ...

    # def dequeue(self):
    #     """
    #     Deques a command
    #     """
    #     ...

    # Keep working on this
    # docs
