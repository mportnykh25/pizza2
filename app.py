import os

import altair as alt
import pandas as pd
import streamlit as st

from labeler import BUSINESS, label_comment, using_demo_mode

# ---- CHANGE THIS for your own business ---------------------------------
TITLE = "Slice Street Pizza"
SUBTITLE = "Customer feedback"
LOGO = "logo.png"
LOW_RATING, HIGH_RATING = 2, 4      # a "low" rating is <= 2 stars, a "high" rating is >= 4 stars
CSV_FILE = "feedback.csv"
LABEL_COLORS = {"positive": "#2BB38A", "negative": "#B34700", "unclear": "#D0D0D0"}   # bluish green, dark vermillion, light gray (colorblind-safe: they differ in lightness)
# -------------------------------------------------------------------------


def needs_review(label, rating):
    """Flag the rows we should read more carefully."""
    if label == "positive" and rating <= LOW_RATING:
        return True
    if label == "negative" and rating >= HIGH_RATING:
        return True
    if label not in ("positive", "negative"):   # "unclear" or anything unexpected
        return True
    return False


def add_flags(df):
    df = df.copy()
    df["read_carefully"] = [needs_review(l, r) for l, r in zip(df["label"], df["rating"])]
    return df


st.set_page_config(page_title=TITLE, page_icon=LOGO, layout="wide")

logo_col, title_col = st.columns([1, 9], vertical_alignment="center")
with logo_col:
    st.image(LOGO, width=90)
with title_col:
    st.title(TITLE)
    st.caption(f"{SUBTITLE}. You run {BUSINESS}. Customers leave feedback, the app labels and stores it, "
               "and you analyze the data later.")

if using_demo_mode():
    st.warning("No API key found, so the app is using a crude keyword rule instead of an LLM. "
               "Add GROQ_API_KEY to your secrets to use the LLM.")

# The app starts empty. Rows are added live and saved to a CSV file.
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else \
        pd.DataFrame(columns=["comment", "rating", "label"])

tab_customer, tab_owner = st.tabs(["Customer: leave feedback", "Owner: analyze the feedback"])

with tab_customer:
    # ---- 1. Type feedback, pick stars, get a label, save ------------------------
    st.subheader("Tell us about your order")
    with st.form("feedback_form", clear_on_submit=True):
        comment = st.text_area("Your comment")
        st.write("Rating")
        stars = st.feedback("stars")          # None until clicked, then 0 to 4
        submitted = st.form_submit_button("Send feedback")

    if submitted:
        if not comment.strip() or stars is None:
            st.error("Please type a comment and choose a star rating.")
        else:
            rating = stars + 1                # 1 to 5 stars
            with st.spinner("Labeling..."):
                label = label_comment(comment.strip())
            new_row = pd.DataFrame([{"comment": comment.strip(), "rating": rating, "label": label}])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.session_state.df.to_csv(CSV_FILE, index=False)   # save to CSV
            st.success("Thank you for your feedback!")
            st.caption(f"Behind the scenes, the app labeled it: {label} ({'★' * rating})")


df = add_flags(st.session_state.df)

with tab_owner:

    if df.empty:
        st.info("No feedback yet. Switch to the customer tab and add the first comment.")
    else:
        # ---- 2. Counts and average rating ---------------------------------------
        st.subheader("What are customers saying?")
        df["rating"] = df["rating"].astype(float)
        n_total = len(df)
        n_pos = int((df["label"] == "positive").sum())
        n_flag = int(df["read_carefully"].sum())
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Comments", n_total)
        m2.metric("Positive", f"{n_pos / n_total:.0%}")
        m3.metric("Average stars", f"{df['rating'].mean():.1f} ★")
        m4.metric("Read carefully", n_flag)

        scale = alt.Scale(domain=list(LABEL_COLORS), range=list(LABEL_COLORS.values()))
        color = alt.Color("label:N", title=None, scale=scale, legend=alt.Legend(orient="bottom"))
        c1, c2, c3 = st.columns(3)

        with c1:
            st.caption("Number of comments by label")
            counts = df["label"].value_counts().rename_axis("label").reset_index(name="count")
            count_bars = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("label:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("count:Q", title="Comments", axis=alt.Axis(tickMinStep=1)),
                color=color, tooltip=["label", "count"])
            count_text = count_bars.mark_text(dy=-8, fontWeight="bold").encode(text="count:Q")
            st.altair_chart(count_bars + count_text, width="stretch")

        with c2:
            st.caption("Average stars by label")
            avg = df.groupby("label")["rating"].mean().round(2).reset_index()
            bars = alt.Chart(avg).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("label:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("rating:Q", title="Average stars", scale=alt.Scale(domain=[0, 5]), axis=alt.Axis(tickMinStep=1)),
                color=color, tooltip=["label", "rating"])
            text = bars.mark_text(dy=-8, fontWeight="bold").encode(text=alt.Text("rating:Q", format=".1f"))
            st.altair_chart(bars + text, width="stretch")

        with c3:
            st.caption("Stars given, colored by label")
            stars = df.assign(stars=df["rating"].astype(int)).groupby(["stars", "label"]).size() \
                      .reset_index(name="count")
            stack = alt.Chart(stars).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("stars:O", title="Stars", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("count:Q", title="Comments", axis=alt.Axis(tickMinStep=1)),
                color=color, tooltip=["stars", "label", "count"])
            st.altair_chart(stack, width="stretch")
        st.caption("Look for positive comments with few stars, or negative comments with many stars. "
                   "Those are the comments listed below.")

        # ---- 3. Read these carefully --------------------------------------------
        st.subheader("Read these carefully")
        st.caption("The label and the rating disagree (positive with a low rating, negative with a high rating), "
                   "or the label is unclear.")
        flagged = df[df["read_carefully"]].copy()
        if flagged.empty:
            st.info("Nothing flagged.")
        else:
            flagged["stars"] = flagged["rating"].astype(int).map(lambda r: "★" * r)
            st.dataframe(flagged[["comment", "stars", "label"]], width="stretch")

        # ---- All data -----------------------------------------------------------
        with st.expander("All feedback"):
            st.dataframe(df.drop(columns="read_carefully"), width="stretch")
        st.download_button("Download CSV", df.drop(columns="read_carefully").to_csv(index=False),
                           file_name="feedback.csv", mime="text/csv")
        st.caption("Note: on the free Streamlit Cloud, the saved file can disappear when the app restarts. "
                   "Download your CSV to keep it.")
