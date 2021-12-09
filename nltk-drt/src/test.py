"""
Test suit for the temporaldrt module
"""
__author__ = "Alex Kislev, Emma Li, Peter Makarov"
__version__ = "1.0"
__date__ = "Tue, 24 Aug 2010"

from util import Tester
from wntemporaldrt import DrtParser

#background knowledge
BK = {
    'earlier' : r'all x y z.(earlier(x,y) & earlier(y,z) -> earlier(x,z)) & all x y.(earlier(x,y) -> -overlap(x,y))',

    'include' : r'all x y z.((include(x,y) & include(z,y)) -> (overlap(x,z)))',

    'die' : r'all x z y.((die(x) & AGENT(x,y) & die(z) & AGENT(z,y)) -> x = z)',

    'husband' : r'(([t,x,y],[POSS(y,x), husband(y)]) -> ([s],[married(s),THEME(s,x),overlap(t,s)]))',

    'married' : r'(([t,s],[married(s),THEME(s,x),overlap(t,s)]) -> ([x,y],[POSS(y,x), husband(y)]))',

    'own' : r'(([s,x,y],[own(s),AGENT(s,x),PATIENT(s,y)]) -> ([],[POSS(y,x)]))',

    'POSS' : r'(([t,y,x],[POSS(y,x)]) -> ([s],[own(s),AGENT(s,x),PATIENT(s,y),overlap(t,s)]))',

   'dead' : r'(([t,s,e,x],[include(s,t),abut(e,s),die(e),AGENT(e,x)]) -> ([],[dead(s),THEME(s,x),overlap(t,s)]))'
    }


def test_anaphora(tester):
    cases = [
    (1, "He wants a car. Jones needs it.", None),

    (2, "He invited Jones.", None),

    (3, "Jones loves Charlotte and Bill loves her. He hates himself.", ["([n,s,s012,s018,x,z6,z11],[Jones{sg,m}(x), Charlotte{sg,f}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), Bill{sg,m}(z11), love(s012), AGENT(s012,z11), PATIENT(s012,z6), overlap(n,s012), overlap(s,s012), hate(s018), AGENT(s018,z11), PATIENT(s018,z11), overlap(n,s018), overlap(s012,s018)])", "([n,s,s012,s018,x,z6,z11],[Jones{sg,m}(x), Charlotte{sg,f}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), Bill{sg,m}(z11), love(s012), AGENT(s012,z11), PATIENT(s012,z6), overlap(n,s012), overlap(s,s012), hate(s018), AGENT(s018,x), PATIENT(s018,x), overlap(n,s018), overlap(s012,s018)])"]),

    (4, "Jones loves Charlotte and Bill loves her. He hates him.", ["([n,s,s012,s018,x,z6,z11],[Jones{sg,m}(x), Charlotte{sg,f}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), Bill{sg,m}(z11), love(s012), AGENT(s012,z11), PATIENT(s012,z6), overlap(n,s012), overlap(s,s012), hate(s018), AGENT(s018,z11), PATIENT(s018,x), overlap(n,s018), overlap(s012,s018)])", "([n,s,s012,s018,x,z6,z11],[Jones{sg,m}(x), Charlotte{sg,f}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), Bill{sg,m}(z11), love(s012), AGENT(s012,z11), PATIENT(s012,z6), overlap(n,s012), overlap(s,s012), hate(s018), AGENT(s018,x), PATIENT(s018,z11), overlap(n,s018), overlap(s012,s018)])"]),

    (5, "Jones loves Charlotte and Bill loves her. Himself hates him.", None),

    (6, "Jones likes the picture of himself.", "([n,s,x,z245],[Jones{sg,m}(x), REL(z245,x), picture{sg,n}(z245), like(s), AGENT(s,x), PATIENT(s,z245), overlap(n,s)])"),

    (7, "Jones likes the picture of him.", None),

    (8, "Bill likes Jones's picture of himself.", "([n,s,x,z15,y],[Bill{sg,m}(x), POSS(y,z15), REL(y,z15), picture{sg,n}(y), Jones{sg,m}(z15), like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)])"),

    (9, "Bill likes Jones's picture of him.", "([n,s,x,z15,y],[Bill{sg,m}(x), POSS(y,z15), REL(y,x), picture{sg,n}(y), Jones{sg,m}(z15), like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)])"),

    (10, "Jones showed Bill his room. He liked it.", ["([n,t,e,t014,s,x,z7,z6],[earlier(t,n), Jones{sg,m}(x), Bill{sg,m}(z7), POSS(z6,z7), room{sg,n}(z6), show(e), AGENT(e,x), PATIENT(e,z6), RECIP(e,z7), include(t,e), earlier(t014,n), like(s), AGENT(s,z7), PATIENT(s,z6), overlap(t014,s), include(s,e)])", "([n,t,e,t014,s,x,z7,z6],[earlier(t,n), Jones{sg,m}(x), Bill{sg,m}(z7), POSS(z6,z7), room{sg,n}(z6), show(e), AGENT(e,x), PATIENT(e,z6), RECIP(e,z7), include(t,e), earlier(t014,n), like(s), AGENT(s,x), PATIENT(s,z6), overlap(t014,s), include(s,e)])", "([n,t,e,t014,s,x,z7,z6],[earlier(t,n), Jones{sg,m}(x), Bill{sg,m}(z7), POSS(z6,x), room{sg,n}(z6), show(e), AGENT(e,x), PATIENT(e,z6), RECIP(e,z7), include(t,e), earlier(t014,n), like(s), AGENT(s,z7), PATIENT(s,z6), overlap(t014,s), include(s,e)])", "([n,t,e,t014,s,x,z7,z6],[earlier(t,n), Jones{sg,m}(x), Bill{sg,m}(z7), POSS(z6,x), room{sg,n}(z6), show(e), AGENT(e,x), PATIENT(e,z6), RECIP(e,z7), include(t,e), earlier(t014,n), like(s), AGENT(s,x), PATIENT(s,z6), overlap(t014,s), include(s,e)])"]),

    (11, "If Jones is away, he has left London.", "([n,x,z8],[(([s],[away(s), THEME(s,x), overlap(n,s)]) -> ([s018,e],[include(s018,n), overlap(s,s018), leave(e), AGENT(e,x), PATIENT(e,z8), abut(e,s018)])), London{sg,n}(z8), Jones{sg,m}(x)])"),

    (12, "No one dated Charlotte and she was upset.", "([n,t,t011,s,z6],[earlier(t,n), -([x,e],[human{sg,m}(x), date(e), AGENT(e,x), PATIENT(e,z6), include(n,e), include(s,e)]), Charlotte{sg,f}(z6), earlier(t011,n), upset(s), THEME(s,z6), overlap(t011,s)])"),

    (13, "If Jones is smart, everyone underestimates him.", "([n,z10],[(([s],[smart(s), THEME(s,z10), overlap(n,s)]) -> ([],[(([x],[human{sg,m}(x)]) -> ([s015],[underestimate(s015), AGENT(s015,x), PATIENT(s015,z10), overlap(n,s015), overlap(s,s015)]))])), Jones{sg,m}(z10)])"),

    (14, "Jones owns a porsche. He likes it.", "([n,z146,s,s0152,x],[Jones{sg,m}(x), porsche{sg,n}(z146), own(s), AGENT(s,x), PATIENT(s,z146), overlap(n,s), like(s0152), AGENT(s0152,x), PATIENT(s0152,z146), overlap(n,s0152), overlap(s,s0152)])"),

    (15, "Jones does not own a porsche. He likes it.", None),

    (16, "Every farmer who owns a donkey likes it.", "([n],[(([x,z167,s],[donkey{sg,n}(z167), own(s), AGENT(s,x), PATIENT(s,z167), overlap(n,s), farmer{sg,m}(x)]) -> ([s0181],[like(s0181), AGENT(s0181,x), PATIENT(s0181,z167), overlap(n,s0181), overlap(s,s0181)]))])"),

    (17, "Every farmer owns a donkey. He likes it.", None),

    (18, "Jones owns a car or he commutes.", "DRS([n,x],[(([z135,s],[car{sg,n}(z135), own(s), AGENT(s,x), PATIENT(s,z135), overlap(n,s)]) | ([e],[commute(e), AGENT(e,x), include(n,e)])), Jones{sg,m}(x)])"),

    (19, "Jones owns a porsche or Brown owns it", None),

    (20, "Jones owns it or Brown owns a porsche", None),

    (22, "Jones loves the baroness and Bill loves her.", "DRS([n,s,s0175,x,z169,z174],[Jones{sg,m}(x), baroness{sg,f}(z169), love(s), AGENT(s,x), PATIENT(s,z169), overlap(n,s), Bill{sg,m}(z174), love(s0175), AGENT(s0175,z174), PATIENT(s0175,z169), overlap(n,s0175), overlap(s,s0175)])"),

    (23, "Jones loves her and Bill loves the baroness.", None)
    ]
    tester.test(cases)


def test_presupposition(tester):

    cases = [
    #definite description
    (1, "Mary likes the president.", "([n,s,x,z6],[Mary{sg,f}(x), president{sg,m}(z6), like(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)])"),

    (2, "Mary does not like the president.", "([n,x,z6],[Mary{sg,f}(x), -([s],[like(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)]), president{sg,m}(z6)])"),

    (3, "If Mary likes the president, she will vote him.", "([n,x,z6],[(([s],[like(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)]) -> ([t012,e],[earlier(n,t012), vote(e), AGENT(e,x), PATIENT(e,z6), include(t012,e), include(s,e)])), president{sg,m}(z6), Mary{sg,f}(x)])"),

    (4, "Mary likes the president or she will not vote him.", "([n,x,z6],[(([s],[like(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)]) | ([t013],[earlier(n,t013), -([e],[vote(e), AGENT(e,x), PATIENT(e,z6), include(t013,e)])])), president{sg,m}(z6), Mary{sg,f}(x)])"),

    (5, "If Mary does not like the president, she will not vote him.", "([n,x,z6],[(([],[-([s],[like(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)])]) -> ([t014],[earlier(n,t014), -([e],[vote(e), AGENT(e,x), PATIENT(e,z6), include(t014,e)])])), president{sg,m}(z6), Mary{sg,f}(x)])"),

    (6, "France has elected a new president. Mary likes the president.", "([n,s,z6,e,s011,x,z10],[include(s,n), France{sg,n}(x), new(z6), president{sg,m}(z6), elect(e), AGENT(e,x), PATIENT(e,z6), abut(e,s), Mary{sg,f}(z10), like(s011), AGENT(s011,z10), PATIENT(s011,z6), overlap(n,s011), include(s011,e)])"),

    (7, "France has elected a new president. Mary does not like the president.", "([n,s,z6,e,x,z11],[include(s,n), France{sg,n}(x), new(z6), president{sg,m}(z6), elect(e), AGENT(e,x), PATIENT(e,z6), abut(e,s), Mary{sg,f}(z11), -([s012],[like(s012), AGENT(s012,z11), PATIENT(s012,z6), overlap(n,s012), include(s012,e)])])"),

    (8, "France has elected a new president. If Mary likes the president, she has voted him.", "([n,s,z6,e,x,z23],[include(s,n), France{sg,n}(x), new(z6), president{sg,m}(z6), elect(e), AGENT(e,x), PATIENT(e,z6), abut(e,s), (([s024],[like(s024), AGENT(s024,z23), PATIENT(s024,z6), overlap(n,s024), include(s024,e)]) -> ([s021,e025],[include(s021,n), include(s021,e), vote(e025), AGENT(e025,z23), PATIENT(e025,z6), abut(e025,s021)])), Mary{sg,f}(z23)])"),

    (9, "France has elected a new president. Mary likes the president or she has not voted him.", "([n,s,z6,e,x,z24],[include(s,n), France{sg,n}(x), new(z6), president{sg,m}(z6), elect(e), AGENT(e,x), PATIENT(e,z6), abut(e,s), (([s025],[like(s025), AGENT(s025,z24), PATIENT(s025,z6), overlap(n,s025), include(s025,e)]) | ([s022],[include(s022,n), include(s022,e), -([e026],[vote(e026), AGENT(e026,z24), PATIENT(e026,z6), abut(e026,s022)])])), Mary{sg,f}(z24)])"),

    (10, "France has elected a new president. If Mary does not like the president, she has not voted him", "([n,s,z6,e,x,z25],[include(s,n), France{sg,n}(x), new(z6), president{sg,m}(z6), elect(e), AGENT(e,x), PATIENT(e,z6), abut(e,s), (([],[-([s026],[like(s026), AGENT(s026,z25), PATIENT(s026,z6), overlap(n,s026), include(s026,e)])]) -> ([s023],[include(s023,n), include(s023,e), -([e027],[vote(e027), AGENT(e027,z25), PATIENT(e027,z6), abut(e027,s023)])])), Mary{sg,f}(z25)])"),

    #complex determiner NPs
    (11, "Mary likes John's car.", "([n,s,x,z10,y],[Mary{sg,f}(x), POSS(y,z10), car{sg,n}(y), John{sg,m}(z10), like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)])"),

    (12, "Mary does not like John's car.", "([n,x,z11,y],[Mary{sg,f}(x), -([s],[like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)]), POSS(y,z11), car{sg,n}(y), John{sg,m}(z11)])"),

    (13, "If Mary likes John's car, she is stupid.", "([n,x,z307,y],[(([s],[like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)]) -> ([s0321],[stupid(s0321), THEME(s0321,x), overlap(n,s0321), overlap(s,s0321)])), POSS(y,z307), car{sg,n}(y), John{sg,m}(z307), Mary{sg,f}(x)])"),

    (14, "Mary likes John's car or she hates it.", "([n,x,z307,y],[(([s],[like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)]) | ([s0327],[hate(s0327), AGENT(s0327,x), PATIENT(s0327,y), overlap(n,s0327)])), POSS(y,z307), car{sg,n}(y), John{sg,m}(z307), Mary{sg,f}(x)])"),

    (15, "Mary likes John's car or she hates his car.", "([n,x,z10,y],[(([s],[like(s), AGENT(s,x), PATIENT(s,y), overlap(n,s)]) | ([s025],[hate(s025), AGENT(s025,x), PATIENT(s025,y), overlap(n,s025)])), POSS(y,z10), car{sg,n}(y), John{sg,m}(z10), Mary{sg,f}(x)])"),

    #possessive pronoun NPs
    (16, "Mary loves John and she likes his car.", "([n,s,s012,x,z6,z9],[Mary{sg,f}(x), John{sg,m}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), POSS(z9,z6), car{sg,n}(z9), like(s012), AGENT(s012,x), PATIENT(s012,z9), overlap(n,s012), overlap(s,s012)])"),

    (17, "Mary loves John but she does not like his car.", "([n,s,x,z6,z9],[Mary{sg,f}(x), John{sg,m}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), -([s013],[like(s013), AGENT(s013,x), PATIENT(s013,z9), overlap(n,s013), overlap(s,s013)]), POSS(z9,z6), car{sg,n}(z9)])"),

    (18, "Mary loves John. If Mary likes his car, she is stupid.", "([n,s,x,z551,z554],[Mary{sg,f}(x), John{sg,m}(z551), love(s), AGENT(s,x), PATIENT(s,z551), overlap(n,s), (([s0570],[like(s0570), AGENT(s0570,x), PATIENT(s0570,z554), overlap(n,s0570), overlap(s,s0570)]) -> ([s0567],[stupid(s0567), THEME(s0567,x), overlap(n,s0567), overlap(s0570,s0567)])), POSS(z554,z551), car{sg,n}(z554)])"),

    (19, "Mary loves John. She likes his car or hates it.", "([n,s,x,z6,z26],[Mary{sg,f}(x), John{sg,m}(z6), love(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s), (([s034],[like(s034), AGENT(s034,x), PATIENT(s034,z26), overlap(n,s034), overlap(s,s034)]) | ([s025],[hate(s025), AGENT(s025,x), PATIENT(s025,z26), overlap(n,s025), overlap(s,s025)])), POSS(z26,z6), car{sg,n}(z26)])"),

    #free variable check
    (20, "Angus is away. Every farmer likes his donkey.", ["([n,s,x],[Angus{sg,m}(x), away(s), THEME(s,x), overlap(n,s), (([z10,z8],[farmer{sg,m}(z10), POSS(z8,z10), donkey{sg,n}(z8)]) -> ([s011],[like(s011), AGENT(s011,z10), PATIENT(s011,z8), overlap(n,s011), overlap(s,s011)]))])", "([n,s,x,z8],[Angus{sg,m}(x), away(s), THEME(s,x), overlap(n,s), (([z10],[farmer{sg,m}(z10)]) -> ([s011],[like(s011), AGENT(s011,z10), PATIENT(s011,z8), overlap(n,s011), overlap(s,s011)])), POSS(z8,x), donkey{sg,n}(z8)])"])
    ]


    admissibility_cases = [
    #admissibility check
    (21, None, "If Mary owns a car, Mary's car is black.", 3),

    (22, None, "If Mary owns a car, her car is black.", 3),

    (23, None, "Mary does not own a car or Mary's car is black.", 3),

    (24, None, "Mary does not own a car or her car is black.", 3),

    (25, None, "If Mary is out, Mary's husband is away.", None),

    (26, None, "If Mary is out, her husband is away.", None),

    (27, None, "If Mary is married, Mary's husband is away.", 3),

    (28, None, "If Mary is married, her husband is away.", 3),
    ]

    cases_wn = [
    (24, "Angus owns a garden but wants a hammer. He needs the tool.", "([n,z12,s,z9,s010,s019,x],[Angus{sg,m}(x), garden{sg,n}(z12), own(s), AGENT(s,x), PATIENT(s,z12), overlap(n,s), hammer{sg,n}(z9), want(s010), AGENT(s010,x), PATIENT(s010,z9), overlap(n,s010), overlap(s,s010), tool{sg,n}(z9), need(s019), AGENT(s019,x), PATIENT(s019,z9), overlap(n,s019), overlap(s010,s019)])"),

    (25, "The garden is abloom. The car is broken.", "([n,s,s010,x,z9],[garden{sg,n}(x), abloom(s), THEME(s,x), overlap(n,s), car{sg,n}(z9), broken(s010), THEME(s010,z9), overlap(n,s010), overlap(s,s010)])"),

    (26, "A farmer owned a hammer. Fido bit him. The animal was stupid.", "([n,t,x,z6,s,t012,e,t018,s017,z11],[earlier(t,n), farmer{sg,m}(x), hammer{sg,n}(z6), own(s), AGENT(s,x), PATIENT(s,z6), overlap(t,s), earlier(t012,n), Fido{sg,n}(z11), bite(e), AGENT(e,z11), PATIENT(e,x), include(t012,e), include(s,e), earlier(t018,n), animal{sg,n}(z11), stupid(s017), THEME(s017,z11), overlap(t018,s017), include(s017,e)])"),

    (27, "A dog bit a cat. The feline was upset.", "([n,t,x,z6,e,t011,s],[earlier(t,n), dog{sg,n}(x), cat{sg,n}(z6), bite(e), AGENT(e,x), PATIENT(e,z6), include(t,e), earlier(t011,n), feline{sg,n}(z6), upset(s), THEME(s,z6), overlap(t011,s), include(s,e)])"),
     ]

    tester.test(cases)
    tester.inference_test(admissibility_cases, BK)
    tester.test(cases_wn)

def test_tenses(tester):
    cases = [
    #simple tenses with / without negation, quantified NPs
    (1, "Angus owns a car", "([n,z6,s,x],[Angus{sg,m}(x), car{sg,n}(z6), own(s), AGENT(s,x), PATIENT(s,z6), overlap(n,s)])"),

    (2, "Angus does not own a car", "([n,x],[Angus{sg,m}(x), -([z9,s],[car{sg,n}(z9), own(s), AGENT(s,x), PATIENT(s,z9), overlap(n,s)])])"),

    (3, "Angus owned a car", "([n,t,z13,s,x],[earlier(t,n), Angus{sg,m}(x), car{sg,n}(z13), own(s), AGENT(s,x), PATIENT(s,z13), overlap(t,s)])"),

    (4, "Angus did not own a car", "([n,t,x],[earlier(t,n), Angus{sg,m}(x), -([z16,s],[car{sg,n}(z16), own(s), AGENT(s,x), PATIENT(s,z16), overlap(t,s)])])"),

    (5, "Angus will own a car", "([n,t,z20,s,x],[earlier(n,t), Angus{sg,m}(x), car{sg,n}(z20), own(s), AGENT(s,x), PATIENT(s,z20), overlap(t,s)])"),

    (6, "Angus will not own a car", "([n,t,x],[earlier(n,t), Angus{sg,m}(x), -([z23,s],[car{sg,n}(z23), own(s), AGENT(s,x), PATIENT(s,z23), overlap(t,s)])])"),

    (7, "A dog bit Angus", "([n,t,x,e,z27],[earlier(t,n), dog{sg,n}(x), Angus{sg,m}(z27), bite(e), AGENT(e,x), PATIENT(e,z27), include(t,e)])"),

    (8, "Everyone owned a car", "([n,t],[earlier(t,n), (([x],[human{sg,m}(x)]) -> ([z33,s],[car{sg,n}(z33), own(s), AGENT(s,x), PATIENT(s,z33), overlap(t,s)]))])"),

    (9, "Everyone owned a dog but wanted a car", "([n,t,t042],[earlier(t,n), earlier(t042,n), (([x],[human{sg,m}(x)]) -> ([z39,s,z36,s037],[dog{sg,n}(z39), own(s), AGENT(s,x), PATIENT(s,z39), overlap(t042,s), car{sg,n}(z36), want(s037), AGENT(s037,x), PATIENT(s037,z36), overlap(t042,s037), overlap(s,s037)]))])"),

    (10, "Angus will buy every car.", "([n,t,z36],[earlier(n,t), Angus{sg,m}(z36), (([x],[car{sg,n}(x)]) -> ([e],[buy(e), AGENT(e,z36), PATIENT(e,x), include(t,e)]))])"),

    #perfect tenses
    (11, "Angus has written a letter", "([n,s,z39,e,x],[include(s,n), Angus{sg,m}(x), letter{sg,n}(z39), write(e), AGENT(e,x), PATIENT(e,z39), abut(e,s)])"),

    (12, "Angus has not written a letter", "([n,s,x],[include(s,n), Angus{sg,m}(x), -([z41,e],[letter{sg,n}(z41), write(e), AGENT(e,x), PATIENT(e,z41), abut(e,s)])])"),

    (13, "No one has written a letter", "([n,s],[include(s,n), -([x,z44,e],[human{sg,m}(x), letter{sg,n}(z44), write(e), AGENT(e,x), PATIENT(e,z44), abut(e,s)])])"),

    (14, "Angus had died", "([n,t,s,e,x],[overlap(s,t), earlier(t,n), Angus{sg,m}(x), die(e), AGENT(e,x), abut(e,s)])"),

    (15, "Angus had not died", "([n,t,s,x],[overlap(s,t), earlier(t,n), Angus{sg,m}(x), -([e],[die(e), AGENT(e,x), abut(e,s)])])"),

    #Reference points
    (16, "Mary kissed John. He smiled", "([n,t,e,t055,e053,x,z48],[earlier(t,n), Mary{sg,f}(x), John{sg,m}(z48), kiss(e), AGENT(e,x), PATIENT(e,z48), include(t,e), earlier(t055,n), smile(e053), AGENT(e053,z48), include(t055,e053), earlier(e,e053)])"),

    (17, "Mary will kiss John and he will smile", "([n,t,e,t063,e062,x,z57],[earlier(n,t), Mary{sg,f}(x), John{sg,m}(z57), kiss(e), AGENT(e,x), PATIENT(e,z57), include(t,e), earlier(n,t063), smile(e062), AGENT(e062,z57), include(t063,e062), earlier(e,e062)])"),

    (18, "John bought a fancy car. He was rich.", "([n,t,z74,e,t079,s,x],[earlier(t,n), John{sg,m}(x), fancy(z74), car{sg,n}(z74), buy(e), AGENT(e,x), PATIENT(e,z74), include(t,e), earlier(t079,n), rich(s), THEME(s,x), overlap(t079,s), include(s,e)])"),

    (19, "John was away. His car was broken", "([n,t,s,t072,s070,x,y],[earlier(t,n), John{sg,m}(x), away(s), THEME(s,x), overlap(t,s), earlier(t072,n), POSS(y,x), car{sg,n}(y), broken(s070), THEME(s070,y), overlap(t072,s070), overlap(s,s070)])"),

    (20, "If John owns a car he is rich", "([n,x],[(([z74,s],[car{sg,n}(z74), own(s), AGENT(s,x), PATIENT(s,z74), overlap(n,s)]) -> ([s079],[rich(s079), THEME(s079,x), overlap(n,s079), overlap(s,s079)])), John{sg,m}(x)])"),

    (21, "John owns a broken car or he is rich", "([n,x],[(([z82,s],[broken(z82), car{sg,n}(z82), own(s), AGENT(s,x), PATIENT(s,z82), overlap(n,s)]) | ([s087],[rich(s087), THEME(s087,x), overlap(n,s087)])), John{sg,m}(x)])"),
    ]

    case_inf = [(22, "Mia died", "Mia will die", 1),

    (23, "Jones has died", "Jones is dead", 2)]


    tester.test(cases)
    tester.inference_test(case_inf, BK, verbose=False)

def test_inference(tester):

    cases_inf = [
    # No background knowledge attached
    (1, "Mia is away", "Mia is not away", 1),

    (2, "Mia is away", "Mia is away", 2),

    (3, "Mia is away", "If Mia is away Angus is out", 3),

    (4, "Mia is away", "If Mia is not away Angus is out", 2),

    (5, "Mia is away", "If Angus is out Mia is away", 2),

    (6, "Mia is away", "If Angus is out Mia is not away", 3),

    (7, "Mia is away", "Angus is out or Mia is away", 2),

    (8, "Mia is away", "Angus is out or Mia is not away", 3),
    ]

    tester.inference_test(cases_inf, BK, verbose=False)

HASH_LINE = "#"*80

def print_header(header):
    len_hash = (74 - len(header))/2
    print ("\n\t# {0} #\n\t### {1} {2} {1} ###\n\t# {0} #\n\n".format(HASH_LINE, "#"*len_hash, header))

TESTS = [("Anaphora Component", test_anaphora),
         ("Presupposition Component", test_presupposition),
         ("Inference Component ", test_inference),
         ("Tempotal Component", test_tenses)
         ]
def main():
    tester = Tester('file:../data/grammar.fcfg', DrtParser)
    for header, test in TESTS:
        print_header("Testing %s" % header)
        test(tester)
    print ("\n\t{0} THE  END {0}".format("#"*37))

if __name__ == '__main__':
    main()
