# from langchain.document_loaders import PyPdfLoader
from tabula import read_pdf
from PyPDF2 import PdfReader
import credit.credit_document as cd
import credit.document as doc
import camelot
import pandas as pd

# Path: main.py


if __name__ == "__main__":
    data_path = "TestData"
    data_path = "/home/cgeissler/local_data/CCRCredit/FichesCredit"
    do_single_file = False
    do_batch = True

    # camdoc = camelot.read_pdf(file_path, pages="all", flavor='stream')
    if do_batch:
        doccollector = cd.CreditDocumentCollector(data_path)
        doccollector.collect_documents(verbose=True, istart=0, iend=10)
        doccollector.write_doc_stats("foo.csv")
    if do_single_file:
        file_path = f"{data_path}/Enquete_210049.pdf"
        file_path = f"{data_path}/Enquete_200926.pdf"
        document = cd.CreditDocument(file_path)
        document.locate_sections()
        # tag, pagenumber, position, line, position_in_line = document.find_tag_in_page("Analyste", 0)
        summary_text = document.summary_section.full_text
        # iline, line, right_section = document.summary_section.get_start_tag_line()
        requested_amount = document.get_requested_amount()
        pass






