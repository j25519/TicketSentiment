import csv
import os
import json
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER sentiment lexicon if needed
nltk.download('vader_lexicon')

# Set up sentiment analyser
sia = SentimentIntensityAnalyzer()

# Prompt for input CSV file name
input_csv = input("Enter the name of the CSV file (e.g., tickets.csv): ").strip()

# Read keywords.txt
with open("keywords.txt", "r", encoding="utf-8") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]

# Load persistent file name counter (I don't want to overwrite the output each time while I mess with things)
counter_file = "ticket_count.json"
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        count_data = json.load(f)
        file_count = count_data.get("count", 0) + 1
else:
    file_count = 1

# Save counter
with open(counter_file, "w") as f:
    json.dump({"count": file_count}, f)

# Output filenames
output_csv = f"Ticket_Sentiment_Analysis_{file_count}.csv"
summary_csv = f"Ticket_Keyword_Summary_{file_count}.csv"

# Read input CSV
with open(input_csv, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

# Output fields for the detailed CSV + reusable sentiment analysis cache
output_fields = ["Subject", "Sentiment", "Compound Score"] + keywords
results = []
ticket_data = []

# Analyse each row (now with caching for maximum efficiency!!!)
for index, row in enumerate(rows, start=1):
    subject = row.get("Subject", "").strip()
    ticket_id = subject if subject else f"[No Subject Row {index}]"
    description = row.get("Ticket Description", "")
    full_text_original = f"{subject} {description}".strip()
    full_text_lower = full_text_original.lower()

    if not full_text_lower:
        continue  # Skip empty rows

    # Get sentiment score
    scores = sia.polarity_scores(full_text_lower)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Count keywords
    counts = [full_text_lower.count(keyword) for keyword in keywords]
    results.append([ticket_id, sentiment, compound] + counts)

    # Cache for reuse later
    ticket_data.append({
        "subject": ticket_id,
        "sentiment": sentiment,
        "compound": compound,
        "text_lower": full_text_lower,
        "text_original": full_text_original
    })

# Write full ticket analysis CSV
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(output_fields)
    writer.writerows(results)

print(f"Raw data written to: {output_csv}")

# Aggregate keyword stats
keyword_stats = {
    keyword: {
        "Total Mentions": 0,
        "Positive": 0,
        "Neutral": 0,
        "Negative": 0
    }
    for keyword in keywords
}

# Tally up counts by keyword
for row in results:
    _, sentiment, _, *keyword_counts = row
    for i, count in enumerate(keyword_counts):
        if count > 0:
            keyword = keywords[i]
            keyword_stats[keyword]["Total Mentions"] += count
            keyword_stats[keyword][sentiment] += 1

# Convert to rows and sort by totals for human readable overview
sorted_stats = sorted(
    [[k, v["Total Mentions"], v["Positive"], v["Neutral"], v["Negative"]] for k, v in keyword_stats.items()],
    key=lambda x: x[1],
    reverse=True
)

# Write keyword summary CSV (less detailed but much more human readable output)
with open(summary_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Keyword", "Total Mentions", "Positive", "Neutral", "Negative"])
    writer.writerows(sorted_stats)

print(f"Keyword summary written to: {summary_csv}")

# Create list for context rows + keep track of tickets to dedup
context_rows = []
seen_pairs = set()

# Extract snippets from tickets using cache + dedup if multiple keywords match
for ticket in ticket_data:
    subject = ticket["subject"]
    sentiment = ticket["sentiment"]
    full_text = ticket["text_original"]
    full_text_lower = ticket["text_lower"]

    # Split into sentences with the power of regex to retain punctuation
    sentences = re.split(r"(?<=[.!?])\s+", full_text)

    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        matched_keywords = [kw for kw in keywords if kw in sentence_lower]

        if matched_keywords:
            snippet = sentence.strip()
            dedup_key = (subject, snippet)

            if dedup_key in seen_pairs:
                continue

            seen_pairs.add(dedup_key)
            keyword_combined = " + ".join(matched_keywords)  # Merge keywords so you don't just see the first one if deduped
            context_rows.append([keyword_combined, subject, sentiment, snippet])

# Write context CSV
context_csv = f"Ticket_Keyword_Context_{file_count}.csv"
with open(context_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Keyword(s)", "Subject", "Sentiment", "Snippet"])
    writer.writerows(context_rows)

print(f"Keyword context written to: {context_csv}")