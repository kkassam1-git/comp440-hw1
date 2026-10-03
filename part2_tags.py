"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from embed_tags import clean_tag, load_embeddings
from load_data import load_all

MY_MOVIE = 858  # the student's claimed movie: Godfather, The (1972)
REPO = Path(__file__).parent
FIGURES = REPO / "figures"


def my_ten_movies():
    """movieIds from the "My ten movies" slot of WRITEUP.md, read the way judge.py reads it."""
    slot = (REPO / "WRITEUP.md").read_text(encoding="utf-8").split("**My ten movies")[-1]
    return [int(n) for n in re.findall(r"^\s*(\d+)", slot.split("\n**")[0], re.M)]


def per_month(frame):
    months = pd.to_datetime(frame["timestamp"], unit="s").dt.to_period("M")
    return months.value_counts().sort_index()


def when_figure(my_ratings, my_tags, title):
    """figures/part2_when.png: tag applications and ratings per month, one panel each."""
    tag_months, rating_months = per_month(my_tags), per_month(my_ratings)
    span = pd.period_range(min(tag_months.index.min(), rating_months.index.min()),
                           max(tag_months.index.max(), rating_months.index.max()), freq="M")
    tag_months = tag_months.reindex(span, fill_value=0)
    rating_months = rating_months.reindex(span, fill_value=0)
    x = span.to_timestamp()

    # two panels sharing the time axis, because the two counts are on different scales
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    top.plot(x, tag_months.values, color="#2a78d6", linewidth=1.5)
    top.set_ylabel("tag applications per month")
    bottom.plot(x, rating_months.values, color="#eb6834", linewidth=1.5)
    bottom.set_ylabel("ratings per month")
    bottom.set_xlabel("month the tag or rating was submitted")
    for ax in (top, bottom):
        ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(bottom=0)
    fig.suptitle(f"When did the tags and the ratings on {title} arrive?")
    fig.text(0.5, 0.005, f"Top: tag applications per month. Bottom: ratings per month. "
             f"MovieLens compact set, movieId {MY_MOVIE}.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / "part2_when.png", dpi=150)
    plt.close(fig)

    # the numbers behind the figure, by year so they fit on screen
    by_year = pd.DataFrame({"tag applications": tag_months, "ratings": rating_months})
    by_year = by_year.groupby(by_year.index.year).sum()
    # the same counts binned by year, as a second figure the student asked for
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    top.bar(by_year.index, by_year["tag applications"], color="#2a78d6", width=0.8)
    top.set_ylabel("tag applications per year")
    bottom.bar(by_year.index, by_year["ratings"], color="#eb6834", width=0.8)
    bottom.set_ylabel("ratings per year")
    bottom.set_xlabel("year the tag or rating was submitted")
    bottom.set_xticks(by_year.index[::2])
    for ax in (top, bottom):
        ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"When did the tags and the ratings on {title} arrive, year by year?")
    fig.text(0.5, 0.005, f"Top: tag applications per year. Bottom: ratings per year. "
             f"MovieLens compact set, movieId {MY_MOVIE}.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURES / "part2_when_by_year.png", dpi=150)
    plt.close(fig)

    print("  figures/part2_when.png and figures/part2_when_by_year.png written; "
          "the same counts by year:")
    print(f"    {'year':<6} {'tag applications':>16} {'ratings':>8}")
    for year, row in by_year.iterrows():
        print(f"    {year:<6} {row['tag applications']:>16,} {row['ratings']:>8,}")

    # monthly numbers the student asked for, to check readings taken off the figure
    print("  monthly numbers (months with none count as zero):")
    for name, months in (("ratings", rating_months), ("tag applications", tag_months)):
        first = months[months > 0].index.min()
        for label, start, end in (("before 2015", first, pd.Period("2014-12", "M")),
                                  ("2015 on", pd.Period("2015-01", "M"), months.index.max())):
            window = months[(months.index >= start) & (months.index <= end)]
            peak = window.idxmax()
            print(f"    {name:<17} {label:<12} {start}..{end}: "
                  f"mean {window.mean():>6.1f} per month, median {window.median():>5.1f}, "
                  f"peak {window.max():>4,} in {peak}")


def score(tags_df, ratings_df, movies_df):
    """The student's score(movie, tag), over tags after clean_tag(): stripped and lowercased.

    f(m, t)   = number of people who applied tag t (any raw string that cleans to t) to m
    sim(t, u) = cosine similarity of the all-mpnet-base-v2 vectors of t and u
    weight    = sum over the movie's other tags u of sim(t, u) * f(m, u),
                divided by the sum of f(m, u) over those same tags
    score     = f(m, t) * weight
    """
    index, vectors = load_embeddings()
    people = (tags_df.assign(tag=clean_tag(tags_df["tag"]))
              .groupby(["movieId", "tag"])["userId"].nunique()
              .rename("people").reset_index())
    parts = []
    for movie, group in people.groupby("movieId", sort=False):
        v = vectors[group["tag"].map(index).to_numpy()].astype(np.float32)
        f = group["people"].to_numpy(dtype=np.float64)
        sim = v @ v.T
        # leave each tag out of its own neighbourhood
        neighbours = sim @ f - np.diag(sim) * f
        others = f.sum() - f
        with np.errstate(invalid="ignore", divide="ignore"):
            weight = np.where(others > 0, neighbours / others, np.nan)
        parts.append(group.assign(weight=weight, score=f * weight))
    out = pd.concat(parts, ignore_index=True)
    return out.sort_values(["movieId", "score"], ascending=[True, False],
                           ignore_index=True)


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MY_MOVIE, "title"]
    mine = tags[tags.movieId == MY_MOVIE]
    print(f"  {title}: {(ratings.movieId == MY_MOVIE).sum():,} ratings, "
          f"{len(mine):,} tag applications")
    # raw tag strings, exactly as typed: no case or spacing merged
    counts = mine["tag"].value_counts()
    for tag, n in counts.items():
        print(f"    {n:>5,}  {tag}")

    print("== (2) up close ==")
    my_ratings = ratings[ratings.movieId == MY_MOVIE]
    when_figure(my_ratings, mine, title)

    print("  who added each tag:")
    per_user = mine.groupby("userId").size().sort_values(ascending=False)
    print(f"    {len(per_user):,} people tagged it; the ten heaviest:")
    print(f"    {'userId':>8} {'applications':>12} {'share':>7}")
    for user, n in per_user.head(10).items():
        print(f"    {user:>8} {n:>12,} {n / len(mine):>7.1%}")

    print("  how the taggers rated it:")
    # top ten raw tag strings; mean rating of this movie by the people who applied each
    # tag (and also rated it) beside the mean of everyone else who rated it
    stars = my_ratings.set_index("userId")["rating"]
    print(f"    {'tag':<18} {'taggers':>7} {'who rated':>9} {'their mean':>10} "
          f"{'others':>7} {'others mean':>11}")
    for tag in counts.head(10).index:
        users = mine.loc[mine.tag == tag, "userId"].unique()
        theirs = stars[stars.index.isin(users)]
        others = stars[~stars.index.isin(users)]
        print(f"    {tag:<18} {len(users):>7,} {len(theirs):>9,} {theirs.mean():>10.2f} "
              f"{len(others):>7,} {others.mean():>11.2f}")

    print("== (3) my definition ==")
    scores = score(tags, ratings, movies)
    print(f"  {len(scores):,} rows over {scores.movieId.nunique():,} movies; "
          f"{scores.score.isna().sum():,} rows have no score (the movie has no other tag)")
    print(f"  top 15 for {title}:")
    print(f"    {'tag':<24} {'people':>6} {'weight':>7} {'score':>8}")
    for _, row in scores[scores.movieId == MY_MOVIE].head(15).iterrows():
        print(f"    {row.tag:<24} {row.people:>6,} {row.weight:>7.3f} {row.score:>8.2f}")

    print("== (4) cleaning ==")
    print("  rule (the student's, the judge's too): strip spaces at the ends, then lowercase")
    cleaned = tags.assign(clean=clean_tag(tags["tag"]))
    print(f"  {tags.tag.nunique():,} raw tag strings in, "
          f"{cleaned.clean.nunique():,} distinct tags out")
    merged = cleaned.groupby("clean").agg(strings=("tag", "nunique"),
                                          applications=("tag", "size"))
    merged = merged[merged.strings > 1].sort_values("applications", ascending=False)
    print("  the five mergers that absorbed the most applications:")
    for clean, row in merged.head(5).iterrows():
        variants = cleaned.loc[cleaned.clean == clean, "tag"].value_counts()
        parts = ", ".join(f"'{t}' {n:,}" for t, n in variants.items())
        print(f"    {clean:<16} {row.applications:>7,} applications from {parts}")

    print("== (5) scores.csv ==")
    judged = pd.read_csv(REPO / "judge" / "movies.csv", keep_default_na=False)
    asked = [(int(m), t) for m, tags_ in zip(judged["id"], judged["tags"])
             for t in tags_.split("|") if t]
    vocabulary = {t.strip() for t in (REPO / "judge" / "vocabulary.txt")
                  .read_text().splitlines() if t.strip()}
    ten = my_ten_movies()
    on_ten = (tags[tags.movieId.isin(ten)].assign(tag=clean_tag(tags["tag"]))
              .query("tag in @vocabulary")[["movieId", "tag"]].drop_duplicates())
    asked += list(on_ten.itertuples(index=False, name=None))
    asked = pd.DataFrame(sorted(set(asked)), columns=["movieId", "tag"])
    out = asked.merge(scores[["movieId", "tag", "score"]], on=["movieId", "tag"], how="left")
    print(f"  {len(asked):,} movie-tag pairs asked for ({judged.id.nunique()} movies in "
          f"judge/movies.csv plus {len(ten)} of mine); "
          f"{out.score.notna().sum():,} have a score, {out.score.isna().sum():,} do not")
    out.dropna(subset=["score"]).to_csv(REPO / "scores.csv", index=False)
    print(f"  scores.csv written: {out.score.notna().sum():,} rows")

    print("== (6) the four rankings ==")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
