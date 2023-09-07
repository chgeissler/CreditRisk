# from langchain.document_loaders import PyPdfLoader
from tabula import read_pdf
from PyPDF2 import PdfReader
import credit.credit_document as cd
import camelot
import pandas as pd

# Path: main.py


if __name__ == "__main__":
    data_path = "TestData/334064.pdf"
    # data_path = 'TestData/SAS_LAGARDE_&_LARONZE_07_2023.pdf'
    # tabula version
    tb_data = read_pdf(data_path,
                       pages="all",
                       multiple_tables=True)
    # pypdf2 version
    # reader = PdfReader(data_path)
    # page = reader.pages[3]
    # print(page.extract_text())
    doc = cd.CreditDocument(data_path)
    # doc.locate_blocks()
    camdoc = camelot.read_pdf(data_path, pages="all", flavor='stream')
    df_tables = pd.concat([table.df for table in camdoc._tables], axis=0)
    df_tables





