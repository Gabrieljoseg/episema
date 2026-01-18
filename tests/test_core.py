import unittest
from episema.core import Point, Rect, Size, Margins, Pitch, Step, Units, to_centimeters, to_inches

class TestCore(unittest.TestCase):

    def test_point(self):
        p1 = Point(10, 20)
        p2 = Point(10, 20)
        p3 = Point(5, 5)

        self.assertEqual(p1.x, 10)
        self.assertEqual(p1.y, 20)
        self.assertTrue(p1.equals(p2))
        self.assertFalse(p1.equals(p3))
        
        p_clone = p1.clone()
        self.assertTrue(p1.equals(p_clone))
        self.assertIsNot(p1, p_clone)

    def test_rect(self):
        r1 = Rect(0, 0, 100, 50)
        r2 = Rect(0, 0, 100, 50)
        
        self.assertEqual(r1.right(), 100)
        self.assertEqual(r1.bottom(), 50)
        self.assertTrue(r1.equals(r2))
        
        p_inside = Point(50, 25)
        p_outside = Point(150, 25)
        
        self.assertTrue(r1.contains(p_inside))
        self.assertFalse(r1.contains(p_outside))
        
        r_union = Rect(0, 0, 10, 10)
        r_union.union(Rect(10, 10, 10, 10))
        # Expected: x=0, y=0, w=20, h=20
        self.assertEqual(r_union.x, 0)
        self.assertEqual(r_union.y, 0)
        self.assertEqual(r_union.width, 20)
        self.assertEqual(r_union.height, 20)

    def test_pitch(self):
        p1 = Pitch(Step.Do, 1)
        p2 = Pitch(Step.Re, 1)
        p3 = Pitch(Step.Do, 2)
        
        self.assertTrue(p2.is_higher_than(p1))
        self.assertTrue(p3.is_higher_than(p2))
        self.assertEqual(p1.to_int(), 12) # 1 * 12 + 0
        
        # Staff offset test
        # Do -> 0
        # Re -> 1
        self.assertEqual(Pitch.step_to_staff_offset(Step.Do), 0)
        self.assertEqual(Pitch.step_to_staff_offset(Step.Re), 1)
        
    def test_units(self):
        val = 1.0 # 1 cm
        # 1 cm = 96/2.54 DIU
        diu = to_centimeters(val) # Wait, my helper wrapper is confusing. 
        # core.py: to_centimeters invokes FromDeviceIndependent.
        # If input is 1 DIU, output is 1/96 * 2.54 cm.
        
        # Let's check Units conversion constants
        # 1 inch = 96 DIU
        # to_inches(96) should be 1
        self.assertAlmostEqual(to_inches(96), 1.0)
        
if __name__ == '__main__':
    unittest.main()
