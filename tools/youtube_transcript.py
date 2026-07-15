#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Callable
from urllib.parse import parse_qs, urlparse


DEFAULT_LANGUAGES = ["en"]


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    text: str


@dataclass(frozen=True)
class TranscriptResult:
    method: str
    language: str
    segments: list[TranscriptSegment]


class YouTubeTranscriptError(RuntimeError):
    pass


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif host.endswith("youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/shorts/") or parsed.path.startswith("/embed/"):
            video_id = parsed.path.strip("/").split("/")[1]
        else:
            video_id = ""
    else:
        video_id = ""

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Could not extract YouTube video ID from URL: {url}")
    return video_id


def slugify_filename(title: str) -> str:
    cleaned = re.sub(r"[/:*?\"<>|]+", " - ", title)
    cleaned = re.sub(r"[!]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .-_")
    return cleaned or "YouTube transcript"


def format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_transcript_markdown(
    *,
    title: str,
    source_url: str,
    method: str,
    language: str,
    segments: list[TranscriptSegment],
) -> str:
    lines = [
        f"# {title}",
        "",
        "## Source",
        "",
        f"- **Source:** {source_url}",
        f"- **Transcript method:** {method}",
        f"- **Language:** {language}",
        "",
        "## Transcript",
        "",
    ]
    for segment in segments:
        text = re.sub(r"\s+", " ", segment.text).strip()
        if text:
            lines.append(f"[{format_timestamp(segment.start)}] {text}")
    lines.append("")
    return "\n".join(lines)


def fetch_youtube_captions(video_id: str, languages: list[str]) -> list[TranscriptSegment]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise YouTubeTranscriptError(
            "Missing dependency: install youtube-transcript-api to fetch YouTube captions."
        ) from exc

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except Exception as exc:  # library exposes several version-dependent exception classes
        raise YouTubeTranscriptError(str(exc)) from exc

    return [
        TranscriptSegment(start=float(item.get("start", 0.0)), text=str(item.get("text", "")))
        for item in transcript
    ]


def fetch_video_title(url: str) -> str:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        return f"YouTube transcript {extract_video_id(url)}"

    result = subprocess.run(
        [yt_dlp, "--print", "%(title)s", "--skip-download", url],
        capture_output=True,
        text=True,
        check=False,
    )
    title = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    return title or f"YouTube transcript {extract_video_id(url)}"


def transcribe_with_faster_whisper(url: str, language: str) -> list[TranscriptSegment]:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        raise YouTubeTranscriptError("Missing executable: install yt-dlp to download audio for Whisper fallback.")

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise YouTubeTranscriptError("Missing dependency: install faster-whisper for local transcription fallback.") from exc

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_template = str(Path(tmpdir) / "audio.%(ext)s")
        result = subprocess.run(
            [
                yt_dlp,
                "-x",
                "--audio-format",
                "mp3",
                "-o",
                audio_template,
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise YouTubeTranscriptError(f"yt-dlp audio download failed:\n{result.stderr.strip()}")

        audio_files = list(Path(tmpdir).glob("audio.*"))
        if not audio_files:
            raise YouTubeTranscriptError("yt-dlp completed but no audio file was produced.")

        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(audio_files[0]), language=language)
        return [TranscriptSegment(start=float(segment.start), text=segment.text) for segment in segments]


CaptionProvider = Callable[[str, list[str]], list[TranscriptSegment]]
WhisperProvider = Callable[[str, str], list[TranscriptSegment]]


def get_transcript(
    url: str,
    languages: list[str],
    *,
    captions_provider: CaptionProvider = fetch_youtube_captions,
    whisper_provider: WhisperProvider = transcribe_with_faster_whisper,
    prefer_whisper: bool = False,
) -> TranscriptResult:
    if not languages:
        languages = DEFAULT_LANGUAGES
    video_id = extract_video_id(url)
    language = languages[0]

    if not prefer_whisper:
        try:
            segments = captions_provider(video_id, languages)
            return TranscriptResult(method="youtube-captions", language=language, segments=segments)
        except YouTubeTranscriptError:
            pass

    segments = whisper_provider(url, language)
    return TranscriptResult(method="faster-whisper", language=language, segments=segments)


def write_transcript_markdown(
    *,
    output_path: Path,
    title: str,
    source_url: str,
    method: str,
    language: str,
    segments: list[TranscriptSegment],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        format_transcript_markdown(
            title=title,
            source_url=source_url,
            method=method,
            language=language,
            segments=segments,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown transcript from a YouTube URL.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--output", help="Output Markdown path. Defaults to raw/<video title> transcript.md")
    parser.add_argument(
        "--language",
        action="append",
        dest="languages",
        help="Preferred transcript language code. Can be repeated. Defaults to en.",
    )
    parser.add_argument(
        "--prefer-whisper",
        action="store_true",
        help="Skip YouTube captions and transcribe downloaded audio with faster-whisper.",
    )
    parser.add_argument("--title", help="Override the transcript title.")
    args = parser.parse_args(argv)

    languages = args.languages or DEFAULT_LANGUAGES
    title = args.title or fetch_video_title(args.url)
    output_path = Path(args.output) if args.output else Path("raw") / f"{slugify_filename(title)} transcript.md"

    try:
        transcript = get_transcript(args.url, languages, prefer_whisper=args.prefer_whisper)
    except (ValueError, YouTubeTranscriptError) as exc:
        parser.exit(1, f"Error: {exc}\n")

    write_transcript_markdown(
        output_path=output_path,
        title=title,
        source_url=args.url,
        method=transcript.method,
        language=transcript.language,
        segments=transcript.segments,
    )
    print(f"Wrote {output_path}")
    print(f"Transcript method: {transcript.method}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
