from pathlib import Path
import build_clear_piano as base

base.NOTES = {
    "C4": (261.63, "C", "C"),
    "Db4": (277.18, "D flat", "Db"),
    "D4": (293.66, "D", "D"),
    "Eb4": (311.13, "E flat", "Eb"),
    "E4": (329.63, "E", "E"),
    "F4": (349.23, "F", "F"),
    "Gb4": (369.99, "G flat", "Gb"),
    "G4": (392.00, "G", "G"),
    "Ab4": (415.30, "A-flat", "Ab"),
    "A4": (440.00, "A", "A"),
    "Bb4": (466.16, "B flat", "Bb"),
    "B4": (493.88, "B", "B"),
    "C5": (523.25, "C", "C"),
}

base.main()

path = Path(__file__).resolve().parents[1] / "index.html"
text = path.read_text(encoding="utf-8")
text = text.replace("Clear Voice v4 - real spoken names, dry audio", "Clear Voice v5 - corrected A and F")
path.write_text(text, encoding="utf-8")
