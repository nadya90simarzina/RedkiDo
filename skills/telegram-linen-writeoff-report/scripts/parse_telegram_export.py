#!/usr/bin/env python3
"""Extract readable messages from a Telegram Desktop HTML export."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


@dataclass
class Message:
    id: str
    dt: str
    date: str
    time: str
    author: str
    text: str
    joined: bool


def _classes(attrs: list[tuple[str, str | None]]) -> set[str]:
    for key, value in attrs:
        if key == "class" and value:
            return set(value.split())
    return set()


def _attr(attrs: list[tuple[str, str | None]], name: str) -> str:
    for key, value in attrs:
        if key == name and value is not None:
            return value
    return ""


def _clean_text(text: str) -> str:
    lines = []
    for line in unescape(text).splitlines():
        line = re.sub(r"[ \t\xa0]+", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


class TelegramExportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.messages: list[Message] = []
        self.current: dict[str, object] | None = None
        self.message_depth: int | None = None
        self.capture: str | None = None
        self.capture_depth: int | None = None
        self.buffers: dict[str, list[str]] = {}
        self.last_author = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = _classes(attrs)
        depth = len(self.stack)

        if tag == "div" and "message" in classes:
            self.current = {
                "id": _attr(attrs, "id"),
                "joined": "joined" in classes,
                "date_title": "",
            }
            self.message_depth = depth
            self.buffers = {"from_name": [], "text": []}

        if self.current is not None and tag == "div":
            if "date" in classes:
                self.current["date_title"] = _attr(attrs, "title")
            elif "from_name" in classes and not self.buffers.get("from_name"):
                self.capture = "from_name"
                self.capture_depth = depth
            elif "text" in classes:
                self.capture = "text"
                self.capture_depth = depth

        if self.current is not None and self.capture == "text" and tag == "br":
            self.buffers["text"].append("\n")

        self.stack.append((tag, classes))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.current is not None and self.capture == "text" and tag == "br":
            self.buffers["text"].append("\n")

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.capture:
            self.buffers[self.capture].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is not None and self.capture and self.capture_depth == len(self.stack) - 1:
            self.capture = None
            self.capture_depth = None

        if self.current is not None and tag == "div" and self.message_depth == len(self.stack) - 1:
            self._finish_message()

        if self.stack:
            self.stack.pop()

    def _finish_message(self) -> None:
        assert self.current is not None
        raw_dt = str(self.current.get("date_title") or "")
        text = _clean_text("".join(self.buffers.get("text", [])))
        author = _clean_text("".join(self.buffers.get("from_name", [])))
        if author:
            author = author.splitlines()[0].strip()
        joined = bool(self.current.get("joined"))
        if not author and joined:
            author = self.last_author
        if author:
            self.last_author = author

        if raw_dt and text:
            try:
                dt = datetime.strptime(raw_dt.split(" UTC")[0], "%d.%m.%Y %H:%M:%S")
                self.messages.append(
                    Message(
                        id=str(self.current.get("id") or ""),
                        dt=dt.isoformat(sep=" "),
                        date=dt.date().isoformat(),
                        time=dt.strftime("%H:%M:%S"),
                        author=author,
                        text=text,
                        joined=joined,
                    )
                )
            except ValueError:
                pass

        self.current = None
        self.message_depth = None
        self.capture = None
        self.capture_depth = None
        self.buffers = {}


def parse_messages(path: str | Path) -> list[Message]:
    try:
        return _parse_messages_lxml(path)
    except Exception:
        # Keep a stdlib fallback for environments without lxml or with unusual parser failures.
        return _parse_messages_stdlib(path)


def _parse_messages_stdlib(path: str | Path) -> list[Message]:
    html = Path(path).read_text(encoding="utf-8")
    parser = TelegramExportParser()
    parser.feed(html)
    parser.close()
    return parser.messages


def _lxml_text_with_breaks(element: object) -> str:
    parts: list[str] = []

    def walk(node: object) -> None:
        text = getattr(node, "text", None)
        if text:
            parts.append(text)
        for child in node:
            tag = str(getattr(child, "tag", "")).lower()
            if tag == "br":
                parts.append("\n")
            else:
                walk(child)
            tail = getattr(child, "tail", None)
            if tail:
                parts.append(tail)

    walk(element)
    return _clean_text("".join(parts))


def _parse_messages_lxml(path: str | Path) -> list[Message]:
    from lxml import html as lxml_html  # type: ignore

    source = Path(path).read_text(encoding="utf-8")
    doc = lxml_html.fromstring(source)
    result: list[Message] = []
    last_author = ""

    message_nodes = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " message ")]')
    for node in message_nodes:
        classes = set((node.get("class") or "").split())
        if "service" in classes:
            continue
        titles = node.xpath('.//div[contains(concat(" ", normalize-space(@class), " "), " date ")]/@title')
        if not titles:
            continue
        try:
            dt = datetime.strptime(str(titles[0]).split(" UTC")[0], "%d.%m.%Y %H:%M:%S")
        except ValueError:
            continue

        text_nodes = node.xpath('.//div[contains(concat(" ", normalize-space(@class), " "), " text ")]')
        text = "\n".join(_lxml_text_with_breaks(text_node) for text_node in text_nodes).strip()
        if not text:
            continue

        from_nodes = node.xpath('.//div[contains(concat(" ", normalize-space(@class), " "), " from_name ")]')
        author = _lxml_text_with_breaks(from_nodes[0]).splitlines()[0].strip() if from_nodes else ""
        joined = "joined" in classes
        if not author and joined:
            author = last_author
        if author:
            last_author = author

        result.append(
            Message(
                id=str(node.get("id") or ""),
                dt=dt.isoformat(sep=" "),
                date=dt.date().isoformat(),
                time=dt.strftime("%H:%M:%S"),
                author=author,
                text=text,
                joined=joined,
            )
        )

    return result


def filter_messages(messages: Iterable[Message], start: date | None, end: date | None) -> list[Message]:
    result = []
    for message in messages:
        message_date = date.fromisoformat(message.date)
        if start and message_date < start:
            continue
        if end and message_date > end:
            continue
        result.append(message)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract messages from Telegram messages.html.")
    parser.add_argument("messages_html", help="Path to Telegram messages.html")
    parser.add_argument("--start", help="Inclusive start date, YYYY-MM-DD")
    parser.add_argument("--end", help="Inclusive end date, YYYY-MM-DD")
    parser.add_argument("--output", help="Output JSON path. Prints to stdout when omitted.")
    args = parser.parse_args()

    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    messages = filter_messages(parse_messages(args.messages_html), start, end)
    payload = [asdict(message) for message in messages]
    text = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
