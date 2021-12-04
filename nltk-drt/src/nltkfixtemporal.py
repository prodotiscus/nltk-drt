from temporaldrt import DRS
from temporaldrt import DrtLambdaExpression
from temporaldrt import DrtApplicationExpression
from temporaldrt import DrtAbstractVariableExpression
from temporaldrt import DrtNegatedExpression
from temporaldrt import DrsDrawer

from nltk.sem.logic import BinaryExpression

def _handle(self, expression, command, x=0, y=0):
    """
    @param expression: the expression to handle
    @param command: the function to apply, either _draw_command or _visit_command
    @param x: the top of the current drawing area
    @param y: the left side of the current drawing area
    @return: the bottom-rightmost point
    """
    if command == self._visit_command:
        #if we don't need to draw the item, then we can use the cached values
        try:
            #attempt to retrieve cached values
            right = expression._drawing_width + x
            bottom = expression._drawing_height + y
            return (right, bottom)
        except AttributeError:
            #the values have not been cached yet, so compute them
            pass

    if isinstance(expression, DrtAbstractVariableExpression):
        factory = self._handle_VariableExpression
    elif isinstance(expression, DRS):
        factory = self._handle_DRS
    elif isinstance(expression, DrtNegatedExpression):
        factory = self._handle_NegatedExpression
    elif isinstance(expression, DrtLambdaExpression):
        factory = self._handle_LambdaExpression
    elif isinstance(expression, BinaryExpression):
        factory = self._handle_BinaryExpression
    elif isinstance(expression, DrtApplicationExpression):
        factory = self._handle_ApplicationExpression
    else:
        # TypeError instead of general exception
        raise TypeError(expression.__class__.__name__)

    (right, bottom) = factory(expression, command, x, y)

    #cache the values
    expression._drawing_width = right - x
    expression._drawing_height = bottom - y

    return (right, bottom)

DrsDrawer._handle = _handle
