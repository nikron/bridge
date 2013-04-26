from __future__ import absolute_import, division, print_function, unicode_literals
import abc

#
# Macro core logic
#

class Action(object):
    __metaclass__ = abc.ABCMeta
    
    """Provides a base class for all action (statement) types that may be
       included within a macro."""
    
    @abc.abstractmethod
    def execute(self, ctx):
        """Execute the logic represented by this Action instance against an
           ExecutionContext ctx."""
        pass

class ExecutionContext(object):
    def commit(self, label, newvalue):
        """Store the ExpressionValue newvalue in the variable named by
           label."""
        pass
        
    def retrieve(self, label):
        """Retrieve the value of the variable named by label."""
        pass

class Expression(object):
    """Provides a base class for all expression types that may be included
       within a macro."""
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def evaluate(self, ctx):
        """Process the logic contained within this Expression instance given
           an ExecutionContext ctx, producing an ExpressionValue representing
           the result."""
        pass

class ExpressionValue():
    """Represents the result of the evaluation of an expression."""
    
    INTEGER = 1
    BOOLEAN = 2
    STATUS_CONTEXT = 3

class Macro(object):
    def execute(self):
        ctx = ExecutionContext()
        self.body.execute(ctx)

#
# Macro expression types
#

class DifferenceExpression(Expression):
    """Implements an expression that evaluates the difference of two
       expressions."""
    
    def __init__(self, l, r):
        self.l = l
        self.r = r
    
    def evaluate(self, ctx):
        lv = l.evaluate(ctx)
        rv = r.evaluate(ctx)
        # TODO: Do the operation
        return None

class GetValueExpression(Expression):
    """Implements an expression type that retrieves a value from a variable
       in the current ExecutionContext."""
       
    def __init__(self, label):
        self.label = label
    
    def evaluate(self, ctx):
        return ctx.retrieve(self.label)

class LiteralExpression(Expression):
    """Implements an expression type that evaluates to a fixed value."""
    
    def __init__(self, value):
        self.value = value
    
    def evaluate(self, ctx):
        return self.value

class ProductExpression(Expression):
    """Implements an expression that evaluates the product of two
       expressions."""
    
    def __init__(self, l, r):
        self.l = l
        self.r = r
    
    def evaluate(self, ctx):
        lv = l.evaluate(ctx)
        rv = r.evaluate(ctx)
        # TODO: Do the operation
        return None

class QuotientExpression(Expression):
    """Implements an expression that evaluates the quotient of two
       expressions."""
    
    def __init__(self, l, r):
        self.l = l
        self.r = r
    
    def evaluate(self, ctx):
        lv = l.evaluate(ctx)
        rv = r.evaluate(ctx)
        # TODO: Do the operation
        return None

class SumExpression(Expression):
    """Implements an expression that evaluates the sum of two expressions."""
    
    def __init__(self, l, r):
        self.l = l
        self.r = r
    
    def evaluate(self, ctx):
        lv = l.evaluate(ctx)
        rv = r.evaluate(ctx)
        # TODO: Do the operation
        return None

#
# Macro action types
#

class ControlAssetAction(Action):
    """Implements an action type that executes a control command on an asset,
       providing a StatusContext value for a later suspend/unwrap operation."""
    
    def __init__(self, asset, attr, rhs, stlabel):
        self.asset = asset
        self.attr = attr
        self.rhs = rhs
        self.stlabel = stlabel
    
    def execute(self, ctx):
        # TODO: Set attr on asset to rhs and place StatusContext in stlabel
        pass

class CompositeAction(Action):
    """Implements an action type that executes a sequence of subactions."""
    
    def __init__(self, *subactions):
        self.subactions = subactions
    
    def execute(self, ctx):
        for act in self.subactions:
            act.execute(ctx)

class ConditionalAction(Action):
    """Implements an action type that conditionally executes its body
       contingent on the value of a condition (in other words, an if-block)."""
    
    def __init__(self, condition, thenaction, elseaction):
        self.condition = condition
        self.thenaction = thenaction
        self.elseaction = elseaction
    
    def execute(self, ctx):
        # TODO: Evaluate condition and execute body if true
        pass

class QueryAttributeAction(Action):
    """Implements an action type that initiates interrogation of some attribute
       of an asset, providing a StatusContext for a later suspend/unwrap
       operation."""
    def __init__(self, asset, attr, stlabel, timeout):
        self.asset = asset
        self.attr = attr
        self.stlabel = stlabel
        self.timeout = timeout
        
    def execute(self, ctx):
        # TODO: Interrogate attr on asset and place StatusContext in stlabel
        pass

class SetVariableAction(Action):
    """Implements an action type that stores a value as a variable in the
       current ExecutionContext."""
    
    def __init__(self, label, rhs):
        self.label = label
        self.rhs = rhs
    
    def execute(self, ctx):
        ctx.commit(self.label, self.rhs.evaluate(ctx))

class SuspendAction(Action):
    """Implements an action type that stalls execution until the operations
       associated with each specified StatusContext-valued expression
       have completed or failed."""
    
    def __init__(self, *targets):
        self.targets = targets
    
    def execute(self, ctx):
        # TODO: Stall until all target control jobs have completed/failed
        pass

class UpdateAttributeAction(Action):
    """Implements an action type that initiates commitment of some value to an
       attribute of an asset, providing a StatusContext value for a later
       suspend operation."""
    
    def __init__(self, asset, attr, rhs, stlabel):
        self.asset = asset
        self.attr = attr
        self.rhs = rhs
        self.stlabel = stlabel
    
    def execute(self, ctx):
        # TODO: Set attr on asset to rhs and place StatusContext in stlabel
        pass
