# HW1 writeup

**Name:** Kaif Kassam
**Date:** 2026-09-17

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** Godfather - the most used tags would probably be #Italian-Mafia, #Drama, #Saga

**(1) Why you think so:** These terms broadly encompass the kind of movies Godfather falls under - I feel they would be the most probable words that come to mind for a general audience when thinking of this movie.

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** 10 people

**(2) Why you think so:** I have never added a tag for a movie myself and don't know anyone who actively does in my circle. Given I'm not exactly a big fan of movies, my estimate may be conservative. But I'm still quite sure that it's a low percentage of people who add tags.

**(3) Can one person's tags take over a movie's tag list? Yes or no:** NO

**(3) Why you think so:** I would assume we only count one "unique tag" per user for a movie - repeated tags by the same user would not be useful for the same movie

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** I did read through it, I dont fully understand the process - but it seems the process that it uses and what makes sense to me is to set a threshold for users in terms of number of ratings and use that as a way to filter down to a smaller subset of the data that is of more use to our research context.

**One rule I considered and rejected, and why:** Random samples of the 32 million could be an approach. It could, and probably would, leave out important data on taggers who we are interested in.

**One interesting thing from `data/README.md`:** I found the broader choices (i.e going for 20+ ratings as a threshold only from the top 4,000 movies selected) that went into creating the compact data set interesting - there is quite some thought to it. It seems to be obvious once you understand it, but it is definitely intentionally ordered this way to extract a dataset that best fits the study's needs.

**How the script's rule differs from mine, and what each keeps that the other drops:** I was thinking of just fitlering the users that met the ratings thredhold and then deal with whatever movies fell in that pool - I am wondering why we didn't filter the most tagged movies instead of filtering the top rated movies - what happens to the more niche movies that have higher tag counts in our study? The script is leaving out more niche (high tagged) movies that do not fall in the top 4000 - my approach would have had no ordering of the movies by any variable since the movies would have just been whatever fell under the reviewd ones for the users who had 20+ ratings in the original dataset. Later thought: I didn't think about how I would have to hit the 5 million number - I just assumed it would be below 5 million total ratings - maybe it would make sense to have my rule filter the movies in the pool by most ratings until we hit the closest difference to 5 million ratings below or above.

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** Median tag applications per user, came from part1_data.py. Raw file with a different library. Yes it matched. Yes median barely moves across 6 row changes, but if you konw that pandas is going to drop them then it should not be a problem

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** It looks at median ratings per movie, comes from part1_data.py, also takes on the raw file with a different library approach, and Yes it matched

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** Godfather (1972). I think it's one of the best works of its era, the cinematography is really impressive and so is the intention behind choice in the plot, acting, and scenes.

**Its most misleading tag in the count-ordered list, and why it misleads:** atmospheric might be the misleading in the list, partly because I'm not sure what is trying to descibe in a crime, mafia movie like The Gofather

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** This is what I noticed - the reviewing is the common 5 star scale, except here the scale has descriptors added to it (awful, poor, okay, good, must watch); there are 10 possible cases going from 0 to 5 stars in intervals of 0.5.

Adding a tag is as simple as typing it in and clicking add. The page shows you how many other occurences of your unique tag have been logged into the system before and the tags are all listed in order of their frequency. This is similar to the social influence scenario we read about in the reading in class. Adding a tag also has an additional step where you add whether the tag is something you like about the moive, dislike, or feel neutral about.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** I think this is more about the tool than it is about the movie. Movielens was released in 1997, so I suppose that's the start of the x axis. Godfather is a classic a lot of people go back to, so I'm going to assume it has a consistent number of tags over the years with some outbursts resulting from references becoming popular in social media or broad experiences like COVID pushing people into watching more movies.
**The figure, what it shows:** There are no tags before 2006 - possibly because movielens did not have that as a feature. The average number of ratings and tags does increase over time. There is a giant increase in ratings in the year 2015, more double the last peak in 1999 and more than 8 times what seems to be the average prior to the year at around 25 ratings per month. Tags also go up but barely compared to ratings.

A rapid increase in tags is seen in 2020, peaking in 2021. Ratings also increase, but no where in proportion to tags. Over all, ratings and tags seem volatile over the time series we're looking at.

**Two interesting details I learned up close that the counts did not show:** The heaviest tagger has 7.45x the tags as the next one. I meant to say 1.1% earlier on and not 11% - with that in mind, if we remove the heaviest as an outlier, the range is around 1-2% in the top 10 list.

THe other thing I found interesting is the most people who tagged alos rated. On average, even though the sample size are magnitudes smaller, the taggers have higher mean ratings than others. All the means for the non-taggers are about 4.26 across all tog tags.

part2_tags.py from section 2

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** For part 0, I did not account for one person submitting many different tags and it seems that for this movie, that number can go beyond 300. So in that sense a single person's tags can influence the taggine of a movie but I would not say take over, since this does not boost the frequency of unique tags and users can see that.

The number of tags is way less consistent than I thought, it is definitely volatile outburts with one really large outlier.

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** 1. The most important factor would be the frequency of the tag, how many individual have tagged it such. 2. Tags should be compared after being classified as "very simliar" - so essentially, case or general grouping i.e. mafia or Mafia or Italian Mafia. The tag is score is weighted by its the density of tis cluseter, the more similar tags there are in its cluster, the higher its score. For mafia we take it's similarity to each of the movie'es other tags and multiply by the frequency of those tags, sum the products together and divide by total frequency of all other tags

**One definition I considered and rejected, and why:** I didn't actively weight another decision in this process, but I did take into account how I did not want uniqueness of the tag to be part of my rule since I do not think that is indicative of a "good" tag - rather in some cases may be the opposite. So, we could say I rejected this one.

**Which tags I merged as the same tag, which I kept apart, and why:** I chose to merge tags that end up being the same after formatting to lower-case. Italian mafia and mafia remain two different tags in this case, since collapsing them into one would just double up my rule's score given the similarity element is already being dealt with by the clustering approach. There are limitations where two tags that are the same like scifi & sci-fi still remain separate, but I would not be too worried about them since their distance in the cluster will likely be very close and push its weight up.

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

It may not seem intuitive right away, but I dont think  uniqueness is a good way to score a tag here. If a tag has many others "cousins" in its cluster,  that may share a similar intention of the tagger - then that I'd say is a good indicator of the general consensus of the public on the movie, and therefore  proves that it's a good tag.

People represent the frequency/popularity of the tag and the weight, as I intended, is an indication of what the movie is about and how the tag covers that. Classic for exmaple ahs the most people but a low weights sicne it does not fit into the broader "mafia" cluster I believe and italian mafia has fewer people but a much higher weight.

My rule gains in supporting a central move description theme and bumping up tags that do a good job at fitting to that, compared to juste generic tags. This, again, is subjective and depends on how one determines a "good" tag in their view.

My rule does lose out on not being able to look into catalog wide trends, it does not account for tag spread and genericness across the catalog and is limited scoring to only one movie.

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

858, Godfather, The (1972)
254726, Dune (2021)
134130, The Martian (2015)
4995, Beautiful Mind, A (2001)
106782, Wolf of Wall Street, The (2013)
148626, Big Short, The (2015)
49272, Casino Royale (2006)
278702, Glass Onion: A Knives Out Mystery (2022)
159858, The Conjuring 2 (2016)
122906, Black Panther (2017)

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

858: mafia, Al Pacino, Mafia, crime, classic, great acting, Marlon Brando, masterpiece, organized crime, atmospheric
254726: sci-fi, politics, based on a book, space travel, visually appealing, immersive, atmospheric, boring, far future, space opera
134130: space travel, Survival Instinct, space, scientific, sci-fi, Space, Near Future, realistic, science, mars
4995: genius, inspirational, math, true story, intelligent, mental illness, schizophrenia, mathematics, twist ending, psychology
106782: Leonardo DiCaprio, Nudity (Topless), drugs, Wall Street, based on a true story, Nudity (Full Frontal), great acting, Martin Scorsese, visually appealing, Funny
148626: finance, wallstreet, Christian Bale, financial crisis, banking, true story, political, breaking the fourth wall, makes good points, interesting
49272: action, James Bond, spy, 007, espionage, torture, Daniel Craig, spies, gambling, poker
278702: mystery, murder mystery, capitalism, nonlinear, good writing, not consistent, no character development, twists & turns, chekhov's gun, whodunnit
159858: demon, Demon, supernatural, the conjuring, based on a true story, paranormal investigation, haunted house, England, 70s, British accents
122906: Africa, Marvel, MCU, superhero, social commentary, strong female characters, great villain, predictable, diverse cast, great costumes

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** I briefly considered using time stamp dat on these tags as a potential judging criterion but I don't think difference in when tags were tagged onto would be that useful, it may just make the reading more blurry. i did not think of how the judge could have never done that anyways, making this not a useful approach inherently, given the data we need is used here.

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** Score() comes closest

From `agreement.py`:

| method | of 5 | movies |
| --- | --- | --- |
| score() | 3.44 | 110 |
| popularity | 3.31 | 110 |
| your own order | 2.90 | 10 |
| best possible | 4.38 | 110 |

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

The judge skill is built from multiple md files. judge/README.md holds the rules, breakind down what each file is for, how to run, and what to share with the user. SKILL.md directs claude to the readme file.

judge/system.md instructs the model - system.md is the file identical across all students. THe answers are restricuted to tag, rating line 1 to 5.

judge/ criterion.md is my input into the judge skill, part of the prompt the judge sees.

movies.csv - 100 movies the judge rates

vocabulary.txt - the 300 tags allowed to chooose from

judge.py is the central script that runs everything together. 5 sessions run in parallel adding my ten movies to the list (from WRITEUP.md) - returns the response for each movie with the relvant information

results are part of judge/ratings_movies.csv, log is a short two line summary from the run

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

Checks if the items files exits, confirms placeholder is replaced by my criterion, reads all items including my 10 movies from writeup.md, prints out what crtierion it read and how many ratings it's using. runs a claude -p session per movie, 5 in parallel (no tools or no memory per session), returns to reading the tag,rating lines, checks for movies that may hvae fewer ratings returned than expecetd by the model, writes the csvs and prints the summary lines into log

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

A skill gives you a layered approach to any task with integrated script, checks, system prompts, and a way to package the response - all being guide by the boundaries set forth in the skill. It's a more cohesive package as a whole that is effectively repeatable across multiple scenarios that may require different inputs or outputs - without the fear of it breaking, since it's designed such that is can evolve and repeat around the needs presented to the skill.

My mind goes straight to data pipelines that I was working with over the summer - such financial reports and data, when integrated into an agent should be supported by guardrails and fixed steps on security and data quality checks - even if the input from the user using the skill may differ from prompt to prompt.

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** Seeing the disagreement list is useful and comparing it to the raw tag applicaiton list helps with verifying the results of the disgreement list, i.e. father-son relationship is ranked number 3 by the judge for The Godfather but varies drastically from the score() rank 38, given it only shows up twice in the list.

The massive lists is defintely what is coming in my way, I barely found the disagreement list and a lot of it seems to be noise we can remove and build into more targetted lists for movies with filters built in to assist with navigating to information we need.

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** The disagreement table and four rankings were in the noise of dat aon the page, every raw tag application was listed out, -  the raw list is now under a drop down that summarizes it as number of applications per these many users

**Improvement 2:** the disagreement table was buried at the end of each movi'es section - after the reankings and raw tag lists, now it's the first thing under the movie's title. The table usedd to spot the issues is immediately visible to the user.

**Improvement 3:** A search bar should help pick movies that should be analyzed in this way and add a dropdown/collapse feature for each movie (the headings/subheadings collpase information accordingly - what if we were looking at a list of 50 movies. It shows the search bar which was not there before

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** father-son relationship is ranked number 3 by the judge for The Godfather but varies drastically from the score() rank 38, given it only shows up twice in the list. The judge recofgnized the "father-son relationship" is a descriptor of the The Godfather but does not account for the frequency of its occurence as a tag.

**Disagreement 2:** The 2nd is "Martin Scorsese" (Wolf of Wall Street) - judge ranks it at 35, and score() at 2nd, a 33 point gap. This represents an opposite trend coming into play as the last one, where this tag is applied 82 times so score() pushed it to the top. A director's name is not a description of the central theme, which explains why the judge ranked it really low.

**Disagreement 3:** "Robert De Niro" from The Godfather. Score() ranked it at 10th and judge ranked it at 45 - that's another 35 gap there. Robert De Niro is not even in the first movie, which means the judge does a good job at not ranking it amongst tags that are "best" or "good" - score() fails to do that since it's a volume based calculation, the high number of applications pushed it to the top 10.

**One other high-level pattern in the results, and what you think is behind it:** Famous individuals acting or associated wtih movies get tagged constantly on these movies, so we see it occue with Leonardo Di Cpario or ANthony Hopkins - where the tag does not do much to describe the theme or experience of the movie - pushing it lower in the judge's ranking. Score() is a function of frequency be design, and clusterin here cannot extract actors names from other tag groups which makes it such that the weighting does not drop the tags position either to match that of the judge.

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:**

1. I was wrong about this. Two of three are generic praise tags, not content descriptors, it seems  frequent tags skew toward crowd praise and credits, not toward what a movie is specifically about - which is how I would approach tagging personally.

2. I was off by a lot - the number is much higher in the compacted data set given how it is constructed.

3. It seems one person can take over the movies tag list overall, but still not the ranking of tags since the same tag does not appear twice under the same user.

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

858, Godfather, The (1972), 4.5
254726, Dune (2021), 4.5
134130, The Martian (2015), 5.0
4995, Beautiful Mind, A (2001), 4.0
106782, Wolf of Wall Street, The (2013), 4.5
148626, Big Short, The (2015), 4.5
49272, Casino Royale (2006), 3.5
278702, Glass Onion: A Knives Out Mystery (2022), 3.5
159858, The Conjuring 2 (2016), 4.0
122906, Black Panther (2017), 4.5
50872, Ratatouille (2007), 3.5
96079, Skyfall (2012), 4.0
91658, Girl with the Dragon Tattoo, The (2011), 4.5
138036, The Man from U.N.C.L.E. (2015), 4.5
79224, Karate Kid, The (2010), 3.5
93840, Cabin in the Woods, The (2012), 2.5
61024, Pineapple Express (2008), 4.0
140110, The Intern (2015), 4.5
49530, Blood Diamond (2006), 5.0
92259, Intouchables (2011), 4.5

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

Im going to set the midpoint at 2.5 - subtract it from the rating to see where it stands from this threshold line then multiply it with my score to come up with a new score - then when putting together movies simply sum the movies and divided by the number of movies.

A tag as I described should reflect the movies a person has rated the highest, weighted by how much they liked them (so rating itself). Using the 2.5 threshold, in the middle, is a way to define above or below this middle ground. I resuse the part 2 score() formula since that measures relevance of tags to movies and then extends to users.

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

From `part3_users.py` section (2): sci-fi 6.933, space 6.092, mafia 5.172, great acting 4.548, space travel 4.524, funny 4.481, leonardo dicaprio 4.409, visually appealing 4.147, based on a true story 4.117, true story 3.858.

Looks lije the formula is doing exactly what it should and pushed up the movies I rated higher up and those which would have had higher scores, I'm surprised none of those (drama, crime, action, thriller, spy) showed up though. they do describe my taste

**What my user viewer shows and why I chose that (about 100 words):**

My user viewer shows the ten users and their top 10 associated tags under score(user,tag). The 5 movies that contributed the most to this tag are under each one. The ratings they were given and the actual contribution number too.

I designed it such that a tag score is provided with context and how the movies contributed to those tags, highlight extremes or other patterns in how these tags show up with their scores.

**What I put in the description column for a person, and why (about 150 words):**

how many movies they rated in total, their mean rating, their top 5 highest rated movies (title plus rating like before), and then what portion of the ratings in their movies falls under a 3.0 threshold or above.

Rating counts and mean shows how many ratings a person has and on average how do they rate.

Top 5 highest rated titels provides context for the judge to determine the kind of movies the user likes.

Share above/below 3.0 shows how strong of a singal, up or down, a particular rating is.

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

The people paragraph looks across movies and rewards tags that recur basd on pattern instead of tags that solely fit one highly rated movie. The movie criterion does not look across movies , since it judges single movies from my understanding, nothing to compare against.

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

20 seemed to be the right amount that didn't use too much copute but also provides a decent sized sample size. I split top10 + random so the comparison does not just look at top 10 by score() and tests whetehr score() may be missing tags the judge considers a good fit.

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

I want to change how score() uses contributions from multiple moves, to normalize the spiking effect from a single, dominant mvoies.

144977's sci-fi tag is 8.45  built mostly from Star Wars alone contributing 445.69, nearly double the next highest movie. User 67478's anime tag (14.523), by contrast, comes from five Ghibli films all rated 5.0, a genuinely consistent pattern. There's no component that tells a spike apart without manually going into the breakdwon.

I've thought through it and I cant seem to figure it out, I'd say just indicate on the viwer that this row has a movie contributiung +50% add a new column that shows percentage contribution if more than 50% turn light red

**Improvement 2: the same (about 150 words):**

After adding the share column, we see 14 rows across 10 users be highlighted for contributing 50% more. This is concentraed in users with fewer ratings, users with higher number of ratings do no suffer from this issue I noticed.  More ratings translate to  naturally more diluted shares per movie, all dependent on the sample we're looking at.

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:**

Not wrong, just that I answered a lot of questions in prior responses and it would just take me in circles sometimes.

**One call where you overrode Claude, and why:** Not anywhere from what I remember.

**What you would hand to Claude sooner next time:** N/A


**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** No, Claude asked me and I named atmospheric first

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** no

**Hours spent:** 8 hrs

**Anyone who helped you, or "no one":** N/A
