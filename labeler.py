"""The labeler. You do NOT need to edit this file to start.
Week 3 opens the box and explains how the API call works.

label_comment(text) -> one of LABELS, or "unclear" if the model answers something else.
"""
import os
import requests

# ---- CHANGE THIS for your own business ---------------------------------
BUSINESS = "a pizza delivery company"
LABELS = ["positive", "negative"]
GUIDE = """Label the customer comment with exactly one word: positive or negative.
- Label by the overall message of the comment.
- If it has praise and a complaint, label by the bigger problem the customer would act on.
- Sarcasm counts as negative.
- If it is a question or too short to tell, choose the closer label."""
# -------------------------------------------------------------------------

# If you get a 404, the model was retired. List yours at https://console.groq.com/docs/models
MODEL = "openai/gpt-oss-20b"
URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_key():
    key = os.environ.get("groq-key-try1")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("groq-key-try1")
    except Exception:
        return None


def _demo_label(text):
    """Used when there is no API key, so the app still runs. Very crude."""
    bad = ["cold", "late", "wrong", "missing", "crash", "refund", "hair", "sick", "never",
           "expensive", "disgusting", "rained", "thanks a lot", "nothing could be done"]
    return "negative" if any(w in text.lower() for w in bad) else "positive"


def label_comment(text):
    key = _get_key()
    if not key:
        return _demo_label(text)
    prompt = (f"You label customer comments for {BUSINESS}.\n{GUIDE}\n"
              f"Allowed labels: {', '.join(LABELS)}.\nReply with the label only.\n\nComment: {text}")
    r = requests.post(
        URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": MODEL, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"].strip().lower().strip(".\"' ")
    return answer if answer in LABELS else "unclear"


def using_demo_mode():
    return _get_key() is None
