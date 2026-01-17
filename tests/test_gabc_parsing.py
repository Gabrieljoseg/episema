import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from episema.gabc import Gabc
from episema.chant import ChantDocument, ChantScore
from episema.signs import QuarterBar
from episema.neumes import Punctum, Podatus

def test_basic_parsing():
    print("Testing basic parsing...")
    source = "(c4) A(f)men(fg)"
    
    # Mock context (needs active_clef)
    class Context:
        def __init__(self):
            self.active_clef = None
    
    ctxt = Context()
    
    mappings = Gabc.create_mappings_from_source(ctxt, source)
    
    print(f"Mappings count: {len(mappings)}")
    
    for i, m in enumerate(mappings):
        print(f"Mapping {i}: source='{m.source}'")
        for n in m.notations:
            print(f"  Notation: {type(n).__name__}")
            if hasattr(n, 'notes'):
                print(f"    Notes: {[note.pitch for note in n.notes]}")
            if hasattr(n, 'lyrics') and n.lyrics:
                print(f"    Lyrics: {[l.text for l in n.lyrics]}")

    # Assertions
    # Word 1: (c4) -> DoClef
    # Word 2: A(f) -> Punctum, Lyric "A"
    # Word 3: men(fg) -> Podatus (if my parser handles fg correctly as Podatus), Lyric "men"
    
    assert len(mappings) == 3
    assert mappings[0].notations[0].__class__.__name__ == 'DoClef'
    assert mappings[1].notations[0].__class__.__name__ == 'Punctum'
    assert mappings[1].notations[0].lyrics[0].text == "A"
    
    # Check Podatus logic in my simple FSM
    # f -> staff pos -1
    # g -> staff pos 0
    # g > f -> Podatus
    assert mappings[2].notations[0].__class__.__name__ == 'Podatus'
    assert mappings[2].notations[0].lyrics[0].text == "men"
    
    print("Test passed!")

if __name__ == "__main__":
    try:
        test_basic_parsing()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
