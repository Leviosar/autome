from fileinput import filename
import json
from math import prod
from pprint import pprint
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
    def parse(cls, input: click.Path):
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
    
    def left_factoring(self, *, iters=10):
        """Fatoração de GLC"""
        self.remove_direct_non_determinism()
        
        for _ in range(iters):
            changed = self.remove_indirect_non_determinism()
            
            self.remove_direct_non_determinism()
            
            if not changed:
                break
        else:
            return False
        
        return True

    def remove_direct_non_determinism(self):
        """Remoção de não determinismo direto"""
        productions = self.productions
        new = {}
        
        for nonterminal in productions:
            new[nonterminal] = []
            prefixes = []
            
            for first in productions[nonterminal]:
                if not prefixes:
                    prefixes.append(first)
                    continue
                
                prefix_found = False
                prefix = []
                
                for i, second in enumerate(prefixes):
                    for p1, p2 in zip(first, second):
                        if p1 != p2:
                            break
                        prefix.append(p1)
                    if prefix and not prefix_found:
                        prefixes[i] = prefix
                        prefix_found = True
                if not prefix_found:
                    prefixes.append(first)
            
            count = 1
            for pref in prefixes:
                aux = []
                for prod in productions[nonterminal]:
                    if len(pref) <= len(prod) and pref == prod[:len(pref)]:
                        aux.append(prod)
                if len(aux) > 1:
                    symbol = f"{nonterminal}" + ("'" * count)
                    count += 1
                    self.nonterminals.append(symbol)
                    new_prod = pref + [symbol]
                    
                    if new_prod not in new[nonterminal]:
                        new[nonterminal].append(new_prod)
                    
                    new[symbol] = []

                    for p in aux:
                        p = p[len(pref):]
                        p = p if len(p) > 0 else ['&']
                        new[symbol].append(p)
                else:
                    new[nonterminal].append(pref)
        self.productions = new

    def remove_indirect_non_determinism(self):
        """ Identifica e remove os indeterminismos indiretos utilizando os conjuntos FIRST"""

        def get_firsts_chain(chain):
            """Helper para atualizar e buscar o first do primeiro simbolo da cadeia"""
            self.calculateFirst()

            if (chain[0] == '&'):
                return []

            return list(self.first[chain[0]])

        changed = False

        for symbol in self.productions:
            aux = []
            worrisome = set()

            for prod in self.productions[symbol]:
                firsts = get_firsts_chain(prod)

                for a in aux:
                    if len(set(firsts).intersection(a[1])) > 0:
                        worrisome.add(tuple(prod))
                        worrisome.add(tuple(a[0]))
                        changed = True

                for i, symbol in enumerate(prod[:-1]):
                    if symbol in self.nonterminals and '&' in self.first[symbol]:
                        if len(self.first[symbol].intersection(get_firsts_chain(prod[i + 1:]))) > 0:
                            worrisome.add(prod)
                            changed = True

                aux.append((prod, firsts))
            
            for prod in worrisome:
                self.productions[symbol].remove(list(prod))

            for prod in worrisome:
                derivations = self.derive(list(prod))
                for d in derivations:
                    if d not in self.productions[symbol]:
                        self.productions[symbol].append(d)
        return changed

    def table(self):
        """Gera tabela de parse LL(1)"""
        self.calculateFirst()
        self.calculateFollow()

        table = {}

        for nonterminal, productions in self.productions.items():
            table[nonterminal] = {}

            for alpha in productions:
                if alpha[0] == '&':
                    # Adicionar follow da cabeça para transições epsilon
                    firsts = ['&']
                else:
                    # Verificar se a produção pode ser anulável
                    firsts = self.first[alpha[0]]

                for symbol in firsts:
                    if symbol in self.terminals:
                        if symbol == "&":
                            table[nonterminal]["$"] = alpha
                        else:
                            table[nonterminal][symbol] = alpha
                
                if '&' in firsts:
                    for symbol in self.follow[nonterminal]:
                        if symbol in self.terminals:
                            if symbol == "&":
                                table[nonterminal]["$"] = alpha
                            else:
                                table[nonterminal][symbol] = alpha
        return table
    
    def accept(self, sentence, show_steps=False):
        """Reconhece sentença via implementação de um analisador LL(1)"""
        table = self.table()
        pprint(table)
        if show_steps:
            print(f"\nMostrando passos para o reconhecimento da sentença {' '.join(sentence)} com a gramática:")
            print(self)
            print('Conjuntos FIRST')
            for symbol, firsts in self.first.items():
                print(f'FIRST({symbol}) = {firsts}')

            print('Conjuntos FOLLOW')
            for symbol, follow in self.follow.items():
                print(f'FOLLOW({symbol}) = {follow}')

        stack = ["$", self.initial]
        sentence += '$'  # adiciona fim da leitura
        i = 0
        symbol = sentence[i]
        while stack != ['$'] and i < len(sentence):
            if show_steps:
                print(f'Cabeçote: {symbol}; Pilha: {stack}')
            if stack[-1] in self.terminals:
                if i + 1 < len(sentence):
                    i += 1
                symbol = sentence[i]
                stack.pop()
                continue
            if symbol not in table[stack[-1]]:
                print('cy')
                break
            prod = table[stack[-1]][symbol]
            stack.pop()
            if prod == ["&"]:
                continue
            elif prod:
                for p in reversed(prod):
                    stack.append(p)
        output = 'aceita' if stack == ["$"] else 'rejeita'
        if show_steps:
            print(f'Cabeçote: {symbol}; Pilha: {stack}')
            print(f'\n{output} sentença')
        return stack == ["$"]