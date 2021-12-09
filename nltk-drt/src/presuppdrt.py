"""
NLTK DRT module extended with presuppositions
"""

__author__ = "Alex Kislev, Emma Li, Peter Makarov"
__version__ = "1.0"
__date__ = "Tue, 24 Aug 2010"

import re
import operator

from nltk.sem.logic import Variable
from nltk.sem.logic import EqualityExpression, ApplicationExpression, ExistsExpression, AndExpression
from nltk.sem.logic import IndividualVariableExpression
from nltk.sem.logic import _counter, is_eventvar, is_funcvar
from nltk.sem.logic import BasicType
from nltk.sem.logic import Expression
# ParseException -> LogicalExpressionException
from nltk.sem.logic import LogicalExpressionException
from nltk.sem.logic import ImpExpression, BooleanExpression, IffExpression
from nltk.sem.drt import DrsDrawer, AnaphoraResolutionException

import nltk.sem.drt as drt


class TimeType(BasicType):
    """
    Basic type of times added on top of nltk.sem.logic.
    """
    def __str__(self):
        return 'i'

    def str(self):
        return 'TIME'

TIME_TYPE = TimeType()

class StateType(BasicType):
    """
    Basic type of states added on top of nltk.sem.logic.
    """
    def __str__(self):
        return 's'

    def str(self):
        return 'STATE'

STATE_TYPE = StateType()

def is_indvar(expr):
    """
    An individual variable must be a single lowercase character other than 'e', 't', 'n', 's',
    followed by zero or more digits.

    @param expr: C{str}
    @return: C{boolean} True if expr is of the correct form
    """
    assert isinstance(expr, str), "%s is not a string" % expr
    return re.match(r'^[a-df-mo-ru-z]\d*$', expr)

def is_timevar(expr):
    """
    An time variable must be a single lowercase 't' or 'n' character followed by
    zero or more digits. Do we need a separate type for utterance time n?

    @param expr: C{str}
    @return: C{boolean} True if expr is of the correct form
    """
    assert isinstance(expr, str), "%s is not a string" % expr
    return re.match(r'^[tn]\d*$', expr)


def is_statevar(expr):
    """
    An state variable must be a single lowercase 's' character followed by
    zero or more digits.

    @param expr: C{str}
    @return: C{boolean} True if expr is of the correct form
    """
    assert isinstance(expr, str), "%s is not a string" % expr
    return re.match(r'^s\d*$', expr)


def is_uttervar(expr):
    """
    An utterance time variable must be a single lowercase 'n' character followed by
    zero or more digits.

    @param expr: C{str}
    @return: C{boolean} True if expr is of the correct form
    """
    assert isinstance(expr, str), "%s is not a string" % expr
    return re.match(r'^n\d*$', expr)


def unique_variable(pattern=None, ignore=None):
    """
    Return a new, unique variable.
    param pattern: C{Variable} that is being replaced.  The new variable must
    be the same type.
    param term: a C{set} of C{Variable}s that should not be returned from
    this function.
    return: C{Variable}
    """
    if pattern is not None:
        if is_indvar(pattern.name):
            prefix = 'z'
        elif is_funcvar(pattern.name):
            prefix = 'F'
        elif is_eventvar(pattern.name):
            prefix = 'e0'
        elif is_timevar(pattern.name):
            prefix = 't0'
        elif is_statevar(pattern.name):
            prefix = 's0'
        else:
            assert False, "Cannot generate a unique constant"
    else:
        prefix = 'z'

    v = Variable(prefix + str(_counter.get()))
    while ignore is not None and v in ignore:
        v = Variable(prefix + str(_counter.get()))
    return v

class TimeVariableExpression(IndividualVariableExpression):
    """This class represents variables that take the form of a single lowercase
    'i' character followed by zero or more digits."""
    type = TIME_TYPE

class StateVariableExpression(IndividualVariableExpression):
    """This class represents variables that take the form of a single lowercase
    's' character followed by zero or more digits."""
    type = STATE_TYPE

def is_unary_predicate(expr):
    """check whether the given expression is an unary predicate"""
    return isinstance(expr, DrtApplicationExpression) and isinstance(expr.function, DrtAbstractVariableExpression)

class ReverseIterator:
    """A generator which yields the given sequence in a reverse order"""
    def __init__(self, sequence, start= -1):
        self.sequence = sequence
        self.start = start
    def __iter__(self):
        if self.start > 0:
            i = self.start + 1
        else:
            i = len(self.sequence) + self.start + 1
        while i > 0:
            i -= 1
            yield self.sequence[i]

class Reading(list):
    """
    A single reading, consists of a list of operations
    each operation is a tuple of a DRS and a function,
    where the function would be executed on the given DRS
    when the reading is generated
    """
    pass

class Binding(Reading):
    pass

class LocalAccommodation(Reading):
    pass

class IntermediateAccommodation(Reading):
    pass

class GlobalAccommodation(Reading):
    pass

class VariableReplacer(object):
    """A generic variable replacer functor to be used in readings"""
    def __init__(self, var, new_var, remove_ref=True):
        self.var = var
        self.new_var = new_var
        self.remove_ref = remove_ref
    def __call__(self, drs):
        if self.remove_ref:
            drs.refs.remove(self.var)
        return drs.__class__(drs.refs, [cond.replace(self.var, self.new_var, False) for cond in drs.conds])

class ConditionReplacer(object):
    """
    A generic condition replacer functor to be used in readings
    replace the condition at the given index with any number of
    conditions, optionally adds a referent
    """
    def __init__(self, index, conds, ref=None):
        self.index = index
        self.conds = conds
        self.ref = ref
    def __call__(self, drs):
        if self.ref:
            drs.refs.append(self.ref)
        drs.conds[self.index:self.index + 1] = self.conds
        return drs

class ConditionRemover(object):
    """A generic condition remover functor to be used in readings"""
    def __init__(self, cond_index):
        self.cond_index = cond_index
    def __call__(self, drs):
        drs.conds.pop(self.cond_index)
        return drs

class ResolutionException(Exception):
    pass

class DrtTokens(drt.DrtTokens):
    OPEN_BRACE = '{'
    CLOSE_BRACE = '}'
    PUNCT = [OPEN_BRACE, CLOSE_BRACE]
    SYMBOLS = drt.DrtTokens.SYMBOLS + PUNCT
    TOKENS = drt.DrtTokens.TOKENS + PUNCT
    NEWINFO_DRS = 'NEWINFO'
    PROPER_NAME_DRS = 'PROP'
    DEFINITE_DESCRIPTION_DRS = 'DEF'
    PRONOUN_DRS = 'PRON'
    PRESUPPOSITION_DRS = [PROPER_NAME_DRS, DEFINITE_DESCRIPTION_DRS, PRONOUN_DRS]
    PRONOUN = 'PRO'
    REFLEXIVE_PRONOUN = 'RPRO'
    POSSESSIVE_PRONOUN = 'PPRO'
    # ??
    NLTK = 'NLTK'

class DrtExpression(drt.DrtExpression):
    """
    A base abstract DRT Expression from which every DRT Expression inherits.
    """

    def applyto(self, other):
        return DrtApplicationExpression(self, other)

    def __neg__(self):
        return DrtNegatedExpression(self)

    def __or__(self, other):
        assert isinstance(other, DrtExpression)
        return DrtOrExpression(self, other)

    def __gt__(self, other):
        assert isinstance(other, DrtExpression)
        return DrtImpExpression(self, other)

    def __lt__(self, other):
        assert isinstance(other, DrtExpression)
        return DrtIffExpression(self, other)

    def __add__(self, other):
        return ConcatenationDRS(self, other)

    def __deepcopy__(self, memo):
        return self.deepcopy()

    def make_EqualityExpression(self, first, second):
        return DrtEqualityExpression(first, second)

    def make_VariableExpression(self, variable):
        return DrtVariableExpression(variable)

    def normalize(self):
        """Rename auto-generated unique variables"""
        def f(e):
            if isinstance(e, Variable):
                if re.match(r'^z\d+$', e.name) or re.match(r'^[est]0\d+$', e.name):
                    return set([e])
                else:
                    return set([])
            else:
                combinator = lambda * parts: reduce(operator.or_, parts)
                return e.visit(f, combinator, set())

        result = self
        for i, v in enumerate(sorted(list(f(self)))):
            if is_eventvar(v.name):
                newVar = 'e0%s' % (i + 1)
            elif is_timevar(v.name):
                newVar = 't0%s' % (i + 1)
            elif is_statevar(v.name):
                newVar = 's0%s' % (i + 1)
            else:
                newVar = 'z%s' % (i + 1)
            result = result.replace(v,
                        self.make_VariableExpression(Variable(newVar)), True)
        return result

    def substitute_bindings(self, bindings):
        expr = self
        for var in expr.variables():
            val = bindings.get(var, None)
            if val:
                if isinstance(val, Variable):
                    val = DrtVariableExpression(val)
                elif isinstance(val, Expression):
                    val = val.substitute_bindings(bindings)
                elif isinstance(val, str):
                    val = DrtFeatureExpression(Variable(val))
                else:
                    raise ValueError('Can not substitute a non-expression '
                                         'value into an expression: %r' % (val,))
                expr = expr.replace(var, val)
        return expr.simplify()

    RESOLUTION_ORDER = {Binding:0,
                        GlobalAccommodation:1,
                        IntermediateAccommodation:2,
                        LocalAccommodation:3}

    def resolve(self, inference_check=None, verbose=False):
        """
        This method does the whole job of collecting multiple readings.
        We aim to get new readings from the old ones by resolving
        presuppositional DRSs one by one. Every time one presupposition
        is resolved, new readings are created and replace the old ones,
        until there are no presuppositions left to resolve.
        """
        readings = []
        errors = []
        if inference_check:
            failed_readings = []

        def traverse(base_reading, operations):
            for operation in sorted(operations, key=lambda o: DrtExpression.RESOLUTION_ORDER[type(o)]):
                new_reading = base_reading.deepcopy(operation)
                if verbose:
                    print("reading: %s" % new_reading)
                try:
                    new_operations = new_reading.readings()
                except Exception as ex:
                    errors.append(str(ex))
                    continue
                if not new_operations:
                    if inference_check:
                        success, error = inference_check(new_reading)
                        if success:
                            readings.append(new_reading)
                            return True
                        else:
                            failed_readings.append((new_reading, error))
                    else:
                        readings.append(new_reading)
                else:
                    if traverse(new_reading, new_operations[0]):
                        if len(operations) == 1 or DrtExpression.RESOLUTION_ORDER[type(operation)] != 0:
                            return True
            return False

        operations = self.readings()
        if operations:
            traverse(self, operations[0])
        else:
            return [self]

        if not readings and errors:
            raise ResolutionException(". ".join(errors))
        return readings, failed_readings if inference_check else readings

    def readings(self, trail=[]):
        raise NotImplementedError()

class DRS(DrtExpression, drt.DRS):
    """A Temporal Discourse Representation Structure."""

    def fol(self):
        if not self.conds:
            raise Exception("Cannot convert DRS with no conditions to FOL.")
        accum = reduce(AndExpression, [c.fol() for c in self.conds])
        for ref in ReverseIterator(self.refs):
            accum = ExistsExpression(ref, AndExpression(accum, self._ref_type(ref).fol()))
        return accum

    def _ref_type(self, referent):
        """Checks a referent type and returns corresponding predicate"""
        ref_cond = None
        if is_eventvar(referent.name):
            ref_cond = drt.DrtConstantExpression(Variable("event"))
        elif is_statevar(referent.name):
            ref_cond = drt.DrtConstantExpression(Variable("state"))
        elif is_timevar(referent.name):
            ref_cond = drt.DrtConstantExpression(Variable("time"))
        else:
            ref_cond = drt.DrtConstantExpression(Variable("individual"))

        return DrtApplicationExpression(ref_cond, DrtAbstractVariableExpression(referent))


    def replace(self, variable, expression, replace_bound=False):
        """Replace all instances of variable v with expression E in self,
        where v is free in self."""
        if variable in self.get_refs():
            #if a bound variable is the thing being replaced
            if not replace_bound:
                return self
            else:
                if variable in self.refs:
                    i = self.refs.index(variable)
                    refs = self.refs[:i] + [expression.variable] + self.refs[i + 1:]
                else:
                    refs = self.refs
                return self.__class__(refs,
                           [cond.replace(variable, expression, True) for cond in self.conds])
        else:
            #variable not bound by this DRS

            # any bound variable that appears in the expression must
            # be alpha converted to avoid a conflict
            for ref in (set(self.get_refs()) & expression.free()):
                newvar = unique_variable(ref)
                newvarex = DrtVariableExpression(newvar)
                if ref in self.refs:
                    i = self.refs.index(ref)
                    refs = self.refs[:i] + [newvar] + self.refs[i + 1:]
                else:
                    refs = self.refs
                self = self.__class__(refs,
                           [cond.replace(ref, newvarex, True)
                            for cond in self.conds])

            #replace in the conditions
            return self.__class__(self.refs,
                       [cond.replace(variable, expression, replace_bound)
                        for cond in self.conds])

    def free(self, indvar_only=True):
        """@see: Expression.free()"""
        conds_free = reduce(operator.or_,
                            [c.free(indvar_only) for c in self.conds], set())
        return conds_free - (set(self.refs) | reduce(operator.or_, [set(c.refs) for c in self.conds if isinstance(c, PresuppositionDRS)], set()))

    def get_refs(self, recursive=False):
        """@see: AbstractExpression.get_refs()"""
        if recursive:
            cond_refs = reduce(operator.add,
                               [c.get_refs(True) for c in self.conds], [])
            return self.refs + cond_refs
        else:
            return self.refs + reduce(operator.add, [c.refs for c in self.conds if isinstance(c, PresuppositionDRS)], [])

    def deepcopy(self, operations=[]):
        """This method returns a deep copy of the DRS.
        Optionally, it can take a list of lists of tuples (DRS, function)
        as an argument and generate a reading by performing
        a substitution in the DRS as specified by the function.
        @param operations: a list of lists of tuples
        """
        functions = [function for drs, function in operations if drs is self]
        newdrs = self.__class__(list(self.refs), [cond.deepcopy(operations) for cond in self.conds])
        for function in functions:
            newdrs = function(newdrs)
        return newdrs

    def simplify(self):
        return self.__class__(self.refs, [cond.simplify() for cond in self.conds])

    def readings(self, trail=[]):
        """get the readings for this DRS"""
        for i, cond in enumerate(self.conds):
            _readings = cond.readings(trail + [self])
            if _readings:
                if _readings[1]:
                    for reading in _readings[0]:
                        reading.append((self, ConditionRemover(i)))
                return _readings[0], False

    #def str(self, syntax=DrtTokens.NLTK):
    def str(self, syntax=None):
        if syntax == DrtTokens.PROVER9:
            return self.fol().str(syntax)
        else:
            return '([%s],[%s])' % (','.join([str(r) for r in self.refs]),
                                    ', '.join([c.str(syntax) for c in self.conds]))

def DrtVariableExpression(variable):
    """
    This is a factory method that instantiates and returns a subtype of
    C{DrtAbstractVariableExpression} appropriate for the given variable.
    """

    if is_indvar(variable.name):
        return DrtIndividualVariableExpression(variable)
    elif is_funcvar(variable.name):
        return DrtFunctionVariableExpression(variable)
    elif is_eventvar(variable.name):
        return DrtEventVariableExpression(variable)
    elif is_statevar(variable.name):
        return DrtStateVariableExpression(variable)
    elif is_uttervar(variable.name):
        return DrtUtterVariableExpression(variable)
    elif is_timevar(variable.name):
        return DrtTimeVariableExpression(variable)
    else:
        return DrtConstantExpression(variable)


class DrtAbstractVariableExpression(DrtExpression, drt.DrtAbstractVariableExpression):
    def readings(self, trail=[]):
        return None

    def deepcopy(self, operations=[]):
        return self.__class__(self.variable)

class DrtIndividualVariableExpression(DrtAbstractVariableExpression, drt.DrtIndividualVariableExpression):
    pass

class DrtFunctionVariableExpression(DrtAbstractVariableExpression, drt.DrtFunctionVariableExpression):
    pass

class DrtEventVariableExpression(DrtIndividualVariableExpression, drt.DrtEventVariableExpression):
    pass

class DrtTimeVariableExpression(DrtIndividualVariableExpression, TimeVariableExpression):
    """expression of discourse referents of time"""
    pass

class DrtStateVariableExpression(DrtIndividualVariableExpression, StateVariableExpression):
    """expression of discourse referents of state"""
    pass

class DrtConstantExpression(DrtAbstractVariableExpression, drt.DrtConstantExpression):
    pass

class DrtUtterVariableExpression(DrtTimeVariableExpression):
    """expression of utterance time referent"""
    pass

class DrtFeatureExpression(DrtConstantExpression):
    """expression for a single syntactic feature"""
    pass

class DrtFeatureConstantExpression(DrtConstantExpression):
    """A constant expression with syntactic features attached"""
    def __init__(self, variable, features):
        DrtConstantExpression.__init__(self, variable)
        self.features = features

    def replace(self, variable, expression, replace_bound=False):
        """@see: Expression.replace()"""
        assert isinstance(variable, Variable), "%s is not a Variable" % variable
        assert isinstance(expression, Expression), "%s is not an Expression" % expression
        return self.__class__(DrtConstantExpression.replace(self, variable, expression, replace_bound).variable, [feature.replace(variable, expression, replace_bound) for feature in self.features])

    def visit(self, function, combinator, default):
        """@see: Expression.visit()"""
        re = combinator(function(self.variable), reduce(combinator,
                      [function(e) for e in self.features], default))
        return re

    def str(self, syntax=DrtTokens.NLTK):
        return str(self.variable) + "{" + ",".join([str(feature) for feature in self.features]) + "}"

    def deepcopy(self, operations=[]):
        return self.__class__(self.variable, self.features)

    def fol(self):
        return DrtConstantExpression(self.variable)

class DrtProperNameExpression(DrtConstantExpression):
    """proper names"""
    pass

class DrtNegatedExpression(DrtExpression, drt.DrtNegatedExpression):
    def readings(self, trail=[]):
        return self.term.readings(trail + [self])

    def deepcopy(self, operations=None):
        return self.__class__(self.term.deepcopy(operations))

class DrtLambdaExpression(DrtExpression, drt.DrtLambdaExpression):
    def alpha_convert(self, newvar):
        """Rename all occurrences of the variable introduced by this variable
        binder in the expression to @C{newvar}.
        @param newvar: C{Variable}, for the new variable
        """
        return self.__class__(newvar, self.term.replace(self.variable,
                          DrtVariableExpression(newvar), True))

    def replace(self, variable, expression, replace_bound=False):
        """@see: Expression.replace()"""
        assert isinstance(variable, Variable), "%s is not a Variable" % variable
        assert isinstance(expression, Expression), "%s is not an Expression" % expression
        #if the bound variable is the thing being replaced
        if self.variable == variable:
            if replace_bound:
                assert isinstance(expression, DrtAbstractVariableExpression), \
                       "%s is not a AbstractVariableExpression" % expression
                return self.__class__(expression.variable,
                                      self.term.replace(variable, expression, True))
            else:
                return self
        else:
            # if the bound variable appears in the expression, then it must
            # be alpha converted to avoid a conflict
            if self.variable in expression.free():
                self = self.alpha_convert(unique_variable(pattern=self.variable))

            #replace in the term
            return self.__class__(self.variable,
                                  self.term.replace(variable, expression, replace_bound))

    def readings(self, trail=[]):
        return self.term.readings(trail + [self])

    def deepcopy(self, operations=[]):
        return self.__class__(self.variable, self.term.deepcopy(operations))

    def get_refs(self, recursive=False):
        """@see: AbstractExpression.get_refs()"""
        return []


class DrtBooleanExpression(DrtExpression, drt.DrtBooleanExpression):
    def readings(self, trail=[]):
        first_readings = self.first.readings(trail + [self])
        if first_readings:
            return first_readings
        else:
            return self.second.readings(trail + [self])

    def deepcopy(self, operations=[]):
        return self.__class__(self.first.deepcopy(operations), self.second.deepcopy(operations))

    def simplify(self):
        """When dealing with DRSs, it is good to have unique names for
        the referents bound by each DRS."""
        if isinstance(self.first, DRS) and isinstance(self.second, DRS):
            new_second = self.second
            for ref in set(self.first.get_refs(True)) & set(self.second.get_refs(True)):
                newref = DrtVariableExpression(unique_variable(ref))
                new_second = self.second.replace(ref, newref, True)

            return drt.DrtBooleanExpression.simplify(self.__class__(self.first, new_second))

        else:
            return drt.DrtBooleanExpression.simplify(self)

class DrtOrExpression(DrtBooleanExpression, drt.DrtOrExpression):
    pass


class DrtImpExpression(DrtBooleanExpression, ImpExpression):
    def fol(self):
        first_drs = self.first
        second_drs = self.second

        accum = None
        if first_drs.conds:
            accum = reduce(AndExpression,
                           [c.fol() for c in first_drs.conds])

        if accum:
            accum = ImpExpression(accum, second_drs.fol())
        else:
            accum = second_drs.fol()

        for ref in first_drs.refs[::-1]:
            accum = AllExpression(ref, accum)

        return accum

    def readings(self, trail=[]):
        first_readings = self.first.readings(trail + [self])
        if first_readings:
            return first_readings
        else:
            return self.second.readings(trail + [self, self.first])

    def __eq__(self, other):
        if (isinstance(self, other.__class__) or isinstance(other, self.__class__)):
            if isinstance(self.first, DRS) and isinstance(self.second, DRS) and isinstance(other.first, DRS) and isinstance(other.second, DRS):
                if len(self.first.conds) == len(other.first.conds) and len(self.second.conds) == len(other.second.conds):
                    for (r1, r2) in zip(self.first.refs + self.second.refs, other.first.refs + other.second.refs):
                        varex = self.make_VariableExpression(r1)
                        other = other.replace(r2, varex, True)
                    return self.first.conds == other.first.conds and self.second.conds == other.second.conds
            else:
                return self.first == other.first and self.second == other.second
        return False


class DrtIffExpression(DrtBooleanExpression, IffExpression):
    def fol(self):
        return IffExpression(self.first.fol(), self.second.fol())


class DrtEqualityExpression(DrtExpression, drt.DrtEqualityExpression):
    def readings(self, trail=[]):
        return None

    def deepcopy(self, operations=[]):
        return self.__class__(self.first.deepcopy(operations), self.second.deepcopy(operations))

class ConcatenationDRS(DrtBooleanExpression):
    """DRS of the form '(DRS + DRS)'"""
    def replace(self, variable, expression, replace_bound=False):
        """Replace all instances of variable v with expression E in self,
        where v is free in self."""
        first = self.first
        second = self.second

        # If variable is bound by both first and second
        if isinstance(first, DRS) and isinstance(second, DRS) and \
           variable in (set(first.get_refs(True)) & set(second.get_refs(True))):
            first = first.replace(variable, expression, True)
            second = second.replace(variable, expression, True)

        # If variable is bound by first
        elif isinstance(first, DRS) and variable in first.refs:
            if replace_bound:
                first = first.replace(variable, expression, replace_bound)
                second = second.replace(variable, expression, replace_bound)

        # If variable is bound by second
        elif isinstance(second, DRS) and variable in second.refs:
            if replace_bound:
                first = first.replace(variable, expression, replace_bound)
                second = second.replace(variable, expression, replace_bound)

        else:
            # alpha convert every ref that is free in 'expression'
            for ref in (set(self.get_refs(True)) & expression.free()):
                v = DrtVariableExpression(unique_variable(ref))
                first = first.replace(ref, v, True)
                second = second.replace(ref, v, True)

            first = first.replace(variable, expression, replace_bound)
            second = second.replace(variable, expression, replace_bound)

        return self.__class__(first, second)

    def simplify(self):
        first = self.first.simplify()
        second = self.second.simplify()

        if isinstance(first, DRS) and isinstance(second, DRS):
            # For any ref that is in both 'first' and 'second'
            for ref in (set(first.get_refs(True)) & set(second.get_refs(True))):
                # alpha convert the ref in 'second' to prevent collision
                newvar = DrtVariableExpression(unique_variable(ref))
                second = second.replace(ref, newvar, True)

            #DRS type is derived from the first member or from the second one
            drs_type = first.__class__ if isinstance(first, PresuppositionDRS) else second.__class__
            return drs_type(first.refs + second.refs, first.conds + second.conds)
        else:
            return self.__class__(first, second)

    def get_refs(self, recursive=False):
        """@see: AbstractExpression.get_refs()"""
        return self.first.get_refs(recursive) + self.second.get_refs(recursive)

    def getOp(self, syntax=DrtTokens.NLTK):
        return DrtTokens.DRS_CONC

    def __eq__(self, other):
        r"""Defines equality modulo alphabetic variance.
        If we are comparing \x.M  and \y.N, then check equality of M and N[x/y]."""
        if isinstance(other, ConcatenationDRS):
            self_refs = self.get_refs()
            other_refs = other.get_refs()
            if len(self_refs) == len(other_refs):
                converted_other = other
                for (r1,r2) in zip(self_refs, other_refs):
                    varex = self.make_VariableExpression(r1)
                    converted_other = converted_other.replace(r2, varex, True)
                return self.first == converted_other.first and \
                        self.second == converted_other.second
        return False

    def fol(self):
        return AndExpression(self.first.fol(), self.second.fol())


class DrtApplicationExpression(DrtExpression, drt.DrtApplicationExpression):

    def fol(self):
        if self.is_propername():
            return EqualityExpression(self.function.fol(),
                                      self.argument.fol())

        else: return ApplicationExpression(self.function.fol(),
                                           self.argument.fol())

    def is_propername(self):
        """
        A proper name is capitalised. We assume that John(x) uniquely
        identifies the bearer of the name John and so, when going from Kamp & Reyle's
        DRT format into classical FOL logic, we change a condition like that into John = x.

        @return: C{boolean} True if expr is of the correct form
        """
        return isinstance(self.function, DrtConstantExpression) and\
        self.function.variable.name.istitle()

    def readings(self, trail=[]):
        function_readings = self.function.readings(trail + [self])
        if function_readings:
            return function_readings
        else:
            return self.argument.readings(trail + [self])

    def deepcopy(self, operations=[]):
        return self.__class__(self.function.deepcopy(operations), self.argument.deepcopy(operations))

class DrtEventualityApplicationExpression(DrtApplicationExpression):
    """application expression with state or event argument"""
    pass

class PresuppositionDRS(DRS):

    def readings(self, trail=[]):
        inner_readings = DRS.readings(self, trail)
        if inner_readings:
            return inner_readings
        else:
            self._init_presupp_data()
            return self._presupposition_readings(trail)

    def _find_outer_drs(self, trail):
        for expr in trail:
            if expr.__class__ is DRS:
                return expr

    def _find_local_drs(self, trail):
        drs = None
        for expr in ReverseIterator(trail):
            if drs:
                if not isinstance(expr, DrtNegatedExpression):
                    return drs
                else: drs = None
            if expr.__class__ is DRS:
                drs = expr
        return drs

    def is_possible_binding(self, cond):
        return is_unary_predicate(cond) and self.has_same_features(cond) and cond.argument.__class__ is DrtIndividualVariableExpression

    def find_bindings(self, trail, collect_event_data=False, filter=lambda x: type(x) is DRS, individuals=None):
        bindings = []
        if collect_event_data:
            event_data_map = {}
            event_strings_map = {}
        is_bindable = True # do not allow forward binding
        for drs in (expr for expr in trail if filter(expr)):
            for cond in drs.conds:
                # Ignore conditions following the presupposition DRS
                if cond is self:
                    if not collect_event_data:
                        break # assuming that the filtered_trail has drss ordered from the outermost to the innermost
                if not isinstance(cond, DrtApplicationExpression):
                    continue
                    is_bindable = False
                if is_bindable and self.is_possible_binding(cond):
                    bindings.append(cond)
                if collect_event_data:
                    self.collect_event_data(cond, event_data_map, event_strings_map, individuals)
        if collect_event_data:
            self._enrich_event_data_map(event_data_map, event_strings_map)
        return (bindings, event_data_map) if collect_event_data else bindings

    def collect_event_data(self, cond, event_data_map, event_strings_map, individuals=None):
        if isinstance(cond.function, DrtApplicationExpression) and \
        isinstance(cond.argument, DrtIndividualVariableExpression) and not isinstance(cond.argument, DrtTimeVariableExpression):
                event_data_map.setdefault(cond.argument.variable, []).append((cond.function.argument, cond.function.function.variable.name))
        elif cond.__class__ == DrtEventualityApplicationExpression and \
        (isinstance(cond.argument, DrtEventVariableExpression) or isinstance(cond.argument, DrtStateVariableExpression)) and\
        not isinstance(cond.function, DrtApplicationExpression):
            assert cond.argument not in event_strings_map
            event_strings_map[cond.argument] = cond.function.variable.name
        # The rest are nouns and attributive adjectives
        elif individuals is not None and cond.__class__ == DrtApplicationExpression and \
        not isinstance(cond.function, DrtApplicationExpression):
            individuals.setdefault(cond.argument.variable, []).append(cond)

    def _enrich_event_data_map(self, event_data_map, event_strings_map):
        for individual in event_data_map:
            new_event_list = []
            for event_tuple in event_data_map[individual]:
                new_event_list.append((event_tuple[0], event_tuple[1], event_strings_map.get(event_tuple[0], None)))
            event_data_map[individual] = new_event_list

    def is_presupposition_cond(self, cond):
        return True

    def _init_presupp_data(self):
        presupp_cond_list = [cond for cond in self.conds if is_unary_predicate(cond) and cond.argument.variable == self.refs[0] and self.is_presupposition_cond(cond)]
        for cond in presupp_cond_list:
            if isinstance(cond.function, DrtFeatureConstantExpression): # this is the one
                # There can be more than one DrtFeatureConstantExpression on the conditions on list, e.g.
                # "Tom, a kind boy, took her hand", or "Tom, who is a kind boy,...", or "Linguist Grimm suggested ...",
                # or "The distinguished physicist Einstein ...". But 'is_presupposition_cond' helps us find the right one.
                self.variable = cond.argument.variable
                self.features = cond.function.features
                self.function_name = cond.function.variable.name
                self.cond = cond
                return

        self.variable = self.refs[0]
        self.features = None
        self.function_name = presupp_cond_list[0].variable.name
        self.cond = presupp_cond_list[0]

    def has_same_features(self, cond):
        return (not isinstance(cond.function, DrtFeatureConstantExpression) and not self.features) \
                or (isinstance(cond.function, DrtFeatureConstantExpression) and cond.function.features == self.features)

    def _get_condition_index(self, superordinate_drs, trail, condition_index_cache={}):
        # Keep a condition index cache
        if not condition_index_cache:
            condition_index_cache = {}
        superordinate_drs_index = id(superordinate_drs)
        if superordinate_drs_index in condition_index_cache:
            return condition_index_cache[superordinate_drs_index]
        # Use a for loop and 'is' to find the condition.
        # Do not use index(), because it calls a time-consuming equals method.
        for ind, trailee in enumerate(trail):
            if trailee is superordinate_drs:
                # The condition might be not in superordinate_drs, but inside one of its conditions (however deep we might need to go)
                look_for = trail[ind + 1] if ind < len(trail) - 1 else self
                for i, cond in enumerate(superordinate_drs.conds):
                    if cond is look_for:
                        condition_index_cache[superordinate_drs_index] = i
                        return i # condition_index
        return None

    class Operation(object):
        """An interface for all operations"""
        def __call__(self, drs):
            raise NotImplementedError

    class Accommodate(Operation):
        def __init__(self, presupp_drs, condition_index):
            # We need the condition index so that the conditions are not just appended to the list of conditions of the DRS,
            # but inserted where the presuppositional DRS had been. The order of conditions is important, because it reflects
            # the proximity of a possible antecedent, which affects antecedent ranking (and our architecture does not allow us to use the
            # index on the list of referents to reflect the proximity/thematic role).
            self.presupp_drs = presupp_drs
            self.condition_index = condition_index
        def __call__(self, drs):
            """Accommodation: put all referents and conditions from
            the presupposition DRS into the given DRS"""
            drs.refs.extend(self.presupp_drs.refs)
            if self.condition_index is None:
                drs.conds.extend(self.presupp_drs.conds)
            else:
                drs.conds = drs.conds[:self.condition_index + 1] + self.presupp_drs.conds + drs.conds[self.condition_index + 1:]
            return drs

    class Bind(Operation):
        def __init__(self, presupp_drs, presupp_variable, presupp_funcname, antecedent_cond, condition_index):
            self.presupp_drs = presupp_drs
            self.presupp_variable = presupp_variable
            self.presupp_funcname = presupp_funcname
            self.antecedent_cond = antecedent_cond
            self.condition_index = condition_index
        def __call__(self, drs):
            """Put all conditions from the presuppositional DRS into the DRS (but do not create duplicates),
            and replace the presupposition condition referent in them with antecedent referent"""
            newdrs = self.presupp_drs.replace(self.presupp_variable, self.antecedent_cond.argument, True)
            # There will be referents and conditions to move
            # if there is a relative clause modifying the noun that has triggered the presuppositon
            drs.refs.extend([ref for ref in newdrs.refs \
                             if ref != self.antecedent_cond.argument.variable])
            conds_to_move = [cond for cond in newdrs.conds \
                             if not cond in drs.conds]
            # Put the conditions at the position of the original presupposition DRS
            if self.condition_index is None: # it is an index, it can be zero
                drs.conds.extend(conds_to_move)
            else:
                drs.conds = drs.conds[:self.condition_index + 1] + conds_to_move + drs.conds[self.condition_index + 1:]
            return drs

    class InnerReplace(Operation):
        def __init__(self, presupp_variable, antecedent_ref):
            self.presupp_variable = presupp_variable
            self.antecedent_ref = antecedent_ref
        def __call__(self, drs):
                """In the conditions of the local DRS, replace the
                referent of the presupposition condition with antecedent_ref"""
                return drs.replace(self.presupp_variable, self.antecedent_ref, True)

    class MoveTemporalConditions(Operation):
        def __init__(self, temporal_conditions):
            self.temporal_conditions = temporal_conditions
        def __call__(self, drs):
                drs.conds.extend(self.temporal_conditions)
                return drs

    class DoMultipleOperations(Operation):
        def __init__(self, operations_list):
            self.operations_list = operations_list

        def __call__(self, drs):
            """Do the operations one by one"""
            for operation in self.operations_list:
                drs = operation(drs)
            return drs

    def binding_reading(self, inner_drs, target_drs, antecedent_cond, trail, temporal_conditions=None, local_drs=None):
        condition_index = self._get_condition_index(target_drs, trail)
        binder = self.Bind(self, self.variable, self.function_name, antecedent_cond, condition_index)
        inner_replacer = self.InnerReplace(self.variable, antecedent_cond.argument)
        temp_cond_mover = self.MoveTemporalConditions(temporal_conditions) if temporal_conditions else None
        if inner_drs is target_drs:
            if temp_cond_mover:
                if local_drs is target_drs:
                    return Binding([(inner_drs, binder), (inner_drs, temp_cond_mover), (inner_drs, inner_replacer)])
                else:
                    return Binding([(local_drs, temp_cond_mover),
                                    (inner_drs, binder), (inner_drs, inner_replacer)])
            else:
                return Binding([(inner_drs, binder), (inner_drs, inner_replacer)])
        else:
            if temp_cond_mover:
                if local_drs is target_drs:
                    return Binding([(target_drs, binder), (target_drs, temp_cond_mover),
                                    (inner_drs, inner_replacer)])
                elif local_drs is inner_drs:
                    return Binding([(target_drs, binder),
                                    (inner_drs, temp_cond_mover), (inner_drs, inner_replacer)])
                else:
                    return Binding([(target_drs, binder),
                                    (local_drs, temp_cond_mover),
                                    (inner_drs, inner_replacer)])
            else:
                return Binding([(target_drs, binder),
                        (inner_drs, inner_replacer)])

    def accommodation_reading(self, target_drs, trail, temporal_conditions=None, local_drs=None, reading_type=Binding):
        condition_index = self._get_condition_index(target_drs, trail)
        accommodator = self.Accommodate(self, condition_index)
        if temporal_conditions:
            temp_cond_mover = self.MoveTemporalConditions(temporal_conditions)
            if local_drs is target_drs:
                return reading_type([(target_drs, temp_cond_mover), (target_drs, accommodator)])
            else:
                return reading_type([(target_drs, accommodator),
                                (local_drs, temp_cond_mover)])
        else:
            return reading_type([(target_drs, accommodator)])

class PronounDRS(PresuppositionDRS):
    """
    A class for DRSs for personal, reflexive, and possessive pronouns
    """
    PRONOUNS = [DrtTokens.PRONOUN, DrtTokens.REFLEXIVE_PRONOUN, DrtTokens.POSSESSIVE_PRONOUN]

    def is_presupposition_cond(self, cond):
        return cond.function.variable.name in PronounDRS.PRONOUNS

    def _presupposition_readings(self, trail=[]):
        #trail[0].draw()
        possible_bindings, event_data = self.find_bindings(trail, True, filter=lambda x: x.__class__ is DRS or isinstance(x, PresuppositionDRS))
        bindings = [cond for cond in possible_bindings if self._is_binding(cond, self._get_pro_events(event_data), event_data)]
        ranked_bindings = self._rank_bindings(bindings, event_data)
        return [Binding([(trail[-1], VariableReplacer(self.variable, cond.argument, False))]) for cond, rank in sorted(ranked_bindings, key=lambda e: e[1], reverse=True)], True

    def _get_pro_events(self, event_data):
        #in case pronoun participates in only one eventuality, which has no other participants,
        #try to extend it with interlinked eventualities
        #f.e. THEME(z5,z3), THEME(e,z5) where z3 only participates in eventuality z5
        #will be extended to participate in e, but only in case z5 has one participant
        pro_events = [event for event, role, event_string in event_data.get(self.variable, ())]
        if len(pro_events) == 1:
            pro_event = pro_events[0]
            #number of participants in the pro_event
            participant_count = sum((1 for event_list in event_data.itervalues() for event, role, event_string in event_list if event == pro_event))
            # if there is only one participant in the pro_event and pro_event itself participates in other eventualities
            if participant_count == 1 and pro_event.variable in event_data:
                pro_events.extend((event for event, role, event_string in event_data[pro_event.variable]))

        return set(pro_events)

    def _rank_bindings(self, bindings, event_data):
        #ranking system
        #increment ranking for matching roles and map the positions of antecedents
        if len(bindings) == 0:
            raise AnaphoraResolutionException("Variable '%s' does not "
                                "resolve to anything." % self.variable)
        elif len(bindings) == 1:
            bindings[0] = (bindings[0], 0)
        else:
            pro_roles = set((role for event, role, event_string in event_data.get(self.variable, ())))
            for index, variable in enumerate(bindings):
                var_roles = set((role for event_list in event_data.get(variable, ()) for event, role, event_string in event_list))
                bindings[index] = (variable, index + len(var_roles.intersection(pro_roles)))
        return bindings

    def _is_binding(self, cond, pro_events, event_data):
        #non reflexive pronouns can not resolve to variables having a role in the same eventuality
        if self.function_name == DrtTokens.POSSESSIVE_PRONOUN:
            return True
        else:
            variable = cond.argument.variable
            variable_events = set((event for event, role, event_string in event_data.get(variable, ())))
        if self.function_name == DrtTokens.PRONOUN:
            return variable_events.isdisjoint(pro_events)
        elif self.function_name == DrtTokens.REFLEXIVE_PRONOUN:
            return not variable_events.isdisjoint(pro_events)
        else:
            return True

class ProperNameDRS(PresuppositionDRS):

    def _presupposition_readings(self, trail=[]):
        """A proper name always has one reading: it is either global binding
        or global accommodation (if binding is not possible)"""
        outer_drs = self._find_outer_drs(trail)
        inner_drs = trail[-1]
        possible_bindings = self.find_bindings([outer_drs])

        assert len(possible_bindings) <= 1
        if possible_bindings:
            # Return the reading
            return [self.binding_reading(inner_drs, outer_drs, possible_bindings[0], trail)], True
        # If no suitable antecedent has been found in the outer DRS,
        # binding is not possible, so we go for accommodation instead.
        return [self.accommodation_reading(outer_drs, trail)], True

    def is_possible_binding(self, cond):
        return super(ProperNameDRS, self).is_possible_binding(cond) and cond.is_propername() and cond.function.variable.name == self.function_name

    def is_presupposition_cond(self, cond):
        return cond.is_propername()

class DefiniteDescriptionDRS(PresuppositionDRS):

    def _presupposition_readings(self, trail=[], overgenerate=False, generate_intermediate=True):
        # If there is a restrictive clause or an adjunct PP, find the perfect binding or accommodate the presupposition
        presupp_event_data = {}
        presupp_event_strings = {}
        presupp_individuals = {}
        # Are there any states/events in this presuppositional DRS that the presupposition referent takes part in?
        for cond in (c for c in self.conds if isinstance(c, DrtApplicationExpression)):
            self.collect_event_data(cond, presupp_event_data, presupp_event_strings, presupp_individuals)
        self._enrich_event_data_map(presupp_event_data, presupp_event_strings)

        possible_bindings = {}
        event_data = {}
        individuals = {}
        accommod_indices = set()
        intermediate_next = False # find the closest antecedent DRS
        outer_drs = self._find_outer_drs(trail)
        local_drs = self._find_local_drs(trail)
        all_refs = []
        free, temporal_conditions = self._get_free()
        # Go through the filtered trail, find bindings and find the intermediate DRS for possible accommodation
        for index, drs in enumerate(trail):
            if isinstance(drs, DrtImpExpression): intermediate_next = True
            if not drs.__class__ is DRS: continue
            # Free variable check
            if not self._free_variable_check(drs, free, all_refs):
                intermediate_next = False
                continue
            # Find the (maximum) three DRSs
            if drs is outer_drs or drs is local_drs or intermediate_next:
                accommod_indices.add(index)
                intermediate_next = False
            # Find the bindings
            drs_possible_bindings, drs_event_data = self.find_bindings([drs], True, individuals=individuals)
            for var in drs_event_data: event_data.setdefault(var, []).extend(drs_event_data[var])
            if drs_possible_bindings:
                possible_bindings[index] = drs_possible_bindings

        # Make accommodation indices a sorted list
        accommod_indices = sorted(list(accommod_indices))
        def accommodation_cite(drsindex):#LocalAccommodation, IntermediateAccommodation, GlobalAccommodation
            if not drsindex in accommod_indices:
                return None
            ind = accommod_indices.index(drsindex)
            if ind == 0:
                return [LocalAccommodation, GlobalAccommodation, GlobalAccommodation][len(accommod_indices) - 1]
            elif ind == 1:
                return [LocalAccommodation, IntermediateAccommodation][len(accommod_indices) - 2]
            else:
                assert ind == 2
                return LocalAccommodation

        # Filter the bindings, create the readings
        antecedent_tracker = [] # do not bind to the same referent twice
        readings = []
        inner_drs = trail[-1]
        for drsindex, drs in enumerate(trail):
            drs_readings = []
            if drsindex in possible_bindings:
                for cond in ReverseIterator(possible_bindings[drsindex]):
                    variable = cond.argument.variable
                    if self._is_binding(variable, individuals[variable], self._get_defdescr_events(event_data), event_data, presupp_event_data, presupp_individuals) and \
                    not cond.argument in antecedent_tracker:
                        antecedent_tracker.append(cond.argument)
                        drs_readings.append(self.binding_reading(inner_drs, drs, \
                                                                         cond, trail, temporal_conditions, local_drs))
            # If binding is possible, no accommodation at this level or below will take place
            # (unless we set the 'overgenerate' parameter to True)
            if not overgenerate and drs_readings: accommod_indices = [None]
            else:
                acc_cite = accommodation_cite(drsindex)
                if acc_cite and not (generate_intermediate is False and acc_cite is IntermediateAccommodation):
                    drs_readings.append(self.accommodation_reading(drs, trail, temporal_conditions, local_drs, acc_cite))
                    accommod_indices.remove(drsindex)
            readings.extend(drs_readings)

        return readings, True

    def _get_free(self):
        free = self.free(True)
        return free, []

    def _get_defdescr_events(self, event_data):
        return [item[0] for item in event_data.get(self.variable, ())]

    def _is_binding(self, variable, var_individuals, defdescr_events, event_data, presupp_event_data, presupp_individuals):
        # No binding is possible to variables having a role in the same eventuality (look for eventualities in DRSs other than self)
        variable_events = set((event for event, role, event_string in event_data.get(variable, ())))
        if not variable_events.isdisjoint(defdescr_events):
            return False
        # Don't allow binding if the potential antecedent participates in the same eventuality (in the relative clause) as self.variable, e.g.:
        # If John has a child, the child that likes him (him = the child in the antecedent of the impl. cond) is away.
        variable_presupp_events = set((event for event, role, event_string in presupp_event_data.get(variable, ())))
        defdescr_presupp_events = set((event for event, role, event_string in presupp_event_data.get(self.variable, ())))
        if not variable_presupp_events.isdisjoint(defdescr_presupp_events):
            return False

        # Don't allow binding x to y if there are conditions like POSS(x,y), POSS(y,x), REL(x,y), REL(y,x) and suchlike
        for event_tuple in presupp_event_data.get(variable, []):
            event = event_tuple[0]
            if event.__class__ == DrtIndividualVariableExpression and event.variable == self.variable:
                return False
        for event_tuple in presupp_event_data.get(self.variable, []):
            event = event_tuple[0]
            if event.__class__ == DrtIndividualVariableExpression and event.variable == variable:
                return False

        # Perform the semantic check
        return self.semantic_check(var_individuals, presupp_individuals)

    def semantic_check(self, individuals, presupp_individuals, strict=False):
        """ Users can plug in their more sophisticated semantic checks here.
        As for this project, we confine ourselves to ontologies provided by WordNet.
        See the other file for how this is supposed to work."""
        if strict:
            # ------------------------ Plug in ontologies here
            if isinstance(self.cond, DrtFeatureConstantExpression):
                for individual in individuals:
                    if isinstance(individual, DrtFeatureConstantExpression) and self.function_name == individual.function.variable.name:
                        return True
                return False
            else:
                # If no features are used, we cannot guarantee that the condition we got self.function_name from wasn't an adjective
                for individual in individuals:
                    for presupp_individual in presupp_individuals[self.variable]:
                        if presupp_individual.function.variable.name == individual.function.variable.name:
                            return True
                return False
        else:
            return True

    def _free_variable_check(self, drs, free, all_refs):
        if free:
            all_refs.extend(drs.refs)
            for variable in free:
                if not variable in all_refs:
                    return False
        return True

class DrtParser(drt.DrtParser):

    def get_all_symbols(self):
        return DrtTokens.SYMBOLS

    def isvariable(self, tok):
        return tok not in DrtTokens.TOKENS

    def handle(self, tok, context):
        """We add new types of DRS to represent presuppositions"""
        if tok.upper() in DrtTokens.PRESUPPOSITION_DRS:
            return self.handle_PresuppositionDRS(tok.upper(), context)
        else:
            return drt.DrtParser.handle(self, tok, context)


    def handle_PresuppositionDRS(self, tok, context):
        """Parse all the Presuppositon DRSs."""
        self.assertNextToken(DrtTokens.OPEN)
        drs = self.handle_DRS(tok, context)
        if tok == DrtTokens.PROPER_NAME_DRS:
            return ProperNameDRS(drs.refs, drs.conds)
        elif tok == DrtTokens.DEFINITE_DESCRIPTION_DRS:
            return DefiniteDescriptionDRS(drs.refs, drs.conds)
        elif tok == DrtTokens.PRONOUN_DRS:
            return PronounDRS(drs.refs, drs.conds)

    def handle_variable(self, tok, context):
        #It's either: 1) a predicate expression: sees(x,y)
        #             2) an application expression: P(x)
        #             3) a solo variable: john OR x
        accum = self.make_VariableExpression(tok)
        # handle the feature structure of the variable
        features = []
        try:
            if self.token(0) == DrtTokens.OPEN_BRACE:
                self.token() # swallow the OPEN_BRACE
                while self.token(0) != DrtTokens.CLOSE_BRACE:
                    features.append(DrtFeatureExpression(Variable(self.token())))
                    if self.token(0) == drt.DrtTokens.COMMA:
                        self.token() # swallow the comma
                self.token() # swallow the CLOSE_BRACE
        except LogicalExpressionException:
            #we've reached the end of input, this constant has no features
            pass
        if self.inRange(0) and self.token(0) == DrtTokens.OPEN:
            if features:
                accum = DrtFeatureConstantExpression(accum.variable, features)
            #The predicate has arguments
            if isinstance(accum, drt.DrtIndividualVariableExpression):
                raise LogicalExpressionException(self._currentIndex,
                                     '\'%s\' is an illegal predicate name.  '
                                     'Individual variables may not be used as '
                                     'predicates.' % tok)
            self.token() #swallow the Open Paren

            #curry the arguments
            accum = self.make_ApplicationExpression(accum,
                                                    self.parse_Expression('APP'))
            while self.inRange(0) and self.token(0) == DrtTokens.COMMA:
                self.token() #swallow the comma
                accum = self.make_ApplicationExpression(accum,
                                                        self.parse_Expression('APP'))
            self.assertNextToken(DrtTokens.CLOSE)
        elif features:
            accum = DrtFeatureConstantExpression(accum.variable, map(Variable, features))
        return accum

    def handle_DRS(self, tok, context):
        drs = drt.DrtParser.handle_DRS(self, tok, context)
        return DRS(drs.refs, drs.conds)

    def get_BooleanExpression_factory(self, tok):
        """This method serves as a hook for other logic parsers that
        have different boolean operators"""

        if tok == DrtTokens.DRS_CONC:
            return ConcatenationDRS
        elif tok in DrtTokens.OR:
            return DrtOrExpression
        elif tok in DrtTokens.IMP:
            return DrtImpExpression
        elif tok in DrtTokens.IFF:
            return DrtIffExpression
        else:
            return None

    def make_VariableExpression(self, name):
        return DrtVariableExpression(Variable(name))

    def make_ApplicationExpression(self, function, argument):
        return DrtApplicationExpression(function, argument)

    def make_ConstantExpression(self, name):
        return DrtConstantExpression(Variable(name))

    def make_NegatedExpression(self, expression):
        return DrtNegatedExpression(expression)

    def make_EqualityExpression(self, first, second):
        """This method serves as a hook for other logic parsers that
        have different equality expression classes"""
        return DrtEqualityExpression(first, second)

    def make_LambdaExpression(self, variables, term):
        return DrtLambdaExpression(variables, term)
