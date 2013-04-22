import abc

class Operation(metaclass=abc.ABCMeta):
    NOT_INITIATED = 1
    PENDING = 2
    COMPLETED = 3
    FAILED = 4
    
    def __init__(self):
        self.status = Operation.NOT_INITIATED
    
    def initiate(self):
        pass
    
    def join(self):
        pass

class ControlAssetOperation(Operation):
    pass

class InterrogateAssetOperation(Operation):
    pass
