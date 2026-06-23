from pathlib import Path
import pandas as pd
import re
import json

#in order to work the code needs a CSV files containing all the articles you've used

class BibliographyOrganizer:

    def __init__(self, csv_file):
        self.csv_file = Path(csv_file) #change to you path
        self.df = pd.read_csv(csv_file)

        self.standardize_columns()
        self.clean_data()
        self.remove_duplicates()

    def standardize_columns(self):

        rename_map = {
            "Authors": "authors",
            "Author": "authors",
            "Title": "title",
            "Year": "year",
            "Journal": "journal",
            "DOI": "doi",
            "URL": "url"
        }

        self.df.rename(columns=rename_map, inplace=True)

    def clean_data(self):

        required = ["title"]

        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")

        self.df["title"] = (
            self.df["title"]
            .fillna("")
            .str.strip()
        )

        if "journal" in self.df.columns:
            self.df["journal"] = (
                self.df["journal"]
                .fillna("")
                .str.strip()
            )

        if "doi" in self.df.columns:
            self.df["doi"] = (
                self.df["doi"]
                .fillna("")
                .str.lower()
                .str.strip()
            )

        if "authors" in self.df.columns:
            self.df["authors"] = (
                self.df["authors"]
                .fillna("")
                .apply(self.normalize_authors)
            )

    def normalize_authors(self, author_string):

        if not author_string:
            return ""

        authors = re.split(r";|,", author_string)

        clean = []

        for author in authors:
            author = author.strip()

            if author:
                clean.append(author)

        return " and ".join(clean)

    def remove_duplicates(self):

        if "doi" in self.df.columns:

            doi_entries = self.df["doi"] != ""

            doi_df = self.df[doi_entries]
            no_doi_df = self.df[~doi_entries]

            doi_df = doi_df.drop_duplicates(
                subset="doi",
                keep="first"
            )

            no_doi_df = no_doi_df.drop_duplicates(
                subset="title",
                keep="first"
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

        sort_columns = []

        if "year" in self.df.columns:
            sort_columns.append("year")

        if "authors" in self.df.columns:
            sort_columns.append("authors")

        if sort_columns:

            self.df = self.df.sort_values(
                by=sort_columns,
                ascending=[False] * len(sort_columns)
            )

    def generate_bibtex_key(self, row):

        author = "unknown"

        if row.get("authors", ""):
            author = row["authors"].split(" and ")[0]

            author = author.split()[-1]

        year = str(row.get("year", "xxxx"))

        title = row.get("title", "")

        first_word = (
            title.split()[0]
            .lower()
            .replace(":", "")
            if title
            else "paper"
        )

        return f"{author}{year}{first_word}"

    def export_bibtex(self, output="references.bib"):

        entries = []

        for _, row in self.df.iterrows():

            key = self.generate_bibtex_key(row)

            entry = [
                f"@article{{{key},"
            ]

            for field in [
                "title",
                "authors",
                "journal",
                "year",
                "doi",
                "url"
            ]:

                if field in row and pd.notna(row[field]):

                    value = str(row[field])

                    if value:

                        name = (
                            "author"
                            if field == "authors"
                            else field
                        )

                        entry.append(
                            f"  {name} = {{{value}}},"
                        )

            entry.append("}")

            entries.append("\n".join(entry))

        Path(output).write_text(
            "\n\n".join(entries),
            encoding="utf-8"
        )

    def export_csl_json(
        self,
        output="references.json"
    ):

        records = []

        for _, row in self.df.iterrows():

            paper = {
                "title": row.get("title", ""),
                "container-title": row.get("journal", ""),
                "issued": row.get("year", ""),
                "DOI": row.get("doi", ""),
                "URL": row.get("url", "")
            }

            records.append(paper)

        with open(output, "w", encoding="utf-8") as f:

            json.dump(
                records,
                f,
                indent=2,
                ensure_ascii=False
            )

    def save_clean_csv(
        self,
        output="organized_bibliography.csv"
    ):

        self.df.to_csv(
            output,
            index=False
        )


if __name__ == "__main__":

    organizer = BibliographyOrganizer(
        "articles.csv"
    )

    organizer.sort_bibliography()

    organizer.save_clean_csv()

    organizer.export_bibtex()

    organizer.export_csl_json()

    print("Bibliography organized.")
