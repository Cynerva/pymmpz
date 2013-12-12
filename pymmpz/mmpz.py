import zlib
from xml.etree import ElementTree
from pyknon.MidiFile import MIDIFile


def get_xml(filename):
    contents = open(filename, "rb").read()
    xml = zlib.decompress(contents[4:])
    return xml.strip()


def get_root(filename):
    return ElementTree.fromstring(get_xml(filename))


def get_starting_tempo(root):
    head = root.find("head")
    try:
        return float(head.get("bpm"))
    except TypeError:
        # Some versions of mmpz have BPM as an element, not an attrib.
        return float(head.find("bpm").get("value"))


def get_instrument_count(element):
    count = 0
    for _ in element.iter("instrument"):
        count += 1
    return count


def add_notes_from_pattern(midifile, pattern, track=0, time=0):
    # 16 channels to choose from, but channel 9 is percussion, so skip it
    channel = track % 15
    if channel >= 9:
        channel += 1

    time += int(pattern.get("pos"))
    for note in pattern.iterfind("note"):
        midifile.addNote(
            track=track,
            channel=channel,
            pitch=int(note.get("key")) + 12,
            time=(time + int(note.get("pos"))) / 48.0,
            duration=int(note.get("len")) / 48.0,
            volume=int(note.get("vol"))
        )


def add_tempo_events_from_track(midifile, track):
    for pattern in track.iterfind("automationpattern"):
        if pattern.get("name") == "Tempo":
            time = int(pattern.get("pos"))
            for event in pattern.iterfind("time"):
                midifile.addTempo(
                    track=0,
                    time=(time + int(event.get("pos"))) / 48.0,
                    tempo=float(event.get("value"))
                )


def convert_mmpz_to_midi(infile, outfile):
    root = get_root(infile)
    midifile = MIDIFile(get_instrument_count(root))
    midifile.addTempo(0, 0, get_starting_tempo(root))

    track_id = 0
    for track in root.find("song").find("trackcontainer"):
        if track.get("type") == "0":
            # Main instrument
            for pattern in track.iterfind("pattern"):
                add_notes_from_pattern(midifile, pattern, track_id)
            track_id += 1
        elif track.get("type") == "1":
            # Beat/Bassline
            pass # TODO
        elif track.get("type") == "5":
            # Automation track
            add_tempo_events_from_track(midifile, track)
                    

    midifile.writeFile(open(outfile, "wb"))
