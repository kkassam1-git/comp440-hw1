"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from load_data import load_all
from part2_tags import score as movie_score

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

MIDPOINT = 2.5  # the student's line between a high and a low rating
# the student's ten users: themselves, plus nine drawn at random (seed 440) from the users
# with at least 10 tag applications
USERS = [ME, 10611, 21565, 61181, 67478, 120553, 132153, 144977, 150744, 158502]


def contributions(ratings, tags, movies, users=USERS):
    """One row per user, movie and tag: (rating - 2.5) * the Part 2 score(movie, tag)."""
    movie_scores = movie_score(tags, ratings, movies).dropna(subset=["score"])
    theirs = ratings[ratings["userId"].isin(users)]
    pairs = theirs.merge(movie_scores[["movieId", "tag", "score"]], on="movieId")
    pairs["contribution"] = (pairs["rating"] - MIDPOINT) * pairs["score"]
    return pairs[["userId", "movieId", "rating", "tag", "contribution"]]


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame, users=USERS,
          parts=None):
    """The student's score(user, tag).

    For each movie m the user rated and each tag t on m:
        contribution = (rating - 2.5) * score(m, t), the Part 2 movie score
    score(user, t) = sum of contributions over the user's movies, divided by the number of
                     movies the user rated (all of them, not only those carrying t)"""
    if parts is None:
        parts = contributions(ratings, tags, movies, users)
    rated = ratings[ratings["userId"].isin(users)].groupby("userId").size().rename("n_rated")
    out = (parts.groupby(["userId", "tag"])["contribution"].sum().rename("total")
           .reset_index().join(rated, on="userId"))
    out["score"] = out["total"] / out["n_rated"]
    return (out[["userId", "tag", "score"]]
            .sort_values(["userId", "score"], ascending=[True, False], ignore_index=True))


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    scores = score(ratings, tags, movies)
    print(f"  {len(scores):,} rows over {scores.userId.nunique():,} user(s)")
    print(f"  my ten best tags (userId {ME}):")
    for row in scores[scores.userId == ME].head(10).itertuples():
        print(f"    {row.tag:<28} {row.score:>8.3f}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
