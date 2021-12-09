"""
NLTK DRT module extended with presuppositions
"""

__author__ = "Alex Kislev, Emma Li, Peter Makarov"
__version__ = "1.0"
__date__ = "Tue, 24 Aug 2010"

import random
from test import BK
from util import Tester, UngrammaticalException
from temporaldrt import DrtParser
from inference import AdmissibilityError, ConsistencyError, InformativityError

class Curt(object):
    INADMISSIBLE = ["That's Greek to me", "Do you get my drift?", "Now, hold your horses!", "Well, I dunno...", "Neither rhyme nor reason."]
    INCONSISTENT = ["I don't believe that!", "Nice try!", "That's a switch!", "Don't try to butter me up!", "I smell a rat.", "Tell it to the marines!"]
    UNINFORMATIVE = ["I know that already!", "Whatever!", "You ain't seen nothing yet!", "Hey, that's an oldie.", "Betcha don't know.", "It's all one to me "]
    OK = ["Nice to know", "OK", "Go on!", "Go ahead!", "No problem!", "Do your thing!", "No kiddin'?", "Really?", "Is that so?", "That's more like it", "What are you driving at?", "C'mon, shake a leg!", "Well, that's the way the cookie crumbles.", "Spill the beans!", "While you live, tell truth and shame the Devil!"]
    GOODBYE = ["See ya!", "Nice talking to you!", "Bye!", "Take care!", "Cheers!", "So long and thanks for all the fish!"]
    def __init__(self, grammar_file='file:../data/grammar.fcfg', logic_parser=DrtParser, background=None):
        self.tester = Tester(grammar_file, logic_parser)
        self.background = background
        self.discourse = None

    def randomize(self, option_list):
        return option_list[random.randint(0, len(option_list) - 1)]

    def inadmissible(self):
        return self.randomize(Curt.INADMISSIBLE)

    def inconsistent(self):
        return self.randomize(Curt.INCONSISTENT)

    def uninformative(self):
        return self.randomize(Curt.UNINFORMATIVE)

    def ok(self):
        return self.randomize(Curt.OK)

    def goodbye(self):
        return self.randomize(Curt.GOODBYE)

    def respond(self, s, explicit):
        if isinstance(s, AdmissibilityError):
            return "%s%s" % (self.inadmissible(), "(inadmissible)" if explicit else "")
        elif isinstance(s, ConsistencyError):
            return "%s%s" % (self.inconsistent(), "(inconsistent)" if explicit else "")
        elif isinstance(s, InformativityError):
            return "%s%s" % (self.uninformative(), "(uninformative)" if explicit else "")

    def process(self, utterance, explicit=False, verbose=False):
        if self.discourse is None:
            self.discourse = self.tester.parse(utterance, utter=True)
        else:
            expression = self.tester.parse_new(self.discourse, utterance)
            inferences, errors = self.tester.interpret_new(self.discourse, expression, background=self.background)
            if not inferences:
                out = []
                for reading, error in errors:
                    if verbose:
                        print("Error: %s" % error)
                    out.append(self.respond(error, explicit))
                return ", ".join(out)
            else:
                if verbose:
                    for inference in inferences:
                        print ("reading: %s" % inference)
                self.discourse = (self.discourse + expression).simplify()

        return self.ok()

    def __str__(self):
        return str(self.discourse)

def main():
    show_model = False
    explicit = False
    verbose = False
    curt = Curt(background=BK)
    print ("Welcome to Curt, type 'h' for help")
    while True:
        s = raw_input("What say you? ")
        if s == "bye":
            print (curt.goodbye())
            return
        elif s == "m":
            show_model = False if show_model else True
            print ("display models: %s" % ("on" if  show_model else "off"))
        elif s == "e":
            explicit = False if explicit else True
            print ("explicit mode: %s" % ("on" if  explicit else "off"))
        elif s == "v":
            verbose = False if verbose else True
            print ("verbose mode: %s" % ("on" if  verbose else "off"))
        elif s == "h":
            print ("e\t toggle explicit mode")
            print ("m\t toggle model printing")
            print ("v\t toggle verbose mode")
            print ("h\t show this message")
            print ("bye\t exit")
        else:
            print ("You say:\t%s" % s)
            try:
                print ("Curt says:\t%s" % curt.process(s, explicit, verbose))
            except ValueError as e:
                print ("Error: %s" % e)
            except UngrammaticalException:
                print ("Curt says:\tWhat was that again?")
            if show_model:
                print ("Model: %s" % str(curt))

def test_curt():
    input = ["If Mia is away Angus is out", "Mia is away", "Angus is out", "Mia is not away", "Mia is away"]
    curt = Curt(background=BK)
    for i in input:
        print (i)
        print (curt.process(i, True))

if __name__ == "__main__":
    main()
