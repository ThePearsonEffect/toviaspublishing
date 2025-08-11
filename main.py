from __future__ import annotations

import argparse
from pathlib import Path

from src.config import ensure_output_dir
from src.utils.log import setup_logging
from src.ocr.extract import extract_text_from_images, extract_quotes
from src.cover.generate import generate_cover, generate_tshirt_design
from src.publishing.kdp import upload_sync
from src.marketing.facebook import post_to_facebook
from src.marketing.instagram import post_to_instagram
from src.marketing.wordpress import post_to_wordpress
from src.audio.record import record_microphone
from src.audio.tts import text_to_speech
from src.grammar.check import GrammarChecker
from src.web.app import create_app
from src.export.format import export_to_pdf, export_to_epub
from src.marketing.generator import generate_quote_tiles, compose_message
from src.marketing.details import generate_book_cover_details, generate_tshirt_details
from src.integrations.brain_runner import ExternalBrain, run_sync
from src.tracking.progress import generate_run_id, log, summarize_run, tail
from src.algorithms.selection import score_quotes, compose_variants


def cmd_ocr(args: argparse.Namespace) -> None:
    images_dir = Path(args.images)
    image_paths = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}])
    text = extract_text_from_images(image_paths)
    quotes = extract_quotes(text)
    ensure_output_dir()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n\n".join(quotes), encoding="utf-8")
    print(f"Saved quotes to {out}")


def cmd_cover(args: argparse.Namespace) -> None:
    quote = args.quote
    if args.quote_file:
        quote = Path(args.quote_file).read_text(encoding="utf-8").splitlines()[0]
    out = Path(args.out)
    generate_cover(args.title, args.author, quote, out)
    print(f"Saved cover to {out}")


def cmd_tshirt(args: argparse.Namespace) -> None:
    out = Path(args.out)
    generate_tshirt_design(text=args.text, out_path=out, title=args.title or None)
    print(f"Saved t-shirt design to {out}")


def cmd_details(args: argparse.Namespace) -> None:
    if args.kind == "cover":
        details = generate_book_cover_details(args.title, args.author, args.text)
    else:
        details = generate_tshirt_details(args.title, args.author, args.text)
    out = Path(args.out)
    out.write_text(
        f"Title: {details.title}\n\nDescription:\n{details.description}\n\nTags: {', '.join(details.tags)}\n",
        encoding="utf-8",
    )
    print(f"Saved product details to {out}")


def cmd_export(args: argparse.Namespace) -> None:
    text_file = Path(args.text)
    if args.pdf:
        export_to_pdf(text_file, Path(args.pdf))
        print(f"Wrote PDF to {args.pdf}")
    if args.epub:
        export_to_epub(text_file, Path(args.epub))
        print(f"Wrote EPUB to {args.epub}")


def cmd_kdp(args: argparse.Namespace) -> None:
    ebook = Path(args.ebook) if args.ebook else None
    pdf = Path(args.paperback) if args.paperback else None
    upload_sync(ebook, pdf, args.title)


def cmd_post(args: argparse.Namespace) -> None:
    run_id = generate_run_id("single_post")
    try:
        platform = args.platform.lower()
        log(run_id, "post", "start", "started", f"Posting to {platform}")
        if platform == "facebook":
            post_to_facebook(args.message, Path(args.image) if args.image else None)
            log(run_id, "post", "facebook", "success", "Posted to Facebook")
            print("Posted to Facebook")
        elif platform == "instagram":
            post_to_instagram(args.message, Path(args.image))
            log(run_id, "post", "instagram", "success", "Requested Instagram post")
        elif platform == "wordpress":
            post_id = post_to_wordpress(args.title or "Post", args.message, Path(args.image) if args.image else None)
            log(run_id, "post", "wordpress", "success", f"WordPress post ID {post_id}")
            print(f"WordPress post ID: {post_id}")
        else:
            raise SystemExit("Unsupported platform")
    except Exception as e:
        log(run_id, "post", "error", "error", str(e))
        raise


def cmd_record(args: argparse.Namespace) -> None:
    out = Path(args.out)
    record_microphone(out, seconds=args.seconds)
    print(f"Saved recording to {out}")


def cmd_tts(args: argparse.Namespace) -> None:
    text = Path(args.text_file).read_text(encoding="utf-8")
    out = Path(args.out)
    text_to_speech(text, out)
    print(f"Saved TTS to {out}")


def cmd_grammarly(_: argparse.Namespace) -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)


def cmd_grammar_check(args: argparse.Namespace) -> None:
    text = Path(args.text_file).read_text(encoding="utf-8")
    checker = GrammarChecker()
    result = checker.check(text)
    out = Path(args.out)
    out.write_text(result.corrected_text, encoding="utf-8")
    print(f"Saved corrected text to {out}")


def cmd_campaign(args: argparse.Namespace) -> None:
    run_id = generate_run_id("campaign")
    try:
        log(run_id, "campaign", "start", "started", "Campaign started")
        quotes: list[str] = []
        if args.images:
            images_dir = Path(args.images)
            image_paths = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}])
            text = extract_text_from_images(image_paths)
            quotes = extract_quotes(text)
            log(run_id, "campaign", "ocr", "success", f"Extracted {len(quotes)} quotes")
        elif args.quotes_file:
            content = Path(args.quotes_file).read_text(encoding="utf-8")
            quotes = [q.strip() for q in content.splitlines() if q.strip()]
            log(run_id, "campaign", "load_quotes", "success", f"Loaded {len(quotes)} quotes from file")
        if not quotes:
            log(run_id, "campaign", "no_quotes", "error", "No quotes found")
            raise SystemExit("No quotes found. Provide --images or --quotes_file.")

        # Algorithmic selection
        if args.algorithm == "salience":
            ranked = score_quotes(quotes)
            quotes = [qs.quote for qs in ranked]
            log(run_id, "campaign", "rank", "success", "Quotes ranked by salience", {
                "top_example": ranked[0].details if ranked else {}
            })

        if args.limit:
            quotes = quotes[: args.limit]
            log(run_id, "campaign", "limit", "info", f"Limited to {len(quotes)} quotes")

        out_dir = Path(args.out_dir or ensure_output_dir()) / "campaign"
        tiles = generate_quote_tiles(quotes, args.author or "", out_dir)
        log(run_id, "campaign", "tiles", "success", f"Generated {len(tiles)} tiles", {"dir": str(out_dir)})

        for idx, (quote, tile) in enumerate(zip(quotes, tiles), start=1):
            message = compose_message(args.title or "", args.author or "", quote)
            if args.post_facebook:
                post_to_facebook(message, tile)
                log(run_id, "campaign", f"fb_{idx}", "success", f"Posted {tile.name}")
            if args.post_wordpress:
                wp_title = f"{args.title or 'Book'} — Quote"
                post_to_wordpress(wp_title, message, tile)
                log(run_id, "campaign", f"wp_{idx}", "success", f"Posted {tile.name}")

        log(run_id, "campaign", "done", "success", "Campaign finished")
        print(f"Campaign assets in {out_dir}\nRun ID: {run_id}")
    except Exception as e:
        log(run_id, "campaign", "error", "error", str(e))
        raise


def cmd_brain(args: argparse.Namespace) -> None:
    brain = ExternalBrain(Path(args.path))
    result = run_sync(brain.execute(args.command, {}))
    print(result)


def cmd_brain_fb(args: argparse.Namespace) -> None:
    brain = ExternalBrain(Path(args.path))
    post_text = run_sync(brain.social_post("facebook", args.prompt, {}))
    post_to_facebook(post_text, Path(args.image) if args.image else None)
    print("Facebook post created via BusinessBrain and posted.")


def cmd_progress(args: argparse.Namespace) -> None:
    if args.run_id:
        summary = summarize_run(args.run_id)
        print(summary)
    else:
        recs = tail(args.tail)
        for r in recs:
            print(f"{r.run_id} | {r.phase}:{r.step} | {r.status} | {r.message}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Tovias Publishing Toolkit")
    sub = p.add_subparsers(dest="command", required=True)

    ocr = sub.add_parser("ocr", help="Extract quotes from images via OCR")
    ocr.add_argument("--images", required=True, help="Directory of images")
    ocr.add_argument("--out", required=True, help="Output quotes .txt file")
    ocr.set_defaults(func=cmd_ocr)

    cover = sub.add_parser("cover", help="Generate a book cover image")
    cover.add_argument("--title", required=True)
    cover.add_argument("--author", required=True)
    cover.add_argument("--quote", required=False, default="")
    cover.add_argument("--quote_file", required=False)
    cover.add_argument("--out", required=True)
    cover.set_defaults(func=cmd_cover)

    tshirt = sub.add_parser("tshirt", help="Generate a t-shirt design (transparent PNG)")
    tshirt.add_argument("--text", required=True)
    tshirt.add_argument("--title")
    tshirt.add_argument("--out", required=True)
    tshirt.set_defaults(func=cmd_tshirt)

    details = sub.add_parser("details", help="Generate product details text")
    details.add_argument("--kind", choices=["cover", "tshirt"], required=True)
    details.add_argument("--title", required=True)
    details.add_argument("--author", required=True)
    details.add_argument("--text", required=True, help="Quote or front text")
    details.add_argument("--out", required=True)
    details.set_defaults(func=cmd_details)

    export = sub.add_parser("export", help="Export manuscript to PDF/EPUB")
    export.add_argument("--text", required=True)
    export.add_argument("--pdf")
    export.add_argument("--epub")
    export.set_defaults(func=cmd_export)

    kdp = sub.add_parser("kdp", help="Assist with Amazon KDP uploads")
    kdp.add_argument("--ebook")
    kdp.add_argument("--paperback")
    kdp.add_argument("--title", required=True)
    kdp.set_defaults(func=cmd_kdp)

    post = sub.add_parser("post", help="Post to social platforms")
    post.add_argument("--platform", choices=["facebook", "instagram", "wordpress"], required=True)
    post.add_argument("--message", required=True)
    post.add_argument("--title")
    post.add_argument("--image")
    post.set_defaults(func=cmd_post)

    record = sub.add_parser("record", help="Record microphone audio")
    record.add_argument("--out", required=True)
    record.add_argument("--seconds", type=int, default=60)
    record.set_defaults(func=cmd_record)

    tts = sub.add_parser("tts", help="Text to speech")
    tts.add_argument("--text_file", required=True)
    tts.add_argument("--out", required=True)
    tts.set_defaults(func=cmd_tts)

    gram_ui = sub.add_parser("grammarly", help="Launch Grammarly-enabled editor UI")
    gram_ui.set_defaults(func=cmd_grammarly)

    gram = sub.add_parser("grammar", help="Batch grammar check with LanguageTool")
    gram.add_argument("--text_file", required=True)
    gram.add_argument("--out", required=True)
    gram.set_defaults(func=cmd_grammar_check)

    camp = sub.add_parser("campaign", help="Generate quote tiles and optionally post to Facebook/WordPress")
    camp.add_argument("--title")
    camp.add_argument("--author")
    group = camp.add_mutually_exclusive_group(required=True)
    group.add_argument("--images", help="Directory of images to OCR for quotes")
    group.add_argument("--quotes_file", help="Text file with one quote per line")
    camp.add_argument("--out_dir", help="Output directory for generated tiles")
    camp.add_argument("--limit", type=int)
    camp.add_argument("--algorithm", choices=["default", "salience"], default="salience")
    camp.add_argument("--post_facebook", action="store_true")
    camp.add_argument("--post_wordpress", action="store_true")
    camp.set_defaults(func=cmd_campaign)

    brain = sub.add_parser("brain", help="Run an external BusinessBrain command")
    brain.add_argument("--path", required=True, help="Path to brain Python file, e.g., C:\\Users\\FireLeaf\\Desktop\\Core Brain\\brain")
    brain.add_argument("--command", required=True, help="Natural language command to run")
    brain.set_defaults(func=cmd_brain)

    brain_fb = sub.add_parser("brain_fb", help="Generate a Facebook post via BusinessBrain and post it")
    brain_fb.add_argument("--path", required=True)
    brain_fb.add_argument("--prompt", required=True)
    brain_fb.add_argument("--image")
    brain_fb.set_defaults(func=cmd_brain_fb)

    prog = sub.add_parser("progress", help="Show progress logs or a run summary")
    prog.add_argument("--run_id", help="Run ID to summarize")
    prog.add_argument("--tail", type=int, default=50, help="Tail last N records if no run_id provided")
    prog.set_defaults(func=cmd_progress)

    return p


def main() -> None:
    setup_logging()
    ensure_output_dir()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
