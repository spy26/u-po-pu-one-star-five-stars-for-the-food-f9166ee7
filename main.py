"""One Star, Five Stars for the Food — entry writer.

Writes a single-sentence alien tourist review of Earth to entry.txt.
Deterministic: no network, no clock, no randomness, stdlib only.

Gate (from the kit): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only whitespace, and a single sentence.
"""

import hashlib
import os
import sys

SENTENCE = (
    "One star: your sun burned my third eye, your pigeons stole my lunch, "
    "and yet the fried chicken from that gas station rewired my opinion "
    "of carbon-based life."
)

MAX_CHARS = 200
FALLBACK_DIR = "/output"
FILENAME = "entry.txt"


class GateError(ValueError):
    """Raised when the sentence fails the competition gate."""


def check_sentence(text):
    """Return a list of gate failures for `text` (empty means it passes)."""
    failures = []
    if not isinstance(text, str):
        failures.append("not text")
        return failures
    if len(text) < 1:
        failures.append("empty")
    if len(text) > MAX_CHARS:
        failures.append("over %d characters: %d" % (MAX_CHARS, len(text)))
    if text.strip() == "":
        failures.append("only whitespace")
    if "\n" in text or "\r" in text:
        failures.append("contains a line break")
    if any(ord(ch) < 32 for ch in text):
        failures.append("contains a control character")
    if text != text.strip():
        failures.append("leading or trailing whitespace")
    terminators = sum(text.count(mark) for mark in (".", "!", "?"))
    if terminators != 1 or not text.endswith("."):
        failures.append("not exactly one sentence")
    return failures


def resolve_output_dir():
    """Output dir from the environment, falling back to /output."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    return chosen


def write_entry(directory):
    """Write the sentence as UTF-8 bytes (no trailing newline) and verify
    the round-trip: read the file back and require byte-identical content."""
    failures = check_sentence(SENTENCE)
    if failures:
        raise GateError("gate failed: " + "; ".join(failures))
    payload = SENTENCE.encode("utf-8")
    os.makedirs(directory, exist_ok=True)
    target = os.path.join(directory, FILENAME)
    with open(target, "wb") as handle:
        handle.write(payload)
    with open(target, "rb") as handle:
        round_tripped = handle.read()
    if round_tripped != payload:
        raise GateError("round-trip mismatch: wrote %d bytes, read %d bytes"
                        % (len(payload), len(round_tripped)))
    return target, payload


def main(argv):
    if len(argv) > 1:
        sys.stderr.write("usage: python3 main.py (takes no arguments)\n")
        return 2
    try:
        directory = resolve_output_dir()
        target, payload = write_entry(directory)
    except GateError as exc:
        sys.stderr.write("error: %s\n" % exc)
        return 1
    except OSError as exc:
        sys.stderr.write("error: cannot write entry: %s\n" % exc)
        return 1
    digest = hashlib.sha256(payload).hexdigest()
    print("wrote %s (%d characters, %d bytes, sha256 %s)"
          % (target, len(SENTENCE), len(payload), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
