import zlib
from xml.etree import ElementTree
from midiutil.MidiFile import MIDIFile


def get_xml(filename):
    contents = open(filename, "rb").read()
    xml = zlib.decompress(contents[4:])
    return xml.strip()

def get_root(filename):
    return ElementTree.fromstring(get_xml(filename))

def get_instrument_count(element):
    count = 0
    for _ in element.iter("instrument"):
        count += 1
    return count

def add_notes_from_pattern(midifile, pattern, track=0, time=0):
    time += int(pattern.get("pos"))
    for note in pattern.iter("note"):
        midifile.addNote(
            track=track,
            channel=track,
            pitch=int(note.get("key")),
            time=(time + int(note.get("pos"))) / 48.0,
            duration=int(note.get("len")) / 48.0,
            volume=int(note.get("vol"))
        )

def convert_mmpz_to_midi(infile, outfile):
    root = get_root(infile)
    midifile = MIDIFile(get_instrument_count(root))

    track_id = 0
    for track in root.find("song").find("trackcontainer"):
        if track.get("type") == "0":
            # Main instrument
            for pattern in track.iterfind("pattern"):
                add_notes_from_pattern(midifile, pattern, track=track_id)
            track_id += 1
        else:
            # Beat/Bassline
            pass # TODO

    midifile.writeFile(open(outfile, "wb"))
