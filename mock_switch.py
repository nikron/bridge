class MockSwitch:

    def __init__(self):
        self.on = False

    def turn_off(self):
        self.on = False

    def turn_on(self):
        self.on = True

    def toggle(self):
        self.on = not self.on
