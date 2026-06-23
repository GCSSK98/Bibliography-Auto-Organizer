import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import re

"""
HOW TO RUN THIS PROGRAM

1. Make sure Python (version 3.10 or newer) is installed.

2. Install the required package by opening a terminal and running:

    pip install pandas

3. Save this script as:
    
    bibliography_organizer.py

4. Run the script from a terminal:

    python bibliography_organizer.py

5. A file selection window will appear.

6. Select one or more .txt files containing bibliographic references.

7. Click "Open".

8. The program will automatically:
    - Read all selected files
    - Extract bibliographic information
    - Remove duplicate references
    - Sort entries by publication year
    - Create an "output" folder

9. Two files will be generated inside the output folder:

    bibliography.csv
    references.bib

IMPORTANT:
This program works best when the .txt files already contain bibliographic references.

Example of a valid entry:

    LeCun Y., Bengio Y., Hinton G. Deep Learning. Nature. 2015. doi:10.1038/nature14539

It is NOT designed to process entire scientific articles converted from PDF to TXT.
"""


class BibliographyOrganizer:

    def __init__(self):

        self.records = []

        self.doi_pattern = re.compile(
            r'10\.\d{4,9}/[-._;()/:A-Z0-9]+',
            re.IGNORECASE
        )

    def select_files(self):

        root = tk.Tk()
        root.withdraw()

        files = filedialog.askopenfilenames(
            title="Seleziona i file bibliografici",
            filetypes=[("Text files", "*.txt")]
        )

        return list(files)

    def process_files(self, files):

        for file in files:

            path = Path(file)

            text = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            self.parse_text(text)

    def parse_text(self, text):

        entries = re.split(r"\n\s*\n", text)

        for entry in entries:

            entry = entry.strip()

            if not entry:
                continue

            paper = self.extract_information(entry)

            self.records.append(paper)

    def extract_information(self, text):

        paper = {
            "authors": "",
            "title": "",
            "journal": "",
            "year": "",
            "doi": "",
            "raw_text": text
        }

        doi = self.doi_pattern.search(text)

        if doi:

            paper["doi"] = doi.group()

        year = re.search(r"(19|20)\d{2}", text)

        if year:

            paper["year"] = int(year.group())

        pieces = text.split(".")

        if len(pieces) >= 1:

            paper["authors"] = pieces[0].strip()

        if len(pieces) >= 2:

            paper["title"] = pieces[1].strip()

        if len(pieces) >= 3:

            paper["journal"] = pieces[2].strip()

        return paper

    def build_dataframe(self):

        df = pd.DataFrame(self.records)

        if df.empty:

            return df

        has_doi = df["doi"] != ""

        doi_df = df[has_doi]

        no_doi_df = df[~has_doi]

        doi_df = doi_df.drop_duplicates(
            subset="doi"
        )

        no_doi_df = no_doi_df.drop_duplicates(
            subset="title"
        )

        df = pd.concat(
            [doi_df, no_doi_df],
            ignore_index=True
        )

        if "year" in df.columns:

            df = df.sort_values(
                by="year",
                ascending=False
            )

        return df

    def create_output(self, df):

        output = Path("output")

        output.mkdir(exist_ok=True)

        csv_file = output / "bibliography.csv"

        df.to_csv(
            csv_file,
            index=False
        )

        self.export_bibtex(
            df,
            output / "references.bib"
        )

        return output

    def export_bibtex(self, df, filename):

        entries = []

        for _, row in df.iterrows():

            surname = "unknown"

            if row["authors"]:

                surname = row["authors"].split()[0]

            year = row["year"]

            title = row["title"]

            title_word = (
                title.split()[0]
                if title
                else "paper"
            )

            key = f"{surname}{year}{title_word}"

            key = re.sub(
                r"[^a-zA-Z0-9]",
                "",
                key
            )

            entry = f"""@article{{{key},
  author = {{{row['authors']}}},
  title = {{{row['title']}}},
  journal = {{{row['journal']}}},
  year = {{{row['year']}}},
  doi = {{{row['doi']}}}
}}"""

            entries.append(entry)

        filename.write_text(
            "\n\n".join(entries),
            encoding="utf-8"
        )


def main():

    organizer = BibliographyOrganizer()

    files = organizer.select_files()

    if not files:

        print("Nessun file selezionato.")

        return

    organizer.process_files(files)

    df = organizer.build_dataframe()

    output = organizer.create_output(df)

    print(f"Bibliografia salvata in: {output.resolve()}")


if __name__ == "__main__":

    main()
