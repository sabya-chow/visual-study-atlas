# Demo

`source/home_budgeting_guide.pdf` is an original three-page text written for this repository (CC0). `build_demo.py` turns it into `app/` using the skill's scripts; `demo.mp4` is a recording of that app (`make_video.py` rebuilds it from the screen captures in `video_frames/`).

Run the app: `cd app && python3 server.py` then open http://127.0.0.1:8801 (the ask box needs Ollama running).
`budgeting_flashcards.txt` is the Anki import file produced by `export_anki.py`.
