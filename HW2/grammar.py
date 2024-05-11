"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum
import math

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        
        # Define the set of nonterminals and terminals
        nonterminals = set(self.lhs_to_rules.keys())
        nonterminals.add(self.startsymbol)
        terminals = set()

        # Check if all symbols in the grammar are either nonterminals or terminals
        for lhs, rules in self.lhs_to_rules.items():
            for rule in rules:
                for symbol in rule[1]:
                    if symbol not in nonterminals:
                        terminals.add(symbol) 
        
        # Check if the sum of the probabilities for each lhs is 1
        for lhs, rules in self.lhs_to_rules.items():
            total_prob = fsum([rule[2] for rule in rules])
            if not math.isclose(total_prob, 1.0, rel_tol = 1e-9):
                return False
        
        return True

if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
        
    if grammar.verify_grammar():
        print("The grammar is a valid PCFG in CNF.")
    else:
        print("The grammar is not a valid PCFG in CNF.")