import os
import pandas as pd

base_path = "dataset"

folders = {
    "20021010_easy_ham": "ham",
    "20021010_hard_ham": "ham",
    "20021010_spam": "spam"
}

emails = []

for folder, label in folders.items():
    folder_path = os.path.join(base_path, folder)

    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        continue

    print(f"Reading: {folder}")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    text = f.read()

                emails.append({
                    "email_text": text,
                    "label": label
                })

            except Exception:
                pass

df = pd.DataFrame(emails)

print("\nDataset created successfully!")
print("Total Emails:", len(df))

df.to_csv("dataset/phishing_email.csv", index=False)

print("Saved as dataset/phishing_email.csv")