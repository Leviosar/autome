from fileinput import filename
import json
from math import prod
from typing import List
from tabulate import tabulate
import click


class Symbol:
    def __init__(self, name: str, terminal: bool):
        self.name = name
        self.terminal = terminal
        
class CFG:
    def __init__(self, nonterminals: List[str], terminals=List[str], initial=str, productions=None, name=''):
        self.nonterminals = nonterminals if nonterminals else list()
        self.terminals = terminals if terminals else list()
        self.initial = initial if initial else list()
        self.productions = productions if productions else dict()
        self.name = name

        self.first = dict()
        self.follow = dict()
    
    def __repr__(self) -> str:
        content = []
        for head, body in self.productions.items():
            prods = [''.join(prod) for prod in body]
            joined = '|'.join(prods)
            content.append(f"{head} → {joined}\n")
        
        return ''.join(content)
        return tabulate(content, headers=["Grammar"], tablefmt="fancy_grid")
    
    @classmethod
    def parse_(cls, input: click.Path):
        with open(input, 'r') as file:
            content = json.load(file)
            
        grammar = content["grammar"]
        
        nonterminals = grammar["nonterminals"]
        
        initial = grammar["initial"]
        if (initial not in nonterminals):
            raise Exception("The initial symbol must be a part of the nonterminals set")
        
        terminals = grammar["terminals"]
        
        productions = dict()
        
        for production in grammar["productions"]:
            prods = [prod.split(' ') for prod in production["body"].split("|") if prod]
            prods = [list(filter(lambda val: val != '', prod)) for prod in prods]
            productions[production["head"]] = prods
            
        return CFG(nonterminals, terminals, initial, productions)
    
    def calculateFirst(self):
        """Calcula o conjunto first da gramática"""
        self.first.clear()

        # First(a) = {a}
        for terminal in self.terminals:
            self.first[terminal] = { terminal }

        # Para cada não terminal X
        for nonterminal in self.nonterminals:
            self.first[nonterminal] = set()
            
            # Se X ::= aY, a pertence à First(X) = First(X) ∪ {a}
            for production in self.productions[nonterminal]:
                if production[0] in self.terminals:
                    self.first[nonterminal].add(production[0])
        

        # 2. Se X ::= Y1 Y2...Yk, então FIRST(Y1) pertence à FIRST(X)
        stop = False
        while not stop:
            stop = True
            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    for symbol in production:
                        if symbol in self.nonterminals:
                            firstSymbol = self.first[symbol].copy()
                            if '&' in firstSymbol:
                                firstSymbol.remove('&')
                            if not firstSymbol.issubset(self.first[nonterminal]):
                                self.first[nonterminal] = self.first[nonterminal].union(firstSymbol)
                                stop = False

                            if "&" not in self.first[symbol]:
                                break
                        else:
                            self.first[nonterminal].add(symbol)
                            break
                        
        return self.first

    def calculateFollow(self):
        """Calcula o conjunto follow dos não-terminais da gramática"""
        self.follow.clear()
        
        self.calculateFirst()

        for nonterminal in self.nonterminals:
            self.follow[nonterminal] = set()
            if nonterminal == self.initial:
                self.follow[nonterminal].add("$")

        stop = False
        while not stop:
            stop = True
            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    # 1. Se A ::= ɑBβ e β != ɛ, então Follow(B) = Follow(B) ∪ First(β) 
                    for i, symbol in enumerate(production[:-1]):
                        if symbol in self.nonterminals: # Somente não-terminais possuem FOLLOW
                            for j in range(i + 1, len(production)):  # Verifica símbolos seguintes
                                firstOfCurrentProduction = self.first[production[j]].copy()
                                if '&' in firstOfCurrentProduction:
                                    firstOfCurrentProduction.remove('&')
                                if not firstOfCurrentProduction.issubset(self.follow[symbol]):
                                    self.follow[symbol] = self.follow[symbol].union(firstOfCurrentProduction)
                                    stop = False
                                # Se & pertence ao First do símbolo atual nonTerminalProduction[j] continua, senão, para
                                if "&" not in self.first[production[j]]:
                                    break
                                
                    # 2. Se A ::= ɑB (ou A ::= ɑBβ, onde & pertence à First(β)), então Follow(A) |= Follow(B)
                    for i, symbol in enumerate(production[::-1]): # Varre produção ao contrário
                        if symbol not in self.nonterminals:
                            break

                        if not self.follow[nonterminal].issubset(self.follow[symbol]):
                            self.follow[symbol] = self.follow[symbol].union(self.follow[nonterminal])
                            stop = False

                        # Se & pertence ao FIRST do símbolo atual nonTerminalProduction[j], continua, senão, para
                        if "&" not in self.first[production[i]]:
                            break

        return self.follow
    
    def eliminateDirectLeftRecursion(self, symbol):
        alphas = list()
        betas = list()
        newSymbol = f"{symbol}\'"
        
        for production in self.productions[symbol]:
            if production[0] is symbol:
                alpha = production[1:].copy()
                alpha.append(newSymbol)
                alphas.append(alpha)
            elif production == ['&']:
                betas.append(['&'])
            else:
                beta = production.copy()
                beta.append(newSymbol)
                betas.append(beta)
        
        if len(alphas) > 0:
            alphas.append(['&'])
            self.productions[newSymbol] = alphas
            self.nonterminals.append(newSymbol)
            self.productions[symbol] = betas
            
    
    def eliminateLeftRecursion(self):
        """Retorna uma gramática equivalente, eliminando recursão a esquerda"""

        for symbol in self.nonterminals:
            self.eliminateDirectLeftRecursion(symbol)

        # elimina &-producoes
        # self.eliminateEpsilonProductions()
        
        nonterminals = enumerate(self.N)
        for (i, nonTerminali) in nonterminals:
            for nonTerminalj in [nonTerminalj for j, nonTermninalj in nonterminals if j < i]:
                for production in self.productions[nonTerminali]:
                    if production[0] is nonTerminalj:
                        self.productions[nonTerminali].remove(production)
                        for productionBeta in self.productions[nonTerminalj]:
                            productionBeta = productionBeta.copy()
                            productionBeta.append(production[1:].copy())
                            self.productions[nonTerminali].append(productionBeta)
            self.eliminateDirectLeftRecursion(nonTerminali)

        # elimina &-producoes
        # self.eliminateEpsilonProductions()

        return self