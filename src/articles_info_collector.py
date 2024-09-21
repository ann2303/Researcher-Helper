import re
from pdf_element_extractor import Pdf
from pathlib import Path

github_regex = r"https?://(?:www\.)?github\.com/[\w-]+/[\w.-]+[\w-]"


class ArticleInfo:

    def __init__(
        self, title, authors, journal, year, abstract, citationCount, saved_pdf=None
    ):
        self.title = title
        self.authors = authors
        self.journal = journal
        self.year = year
        self.abstract = abstract
        self.citationCount = citationCount
        self.saved_pdf = saved_pdf
        self.github_links = []

        if self.saved_pdf is not None:
            self.tables_path = saved_pdf.parent / "tables.pdf"
            self.images_path = saved_pdf.parent / "images"
            self.images_path.mkdir(exist_ok=True)
            self.analyze_pdf(self.saved_pdf)

    def analyze_pdf(self, pdf_path):
        pdf = Pdf(pdf_path)
        text_from_pdf = pdf.extract_text_from_pdf()
        matches = re.findall(github_regex, text_from_pdf)
        if matches is None:
            self.github_links = []
        else:
            self.github_links = matches 
        pdf.extract_and_save_images(self.images_path)
        pdf.extract_and_crop_tables(self.tables_path)
        if not Path(self.tables_path).exists():
            self.tables_path = None
        
        pdf.close()
