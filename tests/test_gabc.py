import unittest
from episema.gabc import Gabc
from episema.chant import DoClef, Note, ChantScore
from episema.core import Step

class MockContext:
    def __init__(self):
        self.active_clef = None
        self.intra_neume_spacing = 0

class TestGabc(unittest.TestCase):

    def setUp(self):
        self.ctxt = MockContext()

    def test_create_mappings_simple(self):
        gabc = "(c4) (f)"
        mappings = Gabc.create_mappings_from_source(self.ctxt, gabc)
        
        # Should be 2 mappings: one for Clef, one for Note
        self.assertEqual(len(mappings), 2)
        
        # Check Clef
        clef = mappings[0].notations[0]
        self.assertIsInstance(clef, DoClef)
        self.assertEqual(clef.staff_position, 3)
        
        # Check Note
        note_mapping = mappings[1]
        self.assertEqual(len(note_mapping.notations), 1)
        # Punctum is a Neume
        punctum = note_mapping.notations[0]
        self.assertTrue(punctum.is_neume)
        self.assertEqual(len(punctum.notes), 1)
        # (f) in c4 -> f is 3 steps below c4(3) ? 
        # Wait, c4 means Do is at 3.
        # f in GABC is ... wait, let's check parse logic
        # Gabc.gabc_height_to_exsurge_height('f') -> 'f' - 'g' = -1
        # c4 DoClef: pitchToStaffPosition(Do) = 3
        # No, the gabc parser sets staff_position directly on the note based on gabc char.
        # 'f' -> -1.
        # Then, if clef is present, it calculates pitch.
        # clef.staff_position_to_pitch(-1)
        # DoClef(3, 2).
        # Offset = -1 - 3 = -4.
        # -4 steps from Do.
        # Do, Ti, La, So, Fa.
        # So it should be Fa.
        
        note = punctum.notes[0]
        self.assertEqual(note.staff_position, -1)
        # Verify pitch
        self.assertEqual(note.pitch.step, Step.Fa)

    def test_lyrics(self):
        gabc = "(c4) A(f)men(fg)"
        mappings = Gabc.create_mappings_from_source(self.ctxt, gabc)
        
        # Word 1: (c4)
        # Word 2: A(f)
        # Word 3: men(fg)
        
        self.assertEqual(mappings[1].source, "A(f)")
        lyric_note = mappings[1].notations[0]
        self.assertTrue(hasattr(lyric_note, 'lyrics'))
        self.assertEqual(lyric_note.lyrics[0].text, "A")
        
        self.assertEqual(mappings[2].source, "men(fg)")
        lyric_neume = mappings[2].notations[0] # Podatus
        self.assertEqual(lyric_neume.lyrics[0].text, "men")

    def test_complex_neume(self):
        # (fgh) -> Scandicus
        # My simple parser currently does:
        # f, g -> Podatus
        # h -> Punctum? 
        # Or Podatus + Punctum.
        # JS logic: Scandicus state machine.
        # My Python logic: iterate. 
        # f, g -> Podatus (f < g). Index advances.
        # Next is h. Remaining: h. -> Punctum.
        # So we expect [Podatus, Punctum].
        
        gabc = "(c4) (fgh)"
        mappings = Gabc.create_mappings_from_source(self.ctxt, gabc)
        neumes = mappings[1].notations
        self.assertEqual(len(neumes), 2)
        self.assertEqual(neumes[0].__class__.__name__, 'Podatus')
        self.assertEqual(neumes[1].__class__.__name__, 'Punctum')

if __name__ == '__main__':
    unittest.main()
