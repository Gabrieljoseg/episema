import unittest
from episema.chant import DoClef, FaClef, Note
from episema.core import Pitch, Step

class TestChant(unittest.TestCase):

    def test_do_clef(self):
        # Do Clef on line 3 (c4)
        c4 = DoClef(3, 2) # Staff pos 3, Octave 2
        
        # Middle C (Do, Octave 2) should be at position 3
        pitch_do = Pitch(Step.Do, 2)
        self.assertEqual(c4.pitch_to_staff_position(pitch_do), 3)
        
        # Re, Octave 2 should be at 4 (Do=3 -> Re=3+1=4 because StepToStaffOffset: Do=0, Re=1)
        pitch_re = Pitch(Step.Re, 2)
        self.assertEqual(c4.pitch_to_staff_position(pitch_re), 4)
        
        # Check reverse
        p = c4.staff_position_to_pitch(3)
        self.assertEqual(p.step, Step.Do)
        self.assertEqual(p.octave, 2)

    def test_fa_clef(self):
        # Fa Clef on line 3 (f4)
        f4 = FaClef(3, 2)
        
        # Fa, Octave 2 should be at position 3
        pitch_fa = Pitch(Step.Fa, 2)
        self.assertEqual(f4.pitch_to_staff_position(pitch_fa), 3)
        
        # Check reverse
        p = f4.staff_position_to_pitch(3)
        self.assertEqual(p.step, Step.Fa)
        self.assertEqual(p.octave, 2)

    def test_note(self):
        n = Note(Pitch(Step.Do, 1))
        self.assertEqual(n.pitch.step, Step.Do)
        self.assertEqual(n.pitch.octave, 1)

if __name__ == '__main__':
    unittest.main()
