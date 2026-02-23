#!/usr/bin/env python3
"""
Queue Processor for Markdown Files

This script helps process the markdown file queue month by month.
Usage:
    python3 process_queue.py --month 2026-02 --location kush
    python3 process_queue.py --next
    python3 process_queue.py --list
"""

import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict

QUEUE_FILE = Path(__file__).parent / "MARKDOWN_SCAN_QUEUE.json"


def load_queue() -> dict:
    """Load the queue JSON file."""
    with open(QUEUE_FILE) as f:
        return json.load(f)


def get_next_month(queue_data: dict, last_processed: Optional[str] = None) -> Optional[dict]:
    """Get the next month to process."""
    if last_processed is None:
        # Start with the first (newest) month
        return queue_data["queue"][0] if queue_data["queue"] else None

    # Find the month after last_processed
    found = False
    for month_entry in queue_data["queue"]:
        if found:
            return month_entry
        if month_entry["month"] == last_processed:
            found = True

    return None


def get_month_files(queue_data: dict, month: str, location: Optional[str] = None) -> list[str]:
    """Get all files for a specific month, optionally filtered by location."""
    for month_entry in queue_data["queue"]:
        if month_entry["month"] == month:
            files = []
            for loc_entry in month_entry["locations"]:
                if location is None or loc_entry["location"] == location:
                    files.extend(loc_entry["files"])
            return files
    return []


def list_months(queue_data: dict):
    """List all months in the queue."""
    print("Available months:")
    for month_entry in queue_data["queue"]:
        month = month_entry["month"]
        total = month_entry["total_files"]
        locations = ", ".join([f"{loc['location']}({loc['file_count']})"
                              for loc in month_entry["locations"]])
        print(f"  {month}: {total} files [{locations}]")


def main():
    parser = argparse.ArgumentParser(description="Process markdown file queue")
    parser.add_argument("--month", help="Process specific month (YYYY-MM)")
    parser.add_argument("--location", help="Filter by location (kush, kooshapari, temp-PRODVERCEL)")
    parser.add_argument("--next", action="store_true", help="Get next month to process")
    parser.add_argument("--list", action="store_true", help="List all months")
    parser.add_argument("--files", action="store_true", help="Output file list")
    parser.add_argument("--count", action="store_true", help="Show file count only")

    args = parser.parse_args()

    queue_data = load_queue()

    if args.list:
        list_months(queue_data)
        return

    if args.next:
        # Try to read last processed from a file
        last_file = Path(__file__).parent / ".last_processed"
        last_processed = None
        if last_file.exists():
            last_processed = last_file.read_text().strip()

        next_month = get_next_month(queue_data, last_processed)
        if next_month:
            print(f"Next month to process: {next_month['month']}")
            print(f"Total files: {next_month['total_files']}")
            if args.files:
                for loc_entry in next_month["locations"]:
                    print(f"\n[{loc_entry['location']}] ({loc_entry['file_count']} files):")
                    for filepath in loc_entry["files"][:10]:  # Show first 10
                        print(f"  {filepath}")
                    if loc_entry["file_count"] > 10:
                        print(f"  ... and {loc_entry['file_count'] - 10} more")
        else:
            print("No more months to process!")
        return

    if args.month:
        files = get_month_files(queue_data, args.month, args.location)

        if args.count:
            print(len(files))
        elif args.files:
            for filepath in files:
                print(filepath)
        else:
            print(f"Month: {args.month}")
            if args.location:
                print(f"Location: {args.location}")
            print(f"Files: {len(files)}")
            print("\nFirst 20 files:")
            for filepath in files[:20]:
                print(f"  {filepath}")
            if len(files) > 20:
                print(f"\n... and {len(files) - 20} more files")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
