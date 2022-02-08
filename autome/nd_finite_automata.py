class NonDeterministicFiniteAutomata(FiniteAutomata):

    def run(self, word):
        return self.determinize().run(word)

    def determinize(args):
        