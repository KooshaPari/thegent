import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path("src").resolve()))

from thegent.contracts.parser import IncrementalXMLParser


def test_incremental_parsing():
    parser = IncrementalXMLParser()

    # Feed chunk 1: Start a tag
    chunk1 = "Hello! <STATUS>in_progr"
    new1 = parser.feed(chunk1)
    assert not new1

    all1 = parser.get_all_tags()
    assert all1 == {"STATUS": "in_progr"}

    # Feed chunk 2: Close the tag, start another
    chunk2 = "ess</STATUS>\n<PROGRESS>50"
    new2 = parser.feed(chunk2)
    assert "STATUS" in new2
    assert new2["STATUS"] == "in_progress"

    all2 = parser.get_all_tags()
    assert all2 == {"STATUS": "in_progress", "PROGRESS": "50"}

    # Feed chunk 3: Close second tag
    chunk3 = "%</PROGRESS>"
    new3 = parser.feed(chunk3)
    assert "PROGRESS" in new3
    assert new3["PROGRESS"] == "50%"

    all3 = parser.get_all_tags()
    assert all3 == {"STATUS": "in_progress", "PROGRESS": "50%"}


def test_sloppy_parsing():
    parser = IncrementalXMLParser()

    # Interleaved or unclosed tags
    text = "<STATUS>completed</STATUS><SUMMARY>Working on it... <BLOCKERS>None"
    parser.feed(text)

    all_tags = parser.get_all_tags(include_partial=True)
    assert all_tags["STATUS"] == "completed"
    assert all_tags["SUMMARY"] == "Working on it..."
    assert all_tags["BLOCKERS"] == "None"


def test_partial_tag_start():
    parser = IncrementalXMLParser()
    parser.feed("<STATUS>done</STATUS><PROG")

    partial = parser.get_partial_state()
    assert partial["incomplete_tag"] == "PROG"
    assert partial["open_tag"] is None


if __name__ == "__main__":
    test_incremental_parsing()
    test_sloppy_parsing()
    test_partial_tag_start()
