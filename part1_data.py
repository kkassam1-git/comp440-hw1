"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import csv
import gzip
import statistics
from collections import Counter
from pathlib import Path

from load_data import load_all

DATA = Path(__file__).parent / "data"

FULL_RATINGS = 32_000_204  # all MovieLens 32M ratings, from data/README.md


def spread(counts, label):
    print(f"  {label:<28} median {counts.median():>8,.0f}   "
          f"min {counts.min():>6,}   max {counts.max():>7,}")


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    for name, frame in (("ratings", ratings), ("tags", tags),
                        ("movies", movies), ("links", links)):
        print(f"  {name:<8} {len(frame):>10,} rows")
    print(f"  distinct users  (in ratings) {ratings.userId.nunique():,}")
    print(f"  distinct movies (in ratings) {ratings.movieId.nunique():,}")
    print(f"  share of all {FULL_RATINGS:,} ML-32M ratings: "
          f"{len(ratings) / FULL_RATINGS:.1%}")

    print("== (b) spread ==")
    spread(ratings.groupby("userId").size(), "ratings per user")
    spread(ratings.groupby("movieId").size(), "ratings per movie")
    # only users and movies with at least one tag appear in these two
    spread(tags.groupby("userId").size(), "tag applications per user")
    spread(tags.groupby("movieId").size(), "tag applications per movie")
    raters = ratings.userId.unique()
    taggers = tags.userId.unique()
    n_both = len(set(raters) & set(taggers))
    print(f"  users who rated anything: {len(raters):,}; of them ever applied a tag: "
          f"{n_both:,} ({n_both / len(raters):.1%})")

    print("== (c) top tags, two ways ==")
    # raw tag strings, exactly as typed: no case or spacing merged
    by_tag = tags.groupby("tag").agg(applications=("userId", "size"),
                                     users=("userId", "nunique"))
    for col, title in (("applications", "by number of applications"),
                       ("users", "by number of distinct users")):
        print(f"  top 20 {title}:")
        top = by_tag.sort_values([col, "applications"], ascending=False).head(20)
        print(f"    {'tag':<30} {'applications':>12} {'users':>7}")
        for tag, row in top.iterrows():
            print(f"    {tag:<30} {row.applications:>12,} {row.users:>7,}")

    print("== (d) two checks ==")
    # the student's route: read the raw .csv.gz files with the standard library
    # (gzip, csv, statistics), with no pandas and no load_data.py
    checks = (
        ("median tag applications per user", "tags.csv.gz", "userId",
         tags.groupby("userId").size().median()),
        ("median ratings per movie", "ratings.csv.gz", "movieId",
         ratings.groupby("movieId").size().median()),
    )
    for label, filename, key, pandas_value in checks:
        counts = Counter()
        with gzip.open(DATA / filename, "rt", newline="") as f:
            for row in csv.DictReader(f):
                counts[row[key]] += 1
        raw_value = statistics.median(counts.values())
        verdict = "MATCH" if raw_value == pandas_value else "DIFFER"
        print(f"  {label:<34} pandas {pandas_value:>8,.1f}   "
              f"raw csv {raw_value:>8,.1f}   {verdict}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
