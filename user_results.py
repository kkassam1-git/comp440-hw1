"""
The user viewer: what score(user, tag) says about each of the student's ten users.

    uv run python user_results.py      # writes user_results.html

The student's design: for each user, the top 10 tags with their score, and under each tag
the five movies that contributed most to that score, with the rating the user gave each.
"""

import html
from pathlib import Path

import pandas as pd

from load_data import load_all
from part3_users import USERS, add_me, contributions, read_my_ratings, score

REPO = Path(__file__).resolve().parent
TOP_TAGS, TOP_MOVIES = 10, 5

CSS = """:root { --bg: #ffffff; --ink: #1a1a1a; --muted: #555555; --line: #cccccc; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #1a1a19; --ink: #f2f2f2; --muted: #b8b8b8; --line: #444444; } }
body { font-family: Helvetica, Arial, sans-serif; margin: 20px; background: var(--bg);
       color: var(--ink); }
table { border-collapse: collapse; margin: 4px 0 14px; }
th, td { border: 1px solid var(--line); padding: 3px 8px; text-align: left; }
.muted { color: var(--muted); }
tr.spike td { background: #f8d4d4; color: #1a1a1a; }"""
SPIKE = 0.5  # the student's flag: one movie supplies more than half of a tag's total


def build():
    ratings, tags, movies, _ = load_all()
    mine, _ = read_my_ratings()
    ratings = add_me(ratings, mine)
    parts = contributions(ratings, tags, movies, USERS)
    scores = score(ratings, tags, movies, USERS, parts=parts)
    titles = movies.set_index("movieId")["title"]
    stats = ratings[ratings.userId.isin(USERS)].groupby("userId")["rating"].agg(["size", "mean"])
    out = []
    for user in USERS:
        rows = []
        for t in scores[scores.userId == user].head(TOP_TAGS).itertuples():
            every = parts[(parts.userId == user) & (parts.tag == t.tag)]
            total = every["contribution"].sum()
            top = every.sort_values("contribution", ascending=False).head(TOP_MOVIES)
            rows.append((t.tag, t.score, [(titles[m.movieId], m.rating, m.contribution,
                                           m.contribution / total)
                                          for m in top.itertuples()]))
        out.append((user, int(stats.loc[user, "size"]), stats.loc[user, "mean"], rows))
    return out


def render(users):
    body = ["<h1>User viewer</h1>",
            '<p class="muted">Per user: the top %d tags under score(user, tag), and under each '
            "the %d movies contributing most, with the user's rating and the contribution "
            "(rating − 2.5) × score(movie, tag), and that movie's share of the sum of all the "
            "tag's contributions. A row is light red when one movie supplies more than half."
            "</p>" % (TOP_TAGS, TOP_MOVIES)]
    for user, n, mean, rows in users:
        body.append("<h2>User %d</h2><p class=\"muted\">%d ratings, mean %.2f</p>"
                    % (user, n, mean))
        for rank, (tag, value, films) in enumerate(rows, 1):
            body.append("<h3>%d. %s — %.3f</h3>" % (rank, html.escape(tag), value))
            body.append("<table><tr><th>Movie</th><th>Rating</th><th>Contribution</th>"
                        "<th>Share of the tag's total</th></tr>%s</table>" % "".join(
                            "<tr%s><td>%s</td><td>%.1f</td><td>%.2f</td><td>%.0f%%</td></tr>"
                            % (' class="spike"' if share > SPIKE else "",
                               html.escape(title), r, c, 100 * share)
                            for title, r, c, share in films))
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>User viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n%s\n"
            "</body>\n</html>\n" % (CSS, "\n".join(body)))


if __name__ == "__main__":
    page = REPO / "user_results.html"
    page.write_text(render(build()), encoding="utf-8")
    print("wrote %s" % page)
