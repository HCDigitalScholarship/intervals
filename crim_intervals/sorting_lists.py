# variable orders.  These include the full chromatic range of possibilities

pitch_order = ['Rest','C2', 'D2', 'E-2', 'E2', 'F2', 'F#2', 'G-2', 'G2', 'G#2', 'A-2', 'A2', 'A#2','B-2', 'B2',
    'C3', 'C#3', 'D-3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3', 'G-3',  'G3', 'G#3', 'A-3', 'A3', 'A#3', 'B-3','B3', 'B#3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4', 'A#4', 'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5', 'A#5', 'B-5', 'B5',
    'C6']

recta_order = ['Rest','D2', 'E-2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'B-2', 'B2',
    'C3', 'C#3','D3', 'D#3', 'E-3','E3', 'F3', 'F#3',  'G3', 'G#3', 'A-3', 'A3', 'B-3','B3',
    'C4', 'C#4', 'D-4','D4', 'D#4','E-4', 'E4', 'F4', 'F#4', 'G-4',  'G4', 'G#4', 'A-4','A4',  'B-4', 'B4',
    'C5', 'C#5','D-5','D5', 'D#5', 'E-5','E5','F5', 'F#5', 'G-5', 'G5', 'G#5', 'A-5', 'A5',  'B-5', 'B5',
    'C6']


pitch_class_order = ['C', 'C#', 'D-','D', 'D#', 'E-', 'E', 'E#', 'F', 'F#', 'G-', 'G', 'G#', 'A-','A', 'A#', 'B-', 'B', 'Rest']

# Function to standardize note names
def standardize_note(note):
   
    if '-' in note:
        return note.replace('-', 'b')
    return note