"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        n = len(tokens)

        # Initialise the parse table.
        table = [[set() for _ in range(n + 1)] for _ in range(n)]

        # Fill in the diagonal of the parse table.
        for i, token in enumerate(tokens):
            for rule in self.grammar.rhs_to_rules[(token,)]:
                table[i][i+1].add(rule[0])

        # Fill in the rest of the table.        
        for length in range(2, n+1):
            for i in range(n-length+1):
                j = i + length
                for k in range(i+1, j):
                    for B in table[i][k]:
                        for C in table[k][j]:
                            for rule in self.grammar.rhs_to_rules.get((B,C),[]):
                                table[i][j].add(rule[0])
            
        return self.grammar.startsymbol in table[0][n]
    
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        n = len(tokens)
        # Initialize the parse table and the probability table
        table = {(i, i + 1): {} for i in range(n)}
        probs = {(i, i + 1): {} for i in range(n)}

        # Fill the diagonal of the tables
        for i, token in enumerate(tokens):
            for rule in self.grammar.rhs_to_rules[(token,)]:
                table[i, i + 1][rule[0]] = token  # rule[0] is the lhs
                probs[i, i + 1][rule[0]] = math.log(rule[2])  # rule[2] is the probability

        # Fill the rest of the tables
        for length in range(2, n + 1):  # length of the substring
            for i in range(n - length + 1):  # start of the substring
                j = i + length
                table[i, j] = {}
                probs[i, j] = {}
                for k in range(i + 1, j):  # position to split the substring
                    for B in table[i, k]:  # non-terminals that produce the first part of the substring
                        for C in table[k, j]:  # non-terminals that produce the second part of the substring
                            for rule in self.grammar.rhs_to_rules.get((B, C), []):
                                A = rule[0]  # rule[0] is the lhs
                                prob = math.log(rule[2]) + probs[i, k][B] + probs[k, j][C]  # rule[2] is the probability
                                if A not in probs[i, j] or prob > probs[i, j][A]:
                                    table[i, j][A] = (B, i, k), (C, k, j)
                                    probs[i, j][A] = prob

        return table, probs


def get_tree(chart, i, j, nt):
    # Base case: the cell contains a terminal symbol
    if j == i + 1:
        return nt, chart[i, j][nt]

    # Recursive case: the cell contains a non-terminal symbol
    left, right = chart[i, j][nt]
    B, i1, k = left
    C, k1, j1 = right
    return nt, get_tree(chart, i1, k, B), get_tree(chart, k1, j1, C)
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        print(check_table_format(table))
        print(check_probs_format(probs))
        print(get_tree(table, 0, len(toks), grammar.startsymbol))
        
