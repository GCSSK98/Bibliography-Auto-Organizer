from pathlib import Path
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import re

"""
HOW TO RUN THIS PROGRAM

1. Make sure Python (version 3.10 or newer) is installed.

2. Install the required package:

    pip install pandas

3. Save this script as:

    bibliography_csv_organizer.py

4. Run the script:

    python bibliography_csv_organizer.py

5. A file selection window will appear.

6. Select one or more CSV files.

7. The program will automatically:
    - Merge all CSV files
    - Standardize column names
    - Clean the data
    - Remove duplicates
    - Sort the bibliography
    - Create an output folder

8. Generated files:

    output/organized_bibliography.csv
    output/references.bib

IMPORTANT

The CSV files should preferably contain columns such as:

title, authors, year, journal, doi, url

The program will also recognize common variations such as:

Title -> title
Authors -> authors
DOI -> doi
Journal -> journal
"""



class CSVBibliographyOrganizer:

    def __init__(self):

        self.df = pd.DataFrame()

    def select_files(self):

        root = tk.Tk()

        root.withdraw()

        files = filedialog.askopenfilenames(
            title="Select CSV files",
            filetypes=[("CSV files", "*.csv")]
        )

        return list(files)

    def load_files(self, files):

        dataframes = []

        for file in files:

            try:

                df = pd.read_csv(file)

                dataframes.append(df)

            except Exception as e:

                print(f"Error reading {file}: {e}")

        if dataframes:

            self.df = pd.concat(
                dataframes,
                ignore_index=True
            )

    def standardize_columns(self):

        rename_map = {

            "Title": "title",
            "TITLE": "title",

            "Author": "authors",
            "Authors": "authors",
            "AUTHOR": "authors",

            "Year": "year",

            "Journal": "journal",

            "DOI": "doi",

            "URL": "url"
        }

        self.df.rename(
            columns=rename_map,
            inplace=True
        )

    def clean_data(self):

        if "title" not in self.df.columns:

            raise ValueError(
                "The CSV must contain a title column."
            )

        self.df["title"] = (
            self.df["title"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        optional_columns = [

            "authors",
            "journal",
            "doi",
            "url"
        ]

        for col in optional_columns:

            if col in self.df.columns:

                self.df[col] = (

                    self.df[col]

                    .fillna("")

                    .astype(str)

                    .str.strip()
                )

        if "doi" in self.df.columns:

            self.df["doi"] = (

                self.df["doi"]

                .str.lower()
            )

    def remove_duplicates(self):

        if "doi" in self.df.columns:

            has_doi = self.df["doi"] != ""

            doi_df = self.df[has_doi]

            no_doi_df = self.df[~has_doi]

            doi_df = doi_df.drop_duplicates(
                subset="doi"
            )

            no_doi_df = no_doi_df.drop_duplicates(
                subset="title"
            )

            self.df = pd.concat(
                [doi_df, no_doi_df],
                ignore_index=True
            )

        else:

            self.df = self.df.drop_duplicates(
                subset="title"
            )

    def sort_bibliography(self):

        if "year" in self.df.columns:

            self.df = self.df.sort_values(
                by="year",
                ascending=False
            )

    def create_output_folder(self):

        output = Path("output")

        output.mkdir(
            exist_ok=True
        )

        return output

    def save_csv(self, output):

        filename = (
            output /
            "organized_bibliography.csv"
        )

        self.df.to_csv(
            filename,
            index=False
        )

    def export_bibtex(self, output):

        filename = output / "references.bib"

        entries = []

        for _, row in self.df.iterrows():

            author = "unknown"

            if "authors" in row:

                value = str(
                    row["authors"]
                )

                if value:

                    author = value.split()[0]

            year = str(
                row.get(
                    "year",
                    "xxxx"
                )
            )

            title = str(
                row.get(
                    "title",
                    ""
                )
            )

            first_word = (

                title.split()[0]

                if title

                else "paper"
            )

            key = (
                f"{author}{year}{first_word}"
            )

            key = re.sub(
                r"[^a-zA-Z0-9]",
                "",
                key
            )

            bib = f"""@article{{{key},
  author = {{{row.get('authors','')}}},
  title = {{{row.get('title','')}}},
  journal = {{{row.get('journal','')}}},
  year = {{{row.get('year','')}}},
  doi = {{{row.get('doi','')}}},
  url = {{{row.get('url','')}}}
}}"""

            entries.append(bib)

        filename.write_text(
            "\n\n".join(entries),
            encoding="utf-8"
        )


def main():

    organizer = CSVBibliographyOrganizer()

    files = organizer.select_files()

    if not files:

        print("No files selected.")

        return

    organizer.load_files(files)

    organizer.standardize_columns()

    organizer.clean_data()

    organizer.remove_duplicates()

    organizer.sort_bibliography()

    output = organizer.create_output_folder()

    organizer.save_csv(output)

    organizer.export_bibtex(output)

    print(
        f"Bibliography saved in {output.resolve()}"
    )


if __name__ == "__main__":

    main()
