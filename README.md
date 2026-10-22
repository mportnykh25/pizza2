# Slice Street Pizza: feedback app (starter)

Type a customer comment and choose a star rating (1 to 5). The app labels the comment
(positive or negative), saves it to `feedback.csv`, and shows:
1. how many comments are positive vs negative,
2. the average star rating for each label,
3. the comments to read carefully: a positive label with a low rating, or a negative label
   with a high rating (or a label that is unclear).

The app starts empty. Add comments live. `demo_comments.csv` has 20 fictional comments with
ratings that you can type in (or copy from) to fill it up.

## Files
- `app.py`: the Streamlit app
- `labeler.py`: the function that asks the LLM for a label (you do not need to edit the API part)
- `logo.png`, `logo.svg`: the company logo
- `demo_comments.csv`: sample comments to type in, not loaded automatically
- `requirements.txt`: packages Streamlit Cloud installs for you

## Run it online for free (no terminal)
1. Put these files in a public GitHub repository (upload them in the browser).
2. On share.streamlit.io, create an app from the repository, main file `app.py`.
3. Under Advanced settings, add a secret: `GROQ_API_KEY = "your key"` (a free Groq key, no credit card).
Without a key the app still runs, with a crude keyword rule and a warning.
Saved files can disappear when the app restarts, so use the Download CSV button.

## Your homework: make it about a different business
Pick a business other than pizza delivery. Edit only the lines marked `CHANGE THIS`:
- `labeler.py`: BUSINESS, LABELS (keep it to two), GUIDE (your rules for hard cases)
- `app.py`: TITLE, SUBTITLE, LOGO (replace `logo.png` with your own), what counts as a low or high rating
Then type about 10 to 20 fictional comments with ratings and check: which comments got flagged?
Change one rule in GUIDE and see what changes.
If you get a 404 error about the model, the model was retired: find a current one at console.groq.com/docs/models.
