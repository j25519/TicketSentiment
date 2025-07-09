# Ticket Sentiment

Python script to perform basic sentiment analysis on exported ticket data in CSV format.

## How it works

1. Accepts CSV input (asks for the file name from user) and takes keywords or phrases from a `keywords.txt` file (one on each line)
2. Uses `nltk` library to do basic sentiment analysis on keywords (positive, negative, or neutral)
3. Tots up how many times each keyword has been used and how many times it's been used positively, negatively, or neutrally
4. Outputs three CSVs: one containing detailed raw data, one summary overview of counts in very human friendly format, and one looking at the context of keywords in tickets also with sentiment
5. The human readable summary sorts keywords by number of mentions and lists them out along with how many tickets with those keywords are positive, negative, or neutral
6. The context report lists ticket names and context for keywords with deduplication and sentiment analysis

If the script has been updated after this readme has been updated, it might do more stuff by now too.