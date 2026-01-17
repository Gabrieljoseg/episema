from enum import IntEnum, IntFlag, auto
from typing import List, Optional, Any, Union
import math
from .core import Pitch, Step, Rect, Point, Size, Units

# Enums

class LiquescentType(IntFlag):
    None_ = 0
    Large = 1 << 0
    Small = 1 << 1
    Ascending = 1 << 2
    Descending = 1 << 3
    InitioDebilis = 1 << 4
    
    # Common combinations
    LargeAscending = (1 << 0) | (1 << 2)
    LargeDescending = (1 << 0) | (1 << 3)
    SmallAscending = (1 << 1) | (1 << 2)
    SmallDescending = (1 << 1) | (1 << 3)

class NoteShape(IntEnum):
    Default = 0
    Virga = 1
    Inclinatum = 2
    Quilisma = 3
    Stropha = 4
    Oriscus = 5

class NoteShapeModifiers(IntFlag):
    None_ = 0
    Ascending = 1 << 0
    Descending = 1 << 1
    Cavum = 1 << 2
    Stemmed = 1 << 3

class AccidentalType(IntEnum):
    Flat = -1
    Natural = 0
    Sharp = 1

# Base Classes

class ChantLayoutElement:
    def __init__(self):
        self.bounds = Rect()
        self.origin = Point()

    def perform_layout(self, ctxt):
        pass

    def draw(self, ctxt):
        pass

    def create_svg_fragment(self, ctxt):
        return ""

class ChantNotationElement(ChantLayoutElement):
    def __init__(self):
        super().__init__()
        self.is_clef = False
        self.is_accidental = False
        self.is_neume = False
        self.resets_accidentals = False
        
        self.visualizers = [] # To store visual components
        
        # properties from JS implementation that might be needed
        self.trailing_space = 0.0
        self.keep_with_next = False
        self.needs_layout = True

    def add_visualizer(self, visualizer):
        self.visualizers.append(visualizer)

    def perform_layout(self, ctxt):
        super().perform_layout(ctxt)
        # Basic layout logic stub
        pass
    
    def finish_layout(self, ctxt):
        # Update bounds based on visualizers
        pass
        
    def has_lyrics(self):
        return hasattr(self, 'lyrics') and self.lyrics and len(self.lyrics) > 0


# Note Class

class Note(ChantLayoutElement):
    def __init__(self, pitch: Optional[Pitch] = None):
        super().__init__()
        
        self.pitch = pitch
        self.staff_position = 0
        self.liquescent = LiquescentType.None_
        self.shape = NoteShape.Default
        self.shape_modifiers = NoteShapeModifiers.None_
        
        self.neume = None
        
        self.epismata = []
        self.morae = []
        
        self.glyph_visualizer = None


# Clef Classes

class Clef(ChantNotationElement):
    def __init__(self, staff_position: int, octave: int, default_accidental: Any = None):
        super().__init__()
        self.is_clef = True
        self.staff_position = staff_position
        self.octave = octave
        self.default_accidental = default_accidental
        self.active_accidental = default_accidental
        self.leading_space = 0.0

    def reset_accidentals(self):
        self.active_accidental = self.default_accidental

    def pitch_to_staff_position(self, pitch: Pitch) -> int:
        raise NotImplementedError("Subclasses must implement pitch_to_staff_position")

    def staff_position_to_pitch(self, staff_position: int) -> Pitch:
        raise NotImplementedError("Subclasses must implement staff_position_to_pitch")

    @staticmethod
    def default():
        return _default_do_clef

class DoClef(Clef):
    def __init__(self, staff_position: int, octave: int, default_accidental: Any = None):
        super().__init__(staff_position, octave, default_accidental)

    def pitch_to_staff_position(self, pitch: Pitch) -> int:
        return (pitch.octave - self.octave) * 7 + self.staff_position + \
               Pitch.step_to_staff_offset(pitch.step) - \
               Pitch.step_to_staff_offset(Step.Do)

    def staff_position_to_pitch(self, staff_position: int) -> Pitch:
        offset = staff_position - self.staff_position
        octave_offset = math.floor(offset / 7)
        
        step = Pitch.staff_offset_to_step(offset)
        
        # Handle default accidental if implemented (stub for now)
        # if self.default_accidental and step == self.default_accidental.step:
        #     pass

        return Pitch(step, self.octave + octave_offset)

    def clone(self):
        return DoClef(self.staff_position, self.octave, self.default_accidental)

class FaClef(Clef):
    def __init__(self, staff_position: int, octave: int, default_accidental: Any = None):
        super().__init__(staff_position, octave, default_accidental)

    def pitch_to_staff_position(self, pitch: Pitch) -> int:
        return (pitch.octave - self.octave) * 7 + self.staff_position + \
               Pitch.step_to_staff_offset(pitch.step) - \
               Pitch.step_to_staff_offset(Step.Fa)

    def staff_position_to_pitch(self, staff_position: int) -> Pitch:
        offset = staff_position - self.staff_position + 3 # + 3 because it's a fa clef
        octave_offset = math.floor(offset / 7)
        
        step = Pitch.staff_offset_to_step(offset)
        
        if step == Step.Ti and self.default_accidental == AccidentalType.Flat:
            step = Step.Te
            
        return Pitch(step, self.octave + octave_offset)

    def clone(self):
        return FaClef(self.staff_position, self.octave, self.default_accidental)

_default_do_clef = DoClef(1, 2)


# Other Elements

class TextOnly(ChantNotationElement):
    def __init__(self):
        super().__init__()

class ChantLineBreak(ChantNotationElement):
    def __init__(self, justify: bool = False):
        super().__init__()
        self.justify = justify
        
    def clone(self):
        return ChantLineBreak(self.justify)
        
    def perform_layout(self, ctxt):
        self.bounds = Rect(0, 0, 0, 0)


# Document Structure

class ChantMapping:
    def __init__(self, source: Any, notations: List[ChantNotationElement]):
        self.source = source
        self.notations = notations

class ChantScore:
    def __init__(self, ctxt: Any = None, mappings: List[ChantMapping] = None, use_drop_cap: bool = True):
        self.mappings = mappings if mappings is not None else []
        self.lines = []
        self.notes = []
        
        self.starting_clef = None
        
        self.use_drop_cap = use_drop_cap
        self.drop_cap = None
        self.annotation = None
        
        self.compiled = False
        self.auto_coloring = True
        self.needs_layout = True
        
        self.bounds = Rect()
        
        if ctxt:
            self.update_notations(ctxt)

    def update_notations(self, ctxt):
        self.notations = []
        for mapping in self.mappings:
            self.notations.extend(mapping.notations)
            
        # Find starting clef
        self.starting_clef = None
        default_clef = DoClef(1, 2)
        
        for i, notation in enumerate(self.notations):
            if notation.is_neume:
                self.starting_clef = default_clef
                break
            
            if notation.is_active_clef if hasattr(notation, 'is_active_clef') else getattr(notation, 'is_clef', False):
                 # Note: in JS it checks .isClef. 
                 self.starting_clef = notation
                 self.notations.pop(i) # Remove it from notations list? JS does splice(i, 1)
                 break
                 
        if not self.starting_clef:
            self.starting_clef = default_clef
            
        # drop cap logic stub
        self.needs_layout = True

    def perform_layout(self, ctxt):
        if not self.needs_layout:
            return
            
        ctxt.active_clef = self.starting_clef
        ctxt.notations = self.notations
        ctxt.curr_notation_index = 0
        
        # ... layout loop ...
        for i, notation in enumerate(self.notations):
             notation.perform_layout(ctxt)
             ctxt.curr_notation_index += 1
             
        self.needs_layout = False

class ChantDocument:
    def __init__(self):
        self.layout = {
            "units": "mm",
            "default-font": {
                "font-family": "Crimson",
                "font-size": 14
            },
            "page": {
                "width": 8.5,
                "height": 11,
                "margin-left": 0,
                "margin-top": 0,
                "margin-right": 0,
                "margin-bottom": 0
            }
        }
        self.scores = []

