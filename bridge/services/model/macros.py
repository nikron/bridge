import abc

#
# Macro core
#

class ExecutionContext():
    def commit(self, varLabel, newValue):
        """Store the ExpressionValue newValue in the variable named by
           varLabel."""
        pass
        
    def retrieve(self, varLabel):
        """Retrieve the value of the variable named by varLabel."""
        pass

class Macro():    
    def execute(self):
        ctx = ExecutionContext()
        self.body.execute(ctx)

#
# Macro expression types
#

class Expression(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def evaluate(self, ctx):
        """Process the logic contained within this Expression instance given
           an ExecutionContext ctx, producing an ExpressionValue representing
           the result."""
        pass

class ExpressionValue():
    pass

#
# Macro action types
#

class Action(metaclass=abc.ABCMeta):
    """Provides a base class for all actions, which are statement types that
       may be included within a macro."""
    
    @abc.abstractmethod
    def execute(self, ctx):
        """Execute the logic represented by this Action instance against an
           ExecutionContext ctx."""
        pass

class ControlAssetAction(Action):
    """Implements an Action that initiates commitment of some value to an
       attribute of an asset, providing a StatusContext value for a later
       SuspendAction."""
    
    def __init__(self, asset, attr, rhs, stVarLabel):
        self.asset = asset
        self.attr = attr
        self.rhs = rhs
        self.stVarLabel = stVarLabel
    
    def execute(self, ctx):
        # TODO: Set attr on asset to rhs and place StatusContext in stVarLabel
        pass

class CompositeAction(Action):
    """Implements an Action that executes a sequence of subactions as one."""
    
    def __init__(self, *subactions):
        self.subactions = subactions
    
    def execute(self, ctx):
        for act in self.subactions:
            act.execute(ctx)

class ConditionalAction(Action):
    """Implements an Action that conditionally executes its body contingent
       on the value of a condition (in other words, an if-block)."""
    
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def execute(self, ctx):
        # TODO: Evaluate condition and execute body if true
        pass

class SetVariableAction(Action):
    """Implements an Action that stores a value as a variable in the current
       ExecutionContext."""
    
    def __init__(self, varLabel, rhs):
        self.varLabel = varLabel
        self.rhs = rhs
    
    def execute(self, ctx):
        ctx.commit(self.varLabel, self.rhs.evaluate(ctx))

class SuspendAction(Action):
    """Implements an Action that stalls execution until the operations
       associated with each specified StatusContext-valued expression
       have completed or failed."""
    
    def __init__(self, *targets):
        self.targets = targets
    
    def execute(self, ctx):
        # TODO: Stall until all target control jobs have completed/failed
        pass
