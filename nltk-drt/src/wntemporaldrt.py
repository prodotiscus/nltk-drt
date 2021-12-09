"""
Extension of temporaldrt using WordNet ontology
"""

__author__ = " Emma Li, Peter Makarov, Alex Kislev"
__version__ = "1.0"
__date__ = "Tue, 24 Aug 2010"

import nltk
from nltk.corpus.reader.wordnet import WordNetCorpusReader
import temporaldrt as drt
from temporaldrt import DrtTokens, DrtFeatureConstantExpression

def singleton(cls):
    instance_container = []
    def getinstance():
        if not len(instance_container):
            instance_container.append(cls())
        return instance_container[0]
    return getinstance

@singleton
class WordNetLookup(object):
    def __init__(self, path='corpora/wordnet'):
        self.path = path
        self.WN = None

    def wn(self):
        if not self.WN:
            self.WN = WordNetCorpusReader(nltk.data.find(self.path))

    def is_superclass_of(self, first, second):
        "Is the second noun the superclass of the first one?"
        self.wn()
        try:
            num_of_senses_first = self._num_of_senses(first)
            num_of_senses_second = self._num_of_senses(second)
        except: return False
        for n in range(num_of_senses_second):
            synset_second = self._noun_synset(second, ind=n)
            for i in range(num_of_senses_first):
                if synset_second in self._noun_synset(first, i).common_hypernyms(synset_second):
                    return True
        return False

    def is_adjective(self, word):
        try:
            self._num_of_senses(word, 'a')
            return True
        except: return False

    def _noun_synset(self, noun, ind):
        self.wn()
        return self.WN.synset("%s.n.%s" % (noun, ind))

    def _num_of_senses (self, word, pos='n'):
        self.wn()
        return len(self.WN._lemma_pos_offset_map[word][pos])

    def is_person(self, word):
        return self.is_superclass_of(word, 'person')

    def is_animal(self, word):
        return self.is_superclass_of(word, 'animal')


class DefiniteDescriptionDRS(drt.DefiniteDescriptionDRS):
    def __init__(self, refs, conds):
        self.wn = WordNetLookup()
        super(drt.DefiniteDescriptionDRS, self).__init__(refs, conds)

    def _strict_check (self, presupp_noun, other_cond):
        other_noun = other_cond.function.variable.name
        return (
                presupp_noun == other_noun or
                self.wn.is_superclass_of(other_noun, presupp_noun) or
                (other_cond.is_propername() and (self.wn.is_person(presupp_noun) or self.wn.is_animal(presupp_noun)))
                )

    def _non_strict_check(self, presupp_noun, other_cond):
        strict_check = self._strict_check(presupp_noun, other_cond)
        if strict_check: return True
        # If the strict check fails, check if both are people
        other_noun = other_cond.function.variable.name
        return (
                (self.wn.is_person(presupp_noun) and self.wn.is_person(other_noun))
                or self.wn.is_superclass_of(presupp_noun, other_noun)) # cat, kitty

    def semantic_check(self, individuals, presupp_individuals, strict=False):
        check = {True : self._strict_check,
                 False: self._non_strict_check}[strict]
        # Strict check - passes if features match and 1) string matching 2) hyponym-hypernym relation, and
        # 3) self.funcname is a person or animal and the antecedent is a proper name
        # Non-strict check: both are people and features match
        if isinstance(self.cond, DrtFeatureConstantExpression):
            for individual in individuals:
                if isinstance(individual, DrtFeatureConstantExpression) and check(self.function_name, individual):
                    return True
            return False
        else:
            # If no features are used, we cannot guarantee that the condition we got self.function_name from wasn't an adjective.
            # Likewise, individuals contains not only nouns but also adjectives, and we don't know which are which
            found_noun = False  # We should find at least one noun
            for presupp_individual in presupp_individuals[self.variable]:
                presupp_noun = presupp_individual.function.variable.name
                if not self.wn.is_adjective(presupp_noun):
                    found_noun = True
                    break
            # If we found no noun (that is not also an adjective), ignore the 'is adjective' check for presupposition individuals
            # (in that case, we had probably better ignore this check for 'individuals', too)
            for individual in individuals:
                other_noun = individual.function.variable.name
                if found_noun and self.wn.is_adjective(other_noun): continue
                for presupp_individual in presupp_individuals[self.variable]:
                    presupp_noun = presupp_individual.function.variable.name
                    if found_noun and self.wn.is_adjective(presupp_noun): continue
                    if check (presupp_noun, individual):
                        return True
            return False

class DrtParser(drt.DrtParser):

    def handle_PresuppositionDRS(self, tok, context):
        if tok == DrtTokens.DEFINITE_DESCRIPTION_DRS:
            self.assertNextToken(DrtTokens.OPEN)
            drs = self.handle_DRS(tok, context)
            return DefiniteDescriptionDRS(drs.refs, drs.conds)
        else:
            return drt.DrtParser.handle_PresuppositionDRS(self, tok, context)
