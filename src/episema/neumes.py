from typing import List
from .chant import ChantNotationElement, Note

class Neume(ChantNotationElement):
    def __init__(self, notes: List[Note] = None):
        super().__init__()
        self.is_neume = True
        self.notes = notes if notes is not None else []
        
        for note in self.notes:
            note.neume = self

    def add_note(self, note: Note):
        note.neume = self
        self.notes.append(note)

    def perform_layout(self, ctxt):
        super().perform_layout(ctxt)
        # Stub

# Subclasses

class Punctum(Neume):
    pass

class Virga(Neume):
    pass

class PunctaInclinata(Neume):
    pass

class Apostropha(Neume):
    pass

class Oriscus(Neume):
    pass

class Podatus(Neume):
    pass

class Clivis(Neume):
    pass

class Climacus(Neume):
    pass

class Porrectus(Neume):
    pass

class PorrectusFlexus(Neume):
    pass

class PesSubpunctis(Neume):
    pass

class Salicus(Neume):
    pass

class SalicusFlexus(Neume):
    pass

class Scandicus(Neume):
    pass

class ScandicusFlexus(Neume):
    pass

class PesQuassus(Neume):
    pass

class Bivirga(Neume):
    pass

class Trivirga(Neume):
    pass

class Distropha(Neume):
    pass

class Torculus(Neume):
    pass

class TorculusResupinus(Neume):
    pass
