import math
from enum import IntEnum, auto
from typing import Union, Optional

# Units

class Units(IntEnum):
    DeviceIndependent = 0  # device independent units: 96/inch
    Centimeters = 1
    Millimeters = 2
    Inches = 3

DIU_PER_INCH = 96
DIU_PER_CENTIMETER = 96 / 2.54

def to_device_independent(n: float, input_units: Units) -> float:
    if input_units == Units.Centimeters:
        return n * DIU_PER_CENTIMETER
    elif input_units == Units.Millimeters:
        return n * DIU_PER_CENTIMETER / 10
    elif input_units == Units.Inches:
        return n * DIU_PER_INCH
    else:
        return n

def from_device_independent(n: float, output_units: Units) -> float:
    if output_units == Units.Centimeters:
        return n / DIU_PER_CENTIMETER
    elif output_units == Units.Millimeters:
        return n / DIU_PER_CENTIMETER * 10
    elif output_units == Units.Inches:
        return n / DIU_PER_INCH
    else:
        return n

# Helper functions for unit conversion (acting as constructors/converters)
def device_independent(n: float) -> float:
    return n

def centimeters(n: float) -> float:
    return to_device_independent(n, Units.Centimeters)

def millimeters(n: float) -> float:
    return to_device_independent(n, Units.Millimeters)

def inches(n: float) -> float:
    return to_device_independent(n, Units.Inches)

def to_centimeters(n: float) -> float:
    return from_device_independent(n, Units.Centimeters)

def to_millimeters(n: float) -> float:
    return from_device_independent(n, Units.Millimeters)

def to_inches(n: float) -> float:
    return from_device_independent(n, Units.Inches)


# Point

class Point:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def clone(self) -> 'Point':
        return Point(self.x, self.y)

    def equals(self, point: 'Point') -> bool:
        return self.x == point.x and self.y == point.y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.equals(other)
        return False

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"


# Rect

class Rect:
    def __init__(self, x: float = float('inf'), y: float = float('inf'), 
                 width: float = float('-inf'), height: float = float('-inf')):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def clone(self) -> 'Rect':
        return Rect(self.x, self.y, self.width, self.height)

    def is_empty(self) -> bool:
        return (self.x == float('inf') and
                self.y == float('inf') and
                self.width == float('-inf') and
                self.height == float('-inf'))

    def right(self) -> float:
        return self.x + self.width

    def bottom(self) -> float:
        return self.y + self.height

    def equals(self, rect: 'Rect') -> bool:
        return (self.x == rect.x and self.y == rect.y and
                self.width == rect.width and self.height == rect.height)

    def __eq__(self, other):
        if isinstance(other, Rect):
            return self.equals(other)
        return False

    def contains(self, other: Union[Point, 'Rect']) -> bool:
        if isinstance(other, Point):
            return (other.x >= self.x and
                    other.x <= self.x + self.width and
                    other.y >= self.y and
                    other.y <= self.y + self.height)
        elif isinstance(other, Rect):
            return (self.x <= other.x and
                    self.x + self.width >= other.x + other.width and
                    self.y <= other.y and
                    self.y + self.height >= other.y + other.height)
        return False

    def union(self, rect: 'Rect') -> None:
        # If this rect is empty/undefined (default), just copy the other rect
        if self.is_empty():
            self.x = rect.x
            self.y = rect.y
            self.width = rect.width
            self.height = rect.height
            return

        # If the other rect is empty, do nothing
        if rect.is_empty():
            return

        right = max(self.x + self.width, rect.x + rect.width)
        bottom = max(self.y + self.height, rect.y + rect.height)

        self.x = min(self.x, rect.x)
        self.y = min(self.y, rect.y)

        self.width = right - self.x
        self.height = bottom - self.y

    def __repr__(self):
        return f"Rect(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


# Margins

class Margins:
    def __init__(self, left: float = 0, top: float = 0, right: float = 0, bottom: float = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def clone(self) -> 'Margins':
        return Margins(self.left, self.top, self.right, self.bottom)

    def equals(self, margins: 'Margins') -> bool:
        return (self.left == margins.left and
                self.top == margins.top and
                self.right == margins.right and
                self.bottom == margins.bottom)

    def __eq__(self, other):
        if isinstance(other, Margins):
            return self.equals(other)
        return False
    
    def __repr__(self):
        return f"Margins(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom})"


# Size

class Size:
    def __init__(self, width: float = 0, height: float = 0):
        self.width = width
        self.height = height

    def clone(self) -> 'Size':
        return Size(self.width, self.height)

    def equals(self, size: 'Size') -> bool:
        return self.width == size.width and self.height == size.height

    def __eq__(self, other):
        if isinstance(other, Size):
            return self.equals(other)
        return False

    def __repr__(self):
        return f"Size(width={self.width}, height={self.height})"


# Pitch and Step

class Step(IntEnum):
    Do = 0
    Du = 1
    Re = 2
    Me = 3
    Mi = 4
    Fa = 5
    Fu = 6
    So = 7
    La = 9
    Te = 10
    Ti = 11

# Maps steps to an incremental position the steps take on the staff line.
_StepToStaffPosition = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 6, 6]
_StaffOffsetToStep = [Step.Do, Step.Re, Step.Mi, Step.Fa, Step.So, Step.La, Step.Ti]

class Pitch:
    def __init__(self, step: Step, octave: int):
        self.step = step
        self.octave = octave

    def to_int(self) -> int:
        return self.octave * 12 + self.step

    def is_higher_than(self, pitch: 'Pitch') -> bool:
        return self.to_int() > pitch.to_int()

    def is_lower_than(self, pitch: 'Pitch') -> bool:
        return self.to_int() < pitch.to_int()

    def equals(self, pitch: 'Pitch') -> bool:
        return self.to_int() == pitch.to_int()

    def __eq__(self, other):
        if isinstance(other, Pitch):
            return self.equals(other)
        return False

    @staticmethod
    def step_to_staff_offset(step: int) -> int:
        # handle IntEnum or int value
        return _StepToStaffPosition[step]

    @staticmethod
    def staff_offset_to_step(offset: int) -> Step:
        while offset < 0:
            offset = len(_StaffOffsetToStep) + offset
        
        return _StaffOffsetToStep[offset % len(_StaffOffsetToStep)]

    def __repr__(self):
        return f"Pitch(step={self.step}, octave={self.octave})"
