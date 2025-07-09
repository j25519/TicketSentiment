# Ticket Sentiment

Python script to perform basic sentiment analysis on exported ticket data in CSV format.

## How it works

1. Accepts CSV input (asks for the file name from user) and takes keywords or phrases from a `keywords.txt` file (one on each line)
2. Uses `nltk` library to do basic sentiment analysis on keywords (positive, negative, or neutral)
3. Tots up how many times each keyword has been used and how many times it's been used positively, negatively, or neutrally
4. Outputs two CSVs: one containing detailed raw data and the other containing less data but much more human readable
5. The human readable summary sorts keywords by number of mentions and lists them out

At the time of writing, that's all it does.

If the script has been updated after this readme has been updated, it might do more stuff by now too.