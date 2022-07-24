import json
import click

from fileinput import filename
from pprint import pprint
from typing import List
from tabulate import tabulate

from autome.interface.sintaxo import display_analysis_table


class Symbol:
    def __init__(self, name: str, terminal: bool):
        self.name = name
        self.terminal = terminal


class CFG:
    def __init__(
        self,
        nonterminals: List[str],
        terminals=List[str],
        initial=str,
        productions=None,
        name="",
    ):
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
            prods = ["".join(prod) for prod in body]
            joined = "|".join(prods)
            content.append(f"{head} → {joined}\n")

        return "".join(content)

    @classmethod
    def parse(cls, input: click.Path):
        with open(input, "r") as file:
            content = json.load(file)

        grammar = content["grammar"]

        nonterminals = grammar["nonterminals"]

        initial = grammar["initial"]
        if initial not in nonterminals:
            raise Exception("The initial symbol must be a part of the nonterminals set")

        terminals = grammar["terminals"]

        productions = dict()

        for production in grammar["productions"]:
            prods = [prod.split(" ") for prod in production["body"].split("|") if prod]
            prods = [list(filter(lambda val: val != "", prod)) for prod in prods]
            productions[production["head"]] = prods

        return CFG(nonterminals, terminals, initial, productions)

    def calculate_first(self):
        """Calcula o conjunto first da gramática"""
        self.first.clear()

        # First(a) = {a}
        for terminal in self.terminals:
            self.first[terminal] = {terminal}

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
                            if "&" in firstSymbol:
                                firstSymbol.remove("&")
                            if not firstSymbol.issubset(self.first[nonterminal]):
                                self.first[nonterminal] = self.first[nonterminal].union(
                                    firstSymbol
                                )
                                stop = False

                            if "&" not in self.first[symbol]:
                                break
                        else:
                            self.first[nonterminal].add(symbol)
                            break

        return self.first

    def first_of_sequence(self, sequence):
        firsts = set()

        for index, symbol in enumerate(sequence):
            firsts = firsts.union(self.first[symbol]) - {"&"}

            # Se o first não tem  epsilon, não precisamos continuar pensando se será ou não anulável
            if "&" not in self.first[symbol]:
                break

            # Se chegou no último símbolo da produção, e esse símbolo é anulável, então precisamos adicionar o follow também
            if index == len(sequence) - 1:
                firsts.add("&")

        return firsts

    def calculate_follow(self):
        """Calcula o conjunto follow dos não-terminais da gramática"""
        self.follow.clear()

        self.calculate_first()

        follows = {symbol: set() for symbol in self.nonterminals}

        follows[self.initial].add("$")

        changed = True

        while changed:
            changed = False

            for head, productions in self.productions.items():
                for production in productions:
                    for i, symbol in enumerate(production):
                        if symbol in self.terminals:
                            continue

                        sequence = production[i + 1 :]

                        # This means that this nonterminal is the last in the production
                        if len(sequence) == 0:
                            follows[symbol] = follows[symbol].union(follows[head])

                            continue

                        firsts = self.first_of_sequence(sequence)

                        old_follow = follows[symbol].copy()

                        follows[symbol] = follows[symbol].union(firsts - {"&"})

                        if "&" in firsts:
                            follows[symbol] = follows[symbol].union(follows[head])

                        if old_follow != follows[symbol]:
                            changed = True

        self.follow = follows

        return self.follow

    def eliminate_direct_left_recursion(self, symbol):
        alphas = list()
        betas = list()
        newSymbol = f"{symbol}'"

        for production in self.productions[symbol]:
            if production[0] is symbol:
                alpha = production[1:].copy()
                alpha.append(newSymbol)
                alphas.append(alpha)
            elif production == ["&"]:
                betas.append(["&"])
            else:
                beta = production.copy()
                beta.append(newSymbol)
                betas.append(beta)

        if len(alphas) > 0:
            alphas.append(["&"])
            self.productions[newSymbol] = alphas
            self.nonterminals.append(newSymbol)
            self.productions[symbol] = betas

    def eliminate_left_recursion(self):
        """Retorna uma gramática equivalente, eliminando recursão a esquerda"""

        for symbol in self.nonterminals:
            self.eliminate_direct_left_recursion(symbol)

        nonterminals = enumerate(self.nonterminals)
        for (i, nonTerminali) in nonterminals:
            for nonTerminalj in [
                nonTerminalj for j, nonTermninalj in nonterminals if j < i
            ]:
                for production in self.productions[nonTerminali]:
                    if production[0] is nonTerminalj:
                        self.productions[nonTerminali].remove(production)
                        for productionBeta in self.productions[nonTerminalj]:
                            productionBeta = productionBeta.copy()
                            productionBeta.append(production[1:].copy())
                            self.productions[nonTerminali].append(productionBeta)
            self.eliminate_direct_left_recursion(nonTerminali)

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

    def derive(self, prod):
        """Gera lista de cadeias derivadas da produção"""
        if not prod:
            return [[]]
        prod_ = prod[0]
        if prod_ in self.terminals:
            return [[prod_] + derivation for derivation in self.derive(prod[1:])]
        elif prod_ in self.productions:
            out = []
            derivations = self.derive(prod[1:])
            for p in self.productions[prod_]:
                if p == ["&"]:
                    out += derivations
                else:
                    if derivations:
                        out += [p + deriv for deriv in derivations]
                    else:
                        out += p
            return out

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
                    if len(pref) <= len(prod) and pref == prod[: len(pref)]:
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
                        p = p[len(pref) :]
                        p = p if len(p) > 0 else ["&"]
                        new[symbol].append(p)
                else:
                    new[nonterminal].append(pref)
        self.productions = new

    def mine_remove(self):
        def get_firsts_chain(chain):
            """Helper para atualizar e buscar o first do primeiro simbolo da cadeia"""
            self.calculate_first()

            if chain[0] == "&":
                return []
            # print(self.first)
            r = self.first[chain[0]]
            # print(r)

            return r

        for head, productions in self.productions.items():
            firsts = []
            print(f"CABEÇA: {head}")
            print(self)
            for i, production in enumerate(productions):
                firsts.append(get_firsts_chain(production))

            intersections = set()

            for i in range(len(firsts)):
                for j in range(len(firsts)):
                    # Not intersection the set with itself
                    if i == j:
                        continue

                    intersections.union(firsts[i].intersection(firsts[j]))
            print(firsts)
            print(intersections)

    def remove_indirect_non_determinism(self):
        """Identifica e remove os indeterminismos indiretos utilizando os conjuntos FIRST"""
        # self.mine_remove()

        # 2 / 0
        def get_firsts_chain(chain):
            """Helper para atualizar e buscar o first do primeiro simbolo da cadeia"""
            self.calculate_first()

            if chain[0] == "&":
                return ["&"]

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
                    if symbol in self.nonterminals and "&" in self.first[symbol]:
                        if (
                            len(
                                self.first[symbol].intersection(
                                    get_firsts_chain(prod[i + 1 :])
                                )
                            )
                            > 0
                        ):
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
        self.calculate_first()
        self.calculate_follow()

        table = {}

        for production_head, productions in self.productions.items():
            table[production_head] = {}

            for alpha in productions:
                firsts = set()

                # Edge case for a production like B -> &
                if alpha[0] == "&":
                    firsts = firsts.union(self.follow[production_head])

                # Verificar se a produção pode ser anulável
                for symbol in alpha:
                    firsts = firsts.union(self.first[symbol]) - {"&"}

                    # Se o first não tem  epsilon, não precisamos continuar pensando se será ou não anulável
                    if "&" not in self.first[symbol]:
                        break

                    # Se chegou no último símbolo da produção, e esse símbolo é anulável, então precisamos adicionar o follow também
                    if symbol == alpha[-1]:
                        firsts = firsts.union(self.follow[production_head])

                for symbol in firsts:
                    table[production_head][symbol] = alpha

        return table

    def print_firsts_follows(self):
        print("Conjuntos FIRST")
        for symbol, firsts in self.first.items():
            print(f"FIRST({symbol}) = {firsts}")

        print("Conjuntos FOLLOW")
        for symbol, follow in self.follow.items():
            print(f"FOLLOW({symbol}) = {follow}")

    def accept(self, sentence, show_steps=False):
        """Reconhece sentença via implementação de um analisador LL(1)"""
        self.calculate_first()
        self.calculate_follow()
        self.eliminate_left_recursion()
        self.left_factoring()

        table = self.table()

        display_analysis_table(self, table)

        if show_steps:
            print(
                f"\nMostrando passos para o reconhecimento da sentença {' '.join(sentence)} com a gramática:"
            )
            print(self)

            self.print_firsts_follows()

        stack = ["$", self.initial]

        sentence = sentence.split(" ")
        sentence.append("$")  # adiciona fim da leitura
        i = 0
        symbol = sentence[i]

        print("Senteça")
        print(sentence)

        while stack != ["$"] and i < len(sentence):
            if show_steps:
                print(f"Cabeçote: {symbol}; Pilha: {stack}")

            if stack[-1] in self.terminals:
                if i + 1 < len(sentence):
                    i += 1

                symbol = sentence[i]
                stack.pop()

                continue

            if symbol not in table[stack[-1]]:
                break

            prod = table[stack[-1]][symbol]
            stack.pop()

            if prod == ["&"]:
                continue
            elif prod:
                for p in reversed(prod):
                    stack.append(p)

        accepted = stack == ["$"] and sentence[i] == "$"

        if show_steps:
            output = "aceita" if accepted else "rejeita"

            print(f"Cabeçote: {symbol}; Pilha: {stack}")
            print(f"\n{output} sentença")

        return accepted
