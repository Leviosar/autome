import copy

from AF import AF


class GLC:
    """
        Uma Gramática Livre de Contexto é uma quadrupla (N, T, P, S) onde:
            - N é o conjunto de símbolos não terminais
            - T é o conjunto de símbolos terminais (o alfabeto)
            - S é o símbolo inicial
            - P é o conjunto de regras de produção, tal que:
                P = { A ::= delta, onde A pertence a N
                    e delta é uma lista de listas de terminais e não-terminais }
                    (cada sublista de delta é uma lista ordenada que representa
                    uma produção)
    """

    def __init__(self, N=None, T=None, S=None, P=None, name=''):
        self.N = N if N else list()
        self.T = T if T else list()
        self.S = S if S else list()
        self.P = P if P else dict()

        self.name = name

        self._first = dict()
        self._follow = dict()

    def __str__(self):
        glc_str = ''
        for origin, productions in self.P.items():
            glc_str += f"{origin} ::= " + \
                       ' | '.join([' '.join(prod) for prod in productions]) + \
                       '\n'
        return glc_str

    def read_grammar(self, filename):
        """Importa gramática de arquivo"""
        with open(filename, 'r') as f:
            # nonterminals
            line = f.readline()
            non_terminals = []
            while True:
                line = f.readline().rstrip('\n')
                if line[0] == '#':
                    break
                non_terminals.append(line)
            # terminals
            terminals = []
            while True:
                line = f.readline().rstrip('\n')
                if line[0] == '#':
                    break
                terminals.append(line)
            if set(non_terminals).intersection(set(terminals)):
                raise ValueError('Algum símbolo aparece nas listas de terminais e não terminais')
            # start
            start = f.readline().rstrip('\n')
            # productions
            productions = {}
            line = f.readline()
            while True:
                line = f.readline().rstrip('\n')
                if line == '':
                    break
                line = line.split(" ::= ")
                origin = line[0]
                prods = [prod.split(' ') for prod in line[1].split("|") if prod]
                prods = [list(filter(lambda val: val != '', prod)) for prod in prods]
                productions[origin] = prods
            self.T = terminals
            self.S = start
            self.N = non_terminals
            self.P = productions

    def export(self, file_name):
        """Exporta gramática para arquivo"""
        with open(file_name, "w") as file:
            file.write("#nonterminals\n")
            for s in self.N:
                file.write(f"{s}\n")
            file.write("#terminals\n")
            for s in self.T:
                file.write(f"{s}\n")
            file.write("#start\n")
            file.write(f"{self.S}\n")
            file.write("#productions\n")
            file.write(str(self))

    def setFirst(self):
        """Calcula o conjunto first da gramática"""
        self._first.clear()
        debug = False

        for terminal in self.T:  # FIRST de um terminal é o próprio terminal
            self._first[terminal] = {terminal}

        for nonTerminal in self.N:  # Definição dos first de cada não-terminal
            self._first[nonTerminal] = set()
        # 1. Se X ::= aY, a pertence à FIRST(X)
        for nonTerminal in self.N:
            for nonTerminalProduction in self.P[nonTerminal]:
                if nonTerminalProduction[0] in self.T:
                    if debug:
                        print(f"{nonTerminalProduction[0]} pertence à FIRST({nonTerminal})={self._first[nonTerminal]}")
                    self._first[nonTerminal].add(nonTerminalProduction[0])

        # 2. Se X ::= Y1 Y2...Yk, então FIRST(Y1) pertence à FIRST(X)
        finished = False
        while not finished:
            finished = True
            for nonTerminal in self.N:
                for nonTerminalProduction in self.P[nonTerminal]:
                    for symbol in nonTerminalProduction:
                        if symbol in self.N:
                            firstSymbol = self._first[symbol].copy()
                            if '&' in firstSymbol:
                                firstSymbol.remove('&')
                            if not firstSymbol.issubset(self._first[nonTerminal]):
                                if debug:
                                    print(
                                        f"FIRST({symbol})={self._first[symbol]} está contido em FIRST({nonTerminal})={self._first[nonTerminal]}")
                                self._first[nonTerminal] = self._first[nonTerminal].union(firstSymbol)
                                finished = False

                            if "&" not in self._first[symbol]:
                                break
                        else:
                            self._first[nonTerminal].add(symbol)
                            break
        if debug:
            print(self._first)

        return self._first

    def setFollow(self):
        """Calcula o conjunto follow dos não-terminais da gramática"""
        self._follow.clear()
        self.setFirst()
        debug = False

        if debug:
            print(f"FIRST={self._first}")

        for nonTerminal in self.N:  # Definição dos follows de cada não-terminal
            self._follow[nonTerminal] = set()
            if nonTerminal == self.S:
                self._follow[nonTerminal].add("$")

        finished = False
        while not finished:  # Enquanto houver alteração nos FOLLOWS
            finished = True
            # Para cada não-terminal nonTerminal
            for nonTerminal in self.N:
                # Para cada produção nonTerminalProduction de nonTerminal
                for nonTerminalProduction in self.P[nonTerminal]:
                    # 1. Se A ::= alfa B beta e beta != &, então adicione FIRST(beta) em FOLLOW(B)
                    # Para cada símbolo symbol da produção nonTerminalProduction
                    for i, symbol in enumerate(nonTerminalProduction[:-1]):
                        if symbol in self.N:  # Somente não-terminais possuem FOLLOW
                            for j in range(i + 1, len(nonTerminalProduction)):  # Verifica símbolos seguintes
                                firstNonTerminalProductionJ = self._first[nonTerminalProduction[j]]
                                if '&' in firstNonTerminalProductionJ:
                                    firstNonTerminalProductionJ.remove('&')
                                if not firstNonTerminalProductionJ.issubset(self._follow[symbol]):
                                    if debug:
                                        print(
                                            f"FIRST({nonTerminalProduction[j]})={self._first[nonTerminalProduction[j]]}"
                                            + f"está contido em FOLLOW({symbol})={self._follow[symbol]}")
                                    self._follow[symbol] = self._follow[symbol].union(firstNonTerminalProductionJ)
                                    finished = False
                                # Se & pertence ao FIRST do símbolo atual nonTerminalProduction[j] continua, senão, para
                                if "&" not in self._first[nonTerminalProduction[j]]:
                                    break
                    # 2. Se A ::= alfa B (ou A ::= alfa B beta, onde & pertence à FIRST(beta)),
                    # então adicione FOLLOW(A) em FOLLOW(B)
                    for i, symbol in enumerate(nonTerminalProduction[::-1]):  # Varre produção ao contrário
                        if symbol not in self.N:  # Se o símbolo for terminal, para
                            break

                        if not self._follow[nonTerminal].issubset(self._follow[symbol]):
                            if debug:
                                print(
                                    f"FOLLOW({nonTerminal})={self._follow[nonTerminal]}"
                                    + f"está contido em FOLLOW({symbol})={self._follow[symbol]}")
                            self._follow[symbol] = self._follow[symbol].union(self._follow[nonTerminal])
                            finished = False

                        # Se & pertence ao FIRST do símbolo atual nonTerminalProduction[j], continua, senão, para
                        if "&" not in self._first[nonTerminalProduction[i]]:
                            break

        if debug:
            print(f"FOLLOW={self._follow}")

        return self._follow

    def removeUnproductiveSymbols(self):
        """Retorna uma gramática equivalente, sem símbolos improdutivos"""
        markedTSymbols = []
        productions = dict()

        def dict_deep_length(dic):
            l = 0
            for e in dic:
                if isinstance(e, list):
                    l += len(e)
                else:
                    l += 1
            return l

        productionCount = 0

        while True:
            for nonTerminal, production in [(nonTerm, prod)
                                            for nonTerm in self.N
                                            for prod in self.P[nonTerminal]]:

                if productions[nonTerminal] and production in productions[nonTerminal]:
                    break

                nonMarked = copy.copy(production)
                for symbol in production:
                    # remove todas as ocorrências de symbol
                    if symbol in self.T:
                        if symbol not in markedTSymbols:
                            markedTSymbols.append(symbol)
                        continue
                    if symbol not in self.N or not productions[symbol]:
                        continue
                    nonMarked = list(filter(symbol.__ne__, nonMarked))

                if not nonMarked:
                    if not productions[nonTerminal]:
                        productions[nonTerminal] = []
                    productions[nonTerminal].append(production)

            currentProductionCount = dict_deep_length(productions)
            if currentProductionCount != productionCount:
                productionCount = currentProductionCount
            else:
                break

        return GLC(productions.keys(), markedTSymbols, self.S, productions, self.name)


    def eliminateEpsilonProductions(self):
        """Elimina de epsilon produções"""
        
        debug = False
        if debug:
            print("--> entering eliminateEpsilonProductions")

        # Lista de não-terminais anuláveis
        nullable = list()
        
        ### Primeiro, encontra-se os não-terminais anuláveis

        possiblyNullableProductions = dict()

        # Primeira passagem pelos não-terminais. 
        # Identifica os anuláveis triviais (que contém '&' nas produções)
        # E as produções que podem ser descobertas anuláveis nas próximas passagens.
        for nonTerminal in self.N:

            # Produções possivelmente anuláveis de nonTerminal
            possiblyNullableProductions[nonTerminal] = list()
            
            for production in self.P[nonTerminal]:
                if production[0] is '&':
                    nullable.append(nonTerminal)
                    break

                possiblyNullableProduction = True
                for symbol in production:
                    if symbol in self.T:
                        possiblyNullableProduction = False
                        break
                    
                if possiblyNullableProduction:
                    possiblyNullableProductions[nonTerminal].append(production)

        # Agora vamos revisar os  não-terminais repetidamente até que nenhum novo
        # não terminal anulável tenha sido descoberto
        previousNullableLen = len(nullable)
        while True:
            for nonTerminal in [nonTerminal for nonTerminal in self.N if nonTerminal not in nullable]:
                for production in possiblyNullableProductions[nonTerminal]:
                    for symbol in production:
                        if symbol not in nullable:
                            break
                    else:
                        nullable.append(nonTerminal)
                        break
            if previousNullableLen == len(nullable):
                break
            else:
                previousNullableLen = len(nullable)

        if debug:
            print(f"nullables found: {nullable}")

        # Agora vamos substituir as produções com não-terminais anuláveis
        # por todos os seus arranjos com e sem esses não-terminais
        newProductions = dict()
        for nonTerminal in self.N:

            if debug:
                print(f"For non-terminal {nonTerminal} with productions {self.P[nonTerminal]}:")

            newProductions[nonTerminal] = list()

            for production in self.P[nonTerminal]:

                if production == ['&']:
                    break

                partialProductions = list()
                partialProductions.append(['&'])

                for symbol in production:

                    if debug:
                        print(f"in production {production}")
                        print(f"reading symbol {symbol}")

                    nextPartialProductions = partialProductions.copy()

                    for partProd in partialProductions:

                        if partProd == ['&']:
                            if symbol not in nullable:
                                nextPartialProductions.remove(['&'])
                            nextPartialProductions.append([symbol])

                        else:
                            if symbol not in nullable:
                                nextPartialProductions.remove(partProd)
                            temp = partProd.copy()
                            temp.append(symbol)
                            nextPartialProductions.append(temp)

                    partialProductions = nextPartialProductions

                    if debug:
                        print(f"PartialProductions: {partialProductions}")

                for prod in partialProductions:
                    for prod2 in newProductions:
                        if prod == prod2:
                            break
                    else:
                        newProductions[nonTerminal].append(prod)

            if debug:
                print(f"productions for {nonTerminal} before: {self.P[nonTerminal]}")
                print(f"productions for {nonTerminal} later: {newProductions[nonTerminal]}")

        self.P = newProductions

    def llRecognizeSentence(self, sentence, show_steps=False):
        """Reconhece sentença via implementação de um analisador LL(1)"""
        table = self.generateLLparseTable()
        if show_steps:
            print(f"\nMostrando passos para o reconhecimento da sentença {' '.join(sentence)} com a gramática:")
            print(self)
            print('Conjuntos FIRST')
            for symbol, firsts in self._first.items():
                print(f'FIRST({symbol}) = {firsts}')

            print('Conjuntos FOLLOW')
            for symbol, follow in self._follow.items():
                print(f'FOLLOW({symbol}) = {follow}')

        stack = ["$", self.S]
        sentence += '$'  # adiciona fim da leitura
        i = 0
        symbol = sentence[i]
        while stack != ['$'] and i < len(sentence):
            if show_steps:
                print(f'Cabeçote: {symbol}; Pilha: {stack}')
            if stack[-1] in self.T:
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
        output = 'aceita' if stack == ["$"] else 'rejeita'
        if show_steps:
            print(f'Cabeçote: {symbol}; Pilha: {stack}')
            print(f'\n{output} sentença')
        return stack == ["$"]

    def generateLLparseTable(self):
        """Gera tabela de parse LL(1)"""
        self.setFirst()
        self.setFollow()
        table = {}
        # itero sobre as produções de cada terminal da gramática
        for non_terminal, productions in self.P.items():
            table[non_terminal] = {}
            # itero sobre as produções do não terminal
            for alpha in productions:
                firsts = self._first[alpha[0]]
                for symbol in firsts:
                    if symbol in self.T:
                        if symbol == "&":
                            table[non_terminal]["$"] = alpha
                        else:
                            table[non_terminal][symbol] = alpha
                if '&' in firsts:
                    for symbol in self._follow[non_terminal]:
                        if symbol in self.T:
                            if symbol == "&":
                                table[non_terminal]["$"] = alpha
                            else:
                                table[non_terminal][symbol] = alpha
        return table


    def eliminateLeftRecursion(self):
        """Retorna uma gramática equivalente, eliminando recursão a esquerda"""

        debug = False
        if debug:
            print("--> entering eliminateLeftRecursion")

        def eliminateDirectLeftRecursion(nonTerminal):
            """ Utilitário para eliminação de recursão direta"""

            if debug:
                print(f"entering eliminateDirectLeftRecursion for {nonTerminal}")
                print(f"productions before: {self.P[nonTerminal]}")

            alphas = list()
            betas = list()
            ntDash = f"{nonTerminal}\'"
            epsilonFlag = False
            
            for production in self.P[nonTerminal]:
                if production[0] is nonTerminal:
                    alpha = production[1:].copy()
                    alpha.append(ntDash)
                    alphas.append(alpha)
                elif production == ['&']:
                    betas.append(['&'])
                else:
                    beta = production.copy()
                    beta.append(ntDash)
                    betas.append(beta)
            
            if len(alphas) > 0:
                alphas.append(['&'])

                self.P[ntDash] = alphas
                self.N.append(ntDash)
                self.P[nonTerminal] = betas
                
                if debug:
                    print("new productions:")
                    print(f"P[{nonTerminal}]: {self.P[nonTerminal]}")
                    print(f"P[{ntDash}]: {self.P[ntDash]}")

            elif debug:
                print("no direct left recursion found. Nothing changed.")

        # elimina recursoes diretas
        for nonTerminal in self.N:
            eliminateDirectLeftRecursion(nonTerminal)

        # elimina &-producoes
        self.eliminateEpsilonProductions()

        # elimina recursoes indiretas
        if debug:
            print("--> initiating indirect recursion removal")

        nonTerminalEnumeration = enumerate(self.N)
        for (i, nonTerminali) in nonTerminalEnumeration:
            for nonTerminalj in [nonTerminalj for j, nonTermninalj in nonTerminalEnumeration if j < i]:
                for production in self.P[nonTerminali]:
                    if production[0] is nonTerminalj:
                        self.P[nonTerminali].remove(production)
                        for productionBeta in self.P[nonTerminalj]:
                            productionBeta = productionBeta.copy()
                            productionBeta.append(production[1:].copy())
                            self.P[nonTerminali].append(productionBeta)
            eliminateDirectLeftRecursion(nonTerminali)

        # elimina &-producoes
        # self.eliminateEpsilonProductions()

        return GLC(self.N, self.T, self.S, self.P, self.name)

    """ ---------------- FATORAÇÃO ----------------- """

    def left_factoring(self, *, iters=10, show_steps=False):
        """Fatoração de GLC"""
        #podemos comçear removendo determinismos diretos, para facilitar o trabalho
        if show_steps:
            print("Fatoração da gramática")
            print(self)
        self.__remove_direct_non_determinism()
        if show_steps:
            print(self)
        for _ in range(iters):
            changed = self.__remove_indirect_non_determinism()
            self.__remove_direct_non_determinism()
            if show_steps and changed:
                print(self)
            if not changed:
                break
        else:
            if show_steps:
                print('gramática não foi fatorada')
            return False
        if show_steps:
            print('gramática foi fatorada')
        return True

    def __remove_direct_non_determinism(self):
        """Remoção de não determinismo direto"""
        productions = self.P
        new_productions = {}
        for non_terminal in productions:
            new_productions[non_terminal] = []
            prefixes = []
            for prod1 in productions[non_terminal]:
                if not prefixes:
                    prefixes.append(prod1)
                    continue
                found_pref = False
                prefix = []
                for i, prod2 in enumerate(prefixes):
                    for p1, p2 in zip(prod1, prod2):
                        if p1 != p2:
                            break
                        prefix.append(p1)
                    if prefix and not found_pref:
                        prefixes[i] = prefix
                        found_pref = True
                if not found_pref:
                    prefixes.append(prod1)
            count = 1
            for pref in prefixes:
                prod_aux = []
                for prod in productions[non_terminal]:
                    # testamos se a produção começa com o prefixo salvo em pref
                    if len(pref) <= len(prod) and pref == prod[:len(pref)]:
                        prod_aux.append(prod)
                if len(prod_aux) > 1:
                    new_symbol = non_terminal + count*"'"
                    count += 1
                    self.N.append(new_symbol)
                    new_prod = pref + [new_symbol]
                    if new_prod not in new_productions[non_terminal]:
                        new_productions[non_terminal].append(new_prod)
                    new_productions[new_symbol] = []
                    for p in prod_aux:
                        p = p[len(pref):]
                        p = p if len(p) > 0 else ['&']
                        new_productions[new_symbol].append(p)
                else:
                    new_productions[non_terminal].append(pref)
        self.P = new_productions

    def derive(self, prod):
        """Gera lista de cadeias derivadas da produção"""
        if not prod:
            return [[]]
        prod_ = prod[0]
        if prod_ in self.T:
            return [[prod_] + derivation for derivation in self.derive(prod[1:])]
        elif prod_ in self.P:
            out = []
            derivations = self.derive(prod[1:])
            for p in self.P[prod_]:
                if p == ['&']:
                    out += derivations
                else:
                    if derivations:
                        out += [p + deriv for deriv in derivations]
                    else:
                        out += p
            return out

    def __remove_indirect_non_determinism(self):
        """ Identifica e remove os indeterminismos indiretos utilizando os conjuntos FIRST"""

        def get_firsts_chain(chain):
            """Helper para atualizar e buscar o first do primeiro simbolo da cadeia"""
            self.setFirst()
            return list(self._first[chain[0]])

        changed = False
        # busca não-determinismos indiretos e os elimina
        for s in self.P:
            aux = []
            worrisome = set()
            for prod in self.P[s]:
                firsts = get_firsts_chain(prod)
                # faz a intersecção com o first de uma produção salva
                for a in aux:
                    if len(set(firsts).intersection(a[1])) > 0:
                        worrisome.add(tuple(prod))
                        worrisome.add(tuple(a[0]))
                        changed = True
                for i, symbol in enumerate(prod[:-1]):
                    if symbol in self.N and '&' in self._first[symbol]:
                        if len(self._first[symbol].intersection(get_firsts_chain(prod[i + 1:]))) > 0:
                            worrisome.add(prod)
                            changed = True
                aux.append((prod, firsts))
            for prod in worrisome:
                self.P[s].remove(list(prod))
            for prod in worrisome:
                derivations = self.derive(list(prod))
                for d in derivations:
                    if d not in self.P[s]:  # precisamos deste if por estarmos usando lists e não sets
                        self.P[s].append(d)
        return changed
