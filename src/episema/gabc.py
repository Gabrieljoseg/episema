import re
from typing import List, Optional, Any, Tuple
from enum import IntEnum

from .core import Pitch, Step, Rect, Point
from .chant import Note, NoteShape, NoteShapeModifiers, LiquescentType, ChantMapping, ChantLineBreak, DoClef, FaClef, TextOnly, Clef, ChantNotationElement
from .signs import Accidental, Custos, QuarterBar, HalfBar, FullBar, DoubleBar, Virgula, AccidentalType
from .neumes import *

# Regex patterns
# Note: JS Regex might use slightly different syntax.
# __syllablesRegex = /(?=.)((?:[^(])*)(?:\(?([^)]*)\)?)?/g;
# Python translate:
# (?=.) -> Lookahead to ensure not empty?
# ((?:[^(])*) -> Capture group 1: Lyrics (chars that are not '(')
# (?:\(?([^)]*)\)?)? -> Optional group handling notation in parens.
#   \(? -> optional '('
#   ([^)]*) -> Capture group 2: Notation data
#   \)? -> optional ')'
SYLLABLES_REGEX = re.compile(r"(?=.)((?:[^(])*?)(?:\(?([^)]*?)\)?)?(?=$|\(|\s)", re.MULTILINE) 
# Note: The JS regex relies on global matching /g to iterate. In Python we use finditer.
# The JS regex `((?:[^(])*)` matches greedy until `(`.
# I'll use a slightly more robust pattern for Python: 
# Split by `(` then process? Or just iterate.
# Let's try to match the JS behavior: "word(notation)" -> match 1="word", match 2="notation".
SYLLABLES_REGEX_PYTHON = re.compile(r"([^(]*)(?:\(([^)]*)\))?")

# __notationsRegex = /z0|z|Z|::|:|;|,|`|c1|c2|c3|c4|f3|f4|cb3|cb4|\/\/|\/| |\!|-?[a-mA-M][oOwWvVrRsxy#~\+><_\.'012345]*(?:\[[^\]]*\]?)*/g;
NOTATIONS_REGEX = re.compile(r"z0|z|Z|::|:|;|,|`|c1|c2|c3|c4|f3|f4|cb3|cb4|//|/| |\!|-?[a-mA-M][oOwWvVrRsxy#~\+><_\.'012345]*(?:\[[^\]]*\]?)*")

class LyricType(IntEnum):
    SingleSyllable = 0
    BeginningSyllable = 1
    MiddleSyllable = 2
    EndingSyllable = 3
    Directive = 4

class Lyric:
    def __init__(self, ctxt, text: str, lyric_type: LyricType):
        self.text = text
        self.lyric_type = lyric_type
        self.elides_to_next = False
        self.center_start_index = -1
        self.center_length = 0

class Gabc:

    @staticmethod
    def split_words(source: str) -> List[str]:
        # Simple whitespace split for now
        return source.strip().split()

    @staticmethod
    def create_mappings_from_source(ctxt, gabc_source: str) -> List[ChantMapping]:
        words = Gabc.split_words(gabc_source)
        
        # Default clef
        ctxt.active_clef = Clef.default()
        
        mappings = []
        for word in words:
            if not word.strip():
                continue
            mapping = Gabc.create_mapping_from_word(ctxt, word)
            if mapping:
                mappings.append(mapping)
                
        # Handle trailing space of last notation logic if needed
        if mappings and mappings[-1].notations:
             mappings[-1].notations[-1].trailing_space = 0
             
        return mappings

    @staticmethod
    def create_mapping_from_word(ctxt, word: str) -> ChantMapping:
        notations = []
        curr_syllable = 0
        
        # In JS: while ((match = __syllablesRegex.exec(word)))
        # Python finditer is good.
        # But look at the regex: `((?:[^(])*)` matches ANY non-open-paren characters.
        # If the word is "Spiritus(fg)", match 1 is "Spiritus", match 2 is "fg".
        
        # Custom parsing loop to allow for complex cases might be better, but let's try regex.
        matches = list(SYLLABLES_REGEX_PYTHON.finditer(word))
        
        # Filter empty matches if any
        matches = [m for m in matches if m.group(0)]
        
        # If no matches found but word exists (and doesn't contain parens?), treat as lyric?
        # Actually the regex is greedy. "Spiritus" matches group 1 "Spiritus", group 2 None.
        
        for j, match in enumerate(matches):
            lyric_text = match.group(1).strip() if match.group(1) else ""
            notation_data = match.group(2) if match.group(2) else ""
            
            items = Gabc.parse_notations(ctxt, notation_data)
            
            if not items:
                # If no notations, maybe it's just text?
                if not notation_data and lyric_text:
                    # Logic in JS assumes items can be empty if notationData is empty/None
                    pass
                else: 
                     continue

            notations.extend(items)
            
            if not lyric_text:
                continue
                
            # Add lyrics to the first notation that makes sense
            notation_with_lyrics = None
            for item in items:
                if item.is_accidental or isinstance(item, Custos):
                    continue
                notation_with_lyrics = item
                break
                
            if notation_with_lyrics is None:
                # If we couldn't find a note to attach lyrics to, return what we have? behavior in JS
                return ChantMapping(word, notations)

            # Determine lyric type
            proposed_lyric_type = LyricType.SingleSyllable
            
            if not getattr(notation_with_lyrics, 'is_neume', False) and not isinstance(notation_with_lyrics, TextOnly):
                proposed_lyric_type = LyricType.Directive
            elif curr_syllable == 0 and j == (len(matches) - 1):
                proposed_lyric_type = LyricType.SingleSyllable
            elif curr_syllable == 0 and j < (len(matches) - 1):
                proposed_lyric_type = LyricType.BeginningSyllable
            elif j == (len(matches) - 1):
                proposed_lyric_type = LyricType.EndingSyllable
            else:
                proposed_lyric_type = LyricType.MiddleSyllable
                
            curr_syllable += 1
            
            if proposed_lyric_type in (LyricType.BeginningSyllable, LyricType.SingleSyllable):
                 ctxt.active_clef.reset_accidentals()
                 
            lyrics = Gabc.create_syllable_lyrics(ctxt, lyric_text, proposed_lyric_type)
            
            if lyrics:
                notation_with_lyrics.lyrics = lyrics
                
        return ChantMapping(word, notations)

    @staticmethod
    def create_syllable_lyrics(ctxt, text: str, proposed_lyric_type: LyricType) -> List[Lyric]:
        lyrics = []
        lyric_texts = text.split('|')
        
        for lyric_text in lyric_texts:
            center_start_index = lyric_text.find('{')
            center_length = 0
            
            if center_start_index >= 0:
                index_closing_bracket = lyric_text.find('}')
                if index_closing_bracket >= 0 and index_closing_bracket > center_start_index:
                    center_length = index_closing_bracket - center_start_index - 1
                    # Strip brackets
                    lyric_text = lyric_text[:center_start_index] + lyric_text[center_start_index+1:index_closing_bracket] + lyric_text[index_closing_bracket+1:]
                else:
                    center_start_index = -1
                    
            lyric = Gabc.make_lyric(ctxt, lyric_text, proposed_lyric_type)
            
            if center_start_index >= 0:
               lyric.center_start_index = center_start_index
               lyric.center_length = center_length
               
            lyrics.append(lyric)
            
        return lyrics

    @staticmethod
    def make_lyric(ctxt, text, lyric_type):
        if len(text) > 1 and text.endswith('-'):
            if lyric_type == LyricType.EndingSyllable:
                lyric_type = LyricType.MiddleSyllable
            elif lyric_type == LyricType.SingleSyllable:
                lyric_type = LyricType.BeginningSyllable
            text = text[:-1]
            
        elides = False
        if len(text) > 1 and text.endswith('_'):
            elides = True
            text = text[:-1]
            
        if text == "*" or text == "†":
            lyric_type = LyricType.Directive
            
        lyric = Lyric(ctxt, text, lyric_type)
        lyric.elides_to_next = elides
        return lyric

    @staticmethod
    def parse_notations(ctxt, data: str) -> List[Any]:
        if not data:
            return [TextOnly()]
            
        notations = []
        notes = []
        trailing_space = -1
        
        def add_notation(notation):
            nonlocal trailing_space, notes
            # process leftover notes into neume
            if notes:
                 neumes = Gabc.create_neumes_from_notes(ctxt, notes, trailing_space)
                 for neume in neumes:
                     notations.append(neume)
                 
                 trailing_space = -1
                 notes = [] # reset list reference
            
            if notation:
                 if getattr(notation, 'is_clef', False):
                     ctxt.active_clef = notation
                 elif getattr(notation, 'is_accidental', False):
                     ctxt.active_clef.active_accidental = notation
                 elif getattr(notation, 'resets_accidentals', False):
                     ctxt.active_clef.reset_accidentals()
                     
                 notations.append(notation)

        atoms = NOTATIONS_REGEX.findall(data)
        
        for atom in atoms:
            if atom == ",":
                add_notation(QuarterBar())
            elif atom == "`":
                add_notation(Virgula())
            elif atom == ";":
                add_notation(HalfBar())
            elif atom == ":":
                add_notation(FullBar())
            elif atom == "::":
                 add_notation(DoubleBar())
            elif atom == "c1":
                 add_notation(DoClef(-3, 2))
            elif atom == "c2":
                 add_notation(DoClef(-1, 2))
            elif atom == "c3":
                 add_notation(DoClef(1, 2))
            elif atom == "c4":
                 add_notation(DoClef(3, 2))
            elif atom == "f3":
                 add_notation(FaClef(1, 2))
            elif atom == "f4":
                 add_notation(FaClef(3, 2))
            elif atom == "cb3":
                 add_notation(DoClef(1, 2, Accidental(0, AccidentalType.Flat)))
            elif atom == "cb4":
                 add_notation(DoClef(3, 2, Accidental(2, AccidentalType.Flat)))
            elif atom == "z":
                 add_notation(ChantLineBreak(True))
            elif atom == "Z":
                 add_notation(ChantLineBreak(False))
            elif atom == "z0":
                 add_notation(Custos(True))
            elif atom == "!":
                 trailing_space = 0
                 add_notation(None)
            elif atom == "/":
                 # trailing_space = ctxt.intra_neume_spacing
                 add_notation(None)
            elif atom == "//":
                 # trailing_space = ctxt.intra_neume_spacing * 2
                 add_notation(None)
            elif atom == " ":
                 add_notation(None)
            else:
                # Custos, Accidental, or Note
                if len(atom) > 1 and atom[1] == '+':
                    custos = Custos()
                    custos.staff_position = Gabc.gabc_height_to_exsurge_height(atom[0])
                    add_notation(custos)
                elif len(atom) > 1 and atom[1] in ('x', 'y', '#'):
                    atype = AccidentalType.Flat
                    if atom[1] == 'y': atype = AccidentalType.Natural
                    elif atom[1] == '#': atype = AccidentalType.Sharp
                    
                    # Need to parse the note to get position
                    note_arr = []
                    Gabc.create_note_from_data(ctxt, ctxt.active_clef, atom, note_arr) # Helper needed
                    accidental = Accidental(note_arr[0].staff_position, atype)
                    ctxt.active_clef.active_accidental = accidental
                    add_notation(accidental)
                else:
                    Gabc.create_note_from_data(ctxt, ctxt.active_clef, atom, notes) # Helper needed

        add_notation(None)
        return notations

    @staticmethod
    def gabc_height_to_exsurge_height(char_code: str):
        # gabc: a=0, b=1 ... m=12 (approx)
        # exsurge: 0 is center line?
        # Exsurge Core.js comment: 0 is center space (gabc 'g').
        # a -> -6, b -> -5 .. g -> 0 .. m -> 6
        code = ord(char_code.lower())
        g_code = ord('g')
        return code - g_code

    @staticmethod
    def create_note_from_data(ctxt, clef, atom, notes_list):
        # Simplistic parser for now, similar to JS
        # atom[0] is pitch
        pitch_char = atom[0]
        staff_pos = Gabc.gabc_height_to_exsurge_height(pitch_char)
        
        # Calculate pitch from staff position using clef
        # Note: In pure data model, we might just store staff_pos, but Note() takes pitch?
        # JS Note takes Pitch.
        # Clef has staffPositionToPitch.
        if clef:
             pitch = clef.staff_position_to_pitch(staff_pos)
        else:
             pitch = Pitch(Step.Do, 0) # Fallback

        note = Note(pitch)
        note.staff_position = staff_pos
        
        # Parse shape modifiers in atom
        # e.g. 'v', 'r', 's'
        if 'v' in atom:
             note.shape = NoteShape.Virga
        elif 'r' in atom:
             note.shape = NoteShape.Inclinatum
        elif 's' in atom:
             note.shape = NoteShape.Stropha
        elif 'w' in atom:
             note.shape = NoteShape.Quilisma
        elif 'o' in atom:
             note.shape = NoteShape.Oriscus
             
        # Add to list
        notes_list.append(note)


    @staticmethod
    def create_neumes_from_notes(ctxt, notes, final_trailing_space):
        if not notes:
            return []
            
        neumes = []
        first_note_index = 0
        curr_note_index = 0
        
        # Determine State
        # Very simplified FSM logic for porting
        
        while first_note_index < len(notes):
             # Just create simple neumes for now (Punctum mostly) to test structure
             # Implementing full FSM is huge.
             # I'll implement basic grouping:
             # If Virga -> Virga
             
             note = notes[first_note_index]
             neume = None
             
             if note.shape == NoteShape.Virga:
                 neume = Virga([note])
             elif note.shape == NoteShape.Inclinatum:
                 neume = PunctaInclinata([note])
             elif note.shape == NoteShape.Stropha:
                 neume = Apostropha([note])
             elif note.shape == NoteShape.Oriscus:
                  neume = Oriscus([note])
             # Need to handle Podatus etc (multiple notes)
             elif first_note_index + 1 < len(notes):
                  # Check for Podatus
                  next_note = notes[first_note_index+1]
                  if next_note.staff_position > note.staff_position and next_note.shape == NoteShape.Default:
                      neume = Podatus([note, next_note])
                      first_note_index += 1
                  elif next_note.staff_position < note.staff_position and next_note.shape == NoteShape.Default:
                      neume = Clivis([note, next_note])
                      first_note_index += 1
                  else:
                      neume = Punctum([note])
             else:
                 neume = Punctum([note])
                 
             if neume:
                 neumes.append(neume)
                 
             first_note_index += 1
             
        # Apply trailing space to last neume
        if neumes:
             neumes[-1].trailing_space = final_trailing_space
             
        return neumes
