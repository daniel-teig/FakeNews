## Inspiration
Most people agree that 'Fake News' are a significant problem in our society. With recent developments, it gets more and more apparent that something needs to be done in order to prevent, or at least mitigate their impact.
Conventional media, while being far from perfect is not involved in the spreading of fake news as much as social media. That's why we chose twitter for our target of operations.

## What it does
> A built in feature for twitter that allows the user to quickly identify and report misinformation. Once identified, a misinformed Tweet will be flagged and the correct information will be linked.

Tweets containing some type of factual information are compared to a database of verified true facts and fake facts.
An LSI-model (Latent Semantic analysis) compares the text of the tweet to the database and calculates the semantic similarity.

The user then receives one of the following judgments:
- Confirmed true fact, if the text matches a verified true fact in the database
- Confirmed fake fact, if the text matches a verified fake fact in the database
- Possible true fact, if the text is similar to a verified true fact in the database
- Possible fake fact, if the text is similar to a verified fake fact in the database
- Not enough information, if the similarity to all facts in the database is below a certain threshold

The database of facts can currently only be managed by an admin who can insert/approve new true or fake facts.

## How we built it
The backend is handled by python, using the gensim library for our NLP needs. Futhermore it's connected to an SQLite Database containing all the fake and true facts.
The frontend is a rebuild of the basic twitter UI for demonstrative purposes and is built with electron.

The functionality of checking a fact is implemented via a python script, that prompts the LSI-model to compare that fact to our entire database and then returning them sorted by similarity to it. If that similarity is high enough for one of them, we consider it to contain the same information.
Therefore we can then say whether the checked fact is true based on the fact in our Database having the truth value true or fake.


## Challenges we ran into
The Language processing libraries we managed to train and test over the weekend are not yet developed enough to support the system we initially envisioned. This system could just automatically detect and remove fake news. The main issue here is the comparison of different facts in the the same area. For example the facts "Apples are bigger than grapes." and "Apples are tastier than grapes." are almost impossible to distinguish, as they are semantically so close. That makes it very hard for us to determine if the given fact actually has the same semantic content as one of the facts in our Database or just resembles it very closely while saying something completely different. That's why, for our system, it's important to always have the fake news fact and the actual corresponding fact in the database to minimize such errors.


## Accomplishments that we're proud of
We devised a system in which human flagged misinformation, combined with the true fact, can be used to match spreading misinformation and possibly mitigate it. Of course the challenges mentioned above make this an imperfect system as any other, but it can still be a useful tool in flagging and removing repeated offences.


## What we learned
We gathered basic insights into the natural language processing world and explored different models that could help us analyse text similarity.
Through this we have developed a great appreciation for all the work that has been done in this challenging field.


## What's next for Well Factually
The text comparator which currently uses an LSI-model could be improved using other techniques to find semantic similarities between given texts.

We would like to introduce a rating system for users to submit tweets or parts of tweets as true or fake facts. This system could involve a method of tracking the reliability of users ratings by comparing them to ratings of certain "verified" fact checkers. This enables us to consistently improve the database whilst also being protected against bots and malicious voters.


