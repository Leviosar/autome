import json
from pprint import pprint
import click

from typing import List
from tabulate import tabulate
from autome.utils.dataclasses import Token
from autome.utils.errors import SyntaxException


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
        """Calculate the 'first' set of all the symbols in the grammar

        Returns:
            Dict: mapping of the sets containing the 'first', indexed by symbol
        """
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
        """Return the first set of a sequence (calculating nullable symbols)

        Args:
            sequence List[str]: the input sequence

        Returns:
            Set[str]: the set holding the firsts of the sequence
        """
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
        """Calculate the follow set for all the nonterminals in the grammar

        Returns:
            Dict: mapping with all the follow sets, indexed by nonterminals
        """
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
                            # if production == ['&']:
                            #     continue

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
        """Helper to eliminate direct left recursion on a given symbol

        Args:
            symbol String: the non terminal holding the left recursion
        """
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
        """Eliminate left recursion by manipulating the grammar and passing the recursion to the right of the productions

        Returns:
            Grammar: the altered grammar
        """

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
        """Procedure for removing non-determinism on the grammar. While removing direct determinism, you can create
        a new non-determinism in another production and this can occur in a loop, so this proccess is not decidible
        by a Turing Machine. Hence, this function tries up to @iters times to remove, if after this number of
        iterations the grammar keeps changing, we return false and you should stop the execution of your program

        Args:
            iters (int, optional): Total iterations. Defaults to 10.

        Returns:
            boolean: true if the grammar could be factorated, false otherwise.
        """
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
        """Recursively returns a list of all derivations that can be made by a given production

        Args:
            prod List[string]: list of symbols representing a production

        Returns:
            List[List[string]]: all the derivations that can be generated starting at the given production
        """
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
        """Searches for direct non-determinism and removes them by factoring the grammar to the left"""
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

    def remove_indirect_non_determinism(self):
        """Search for indirect non-determinisms and removes them by transforming into direct
        nondeterminisms using sucessive derivations

        Returns:
            boolean: true if the function modified the grammar, false otherwise
        """

        def get_firsts_chain(chain):
            """Returns the first set of an entire sequence of symbols

            Args:
                chain List[String]: the chain for which the first should be calculated

            Returns:
                List[String]: A list containing First(@chain)
            """
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
                            try:
                                worrisome.add(prod)
                            except TypeError:
                                print(f"Opsie {prod}")
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
        """Mounts the syntax analysis table for the LL(1) algorithim using first and follow.

        Returns:
            Dict: the table containing all the information needed for LL(1) parsing
        """
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

    def display_analysis_table(self, table):
        print("\nLL(1) analysis table\n")
        m = len(self.terminals) + 2
        n = len(self.nonterminals) + 2

        data = [["-" for i in range(m)] for j in range(n)]
        for column in range(1, n):
            data[column][0] = self.nonterminals[column - 2]

        for row in range(1, m):
            if row == len(self.terminals) + 1:
                data[0][row] = "$"
            else:
                data[0][row] = self.terminals[row - 2]

        for column in range(1, n):
            for row in range(1, m):
                if data[0][row] == "$":
                    nonterminal = data[column][0]
                    terminal = "$"
                else:
                    nonterminal = data[column][0]
                    terminal = data[0][row]

                try:
                    data[column][row] = " ".join(table[nonterminal][terminal])
                except KeyError:
                    pass

        print(tabulate(data, tablefmt="fancy_grid"))

    def accept(self, tokens: List[Token], debug=False):
        """Validates a sequence of tokens using the LL(1) parser. This wrapper already
        calculate First and Follow sets, eliminates left recursion and apply left factoring
        to remove non-determinism to the grammar.

        Args:
            tokens (List[Token]): List of tokens to be validated
            debug (bool, optional): Debug level flag. Defaults to False.

        Raises:
            SyntaxException: if a syntax error is found

        Returns:
            boolean: the result of the validation
        """
        self.calculate_first()
        self.calculate_follow()
        self.eliminate_left_recursion()
        self.left_factoring()

        table = self.table()

        if debug:
            self.display_analysis_table(table)
        
        stack = ["$", self.initial]

        sentence = " ".join([token.type for token in tokens])
        sentence = sentence.split(" ")
        sentence.append("$")
        i = 0
        symbol = sentence[i]

        if debug:
            print("\nLL(1) recognition stack:\n")

        while stack != ["$"] and i < len(sentence):
            if debug:
                print(f"Input: {symbol}; Stack: {stack}")

            if stack[-1] in self.terminals:
                if i + 1 < len(sentence):
                    i += 1

                symbol = sentence[i]
                stack.pop()

                continue

            if symbol not in table[stack[-1]]:
                if symbol == "$":
                    raise SyntaxException(f"Unexpected EOL: {sentence[i - 1]}")
                else:
                    raise SyntaxException(f"Unexpected symbol: {symbol}")

            prod = table[stack[-1]][symbol]
            stack.pop()

            if prod == ["&"]:
                continue
            elif prod:
                for p in reversed(prod):
                    stack.append(p)

        if debug:
            print(f"Input: {symbol}; Stack: {stack}")

        return stack == ["$"] and sentence[i] == "$"
