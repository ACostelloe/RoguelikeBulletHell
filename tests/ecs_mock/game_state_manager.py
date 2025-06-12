class MockGameState:
    def __init__(self, name):
        self.name = name

class MockGameStateManager:
    def __init__(self):
        self.state_stack = []

    @property
    def current_state(self):
        return self.state_stack[-1] if self.state_stack else None

    def set_state(self, name):
        self.state_stack = [MockGameState(name)]

    def push_state(self, name):
        self.state_stack.append(MockGameState(name))

    def pop_state(self):
        if self.state_stack:
            self.state_stack.pop() 