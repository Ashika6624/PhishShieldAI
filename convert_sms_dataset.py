import pandas as pd

# Read the SMS Spam Collection dataset
df = pd.read_csv(
    "dataset/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "email_text"]
)

# Save as CSV
df.to_csv("dataset/phishing_email.csv", index=False)

print("Dataset converted successfully!")
print(df.head())
print("Total Emails:", len(df))