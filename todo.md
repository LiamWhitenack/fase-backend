# TODO

## Overview

Salaries will be calculated as a percentage of the current cap when they were given, but when projecting for the future assume that the cap will stay the same even though a player's percentage of the cap may change. This will mean that holding onto a player will usually result in an increase of value.

Unlike a company, a player's career is strictly bound by time, meaning that a stock would typically have little value towards the end of a career. To adjust for this, a player's earnings will be calculated on a game-by-game basis and dividends will be given out based on the percentage which a user owns. So if a user owns 1% of the stock of Cooper Flagg and Flagg makes $100,000 for one game, the user will make $1,000 (all fake money btw) in exchange for the inevitable move closer to the end of Flagg's career.

Before a user is able to interface with the app in a meaninful way, each player needs to have a market cap, probably estimated via ML forecasting methods.
There are two main types of estimates needed: mid-career and pre-draft.

### Mid-career

Rookie contracts and extensions/free agency signings should be handled differently.

#### Rookie contract

use season statistics to estimate whether or not the player will be cut before their 4th year is over. It's pretty rare that they are cut. If, however, they are likely to be cut, assume that their career will be all but over after they are.

#### Free agency / extensions

If a player's career is not projected to outlive their rookie contract, skip this. Otherwise, predict whether or not they will be a "max" player. The maximum salary is fixed by season but can be made convoluted by all-star selections, awards, or non-garunteed incentives. I don't have a clue on how to figure out what the max is yet but a binary classification model could be used to figure out if a player is a "max" player and the rest of the players would have to use a regression model.

The tricky part, from there, is figuring out how long the player's career will be. I think the most effective way of doing this will be finding similar players and how long their career lasted. This will fail for one-in-a-million types of players like Steph Curry or LeBron James, but those situations will be rare enough to not cause too much trouble. For most players, comparing things like their height and three point percentage will be informative for how long their career will last.

Even if we can assume that a player's career will continue 14 more years, it's not safe to assume that their salary will not have to decrease. There has to be some type of way to figure that out.

### Pre-draft

Making a pre-draft estimate of how well a player is going to do is initially simple enough, following these steps:

- Scrape tankathon's NBA big board to figure out which player is projected to go at which spot
- Estimate the average career earnings of each draft pick (and undrafted players)
  - this is non-trivial because it will require estimating how much longer a player will be active and assuming previous earnings for active or retired players who were drafted before 2011 (the reason being because I only have contract data from 2011+, although incomplete data is available from spotrac pre-2011)
- Each prospect's market cap will be equal to the average earnings of each draft pick

The above method does have some fatal flaws, though. There are years where the #1 pick is a clear and obvious favorite to make a fortune, like Cooper Flagg this last year. On other years, Zacharrie Risacher is the top pick and the entire draft is notoriously weak. There may be a way to fine tune the estimates based on sentiment by listening to a couple podcasts about the draft and getting a general idea of whether the draft is top-heavy, weak, deep, or any other combination. We could also automate that. I have no idea.

Another concern is the obvious limitations of a player's body compared with their stats. For example, Zion Williamson was the best college player and rookie I've ever seen, but it was clear even in college that his body was going to be in so many collisions and high-impact falls that he may not see a long career of max contracts. Compare that to Cooper Flagg, who has a prototypical all-star build and frame and doesn't seem to put his body in compromising positions when finishing at the rim or defending the paint. Given that players like Zion, Flagg, or even Wemby will likely be seeing a lot of attention in the stock market, this does seem important.

## Initial Setup

### Upload Team Seasons

Each team should have a season's associated data, including the win-loss record, money spent (including luxury tax and apron features), their playoff record, and upcoming draft picks for that year.

### Upload Games / Player Games

this will require an absurd amount of calls to the `nba_api` and will make our db much, much bigger. So let's hold off on it! It's more of a nice-to-have, anyway. Until we add these, we can easily just upload and download copies of the db to github

### Continue downloading big board stats (2023 and earlier)

I am very happy to learn that quite a bit of data is available on tankathon, it just requires scraping. I'm trying to take it easy to avoid getting blocked. Let me know if you can help.

### Upload Player Career Statistics

this could be appended to the player table, I should have taken care of that earlier. Whoops.

## Research

I don't know much about how the stock market works and how purchasing it works as well as the way the stock's price should adjust given that someone wants to sell or buy. I heard something about AMM being a good method from ChatGPT? I'll probably ask my brother if he's interested in figuring this out and helping.

## Data Sources

- Basketball Reference: only for awards, they make it very difficult to scrape the website
- Spotrac: by downloading CSV's with a premium subscription, including minor automations
- NBA API: via the `nba_api` python package
