## Tovias Publishing Toolkit (Personal)

A personal toolkit to extract quotes from images, generate social quote tiles, post to Facebook and WordPress, plus audio and grammar tools. KDP/Instagram pieces are optional.

### Setup

```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python -m playwright install
cp .env.example .env
```

### Marketing workflow

- Generate a campaign from images (OCR quotes) and post to Facebook:
```
python main.py campaign --images path/to/images --title "My Book" --author "Me" --post_facebook --out_dir output/campaign
```
- Or from a quotes.txt file (one quote per line):
```
python main.py campaign --quotes_file output/quotes.txt --title "My Book" --author "Me" --post_facebook --out_dir output/campaign
```
- Post to WordPress too:
```
python main.py campaign --quotes_file output/quotes.txt --title "My Book" --author "Me" --post_facebook --post_wordpress
```

### Other commands

- Launch Grammarly editor: `python main.py grammarly`
- OCR quotes only: `python main.py ocr --images path/to/images --out output/quotes.txt`
- Generate a cover: `python main.py cover --title "My Book" --author "Me" --quote_file output/quotes.txt --out output/cover.png`
- Record audio: `python main.py record --out output/read.wav --seconds 60`
- TTS: `python main.py tts --text_file manuscript.txt --out output/tts.wav`

Notes: Facebook and WordPress use their APIs and credentials from `.env`. Instagram requires a public image URL and is not enabled by default.
