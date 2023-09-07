import os

from PyPDF2 import PdfReader, PageObject
from tabula import read_pdf as tb_rdpdf
from typing import List, Dict, Tuple, Optional
import credit.textutils as tu
import camelot
import pandas as pd


class CreditDocument(object):
    def __init__(self, path):
        self._path = path
        self._reader = PdfReader(path)
        self._sections = []
        self._summary_section = SummarySection(self)
        self._sections.append(self._summary_section)
        self._identity_section = IdentitySection(self)
        self._sections.append(self._identity_section)
        self._activity_section = ActivitySection(self)
        self._sections.append(self._activity_section)
        self._bank_section = BankSection(self)
        self._sections.append(self._bank_section)
        self._key_financials_section = KeyFinancialsSection(self)
        self._sections.append(self._key_financials_section)
        self._bfr_section = BFRSection(self)
        self._sections.append(self._bfr_section)
        self._structural_analysis_section = StructuralAnalysisSection(self)
        self._sections.append(self._structural_analysis_section)
        self._turnover_ratios_section = TurnoverRatiosSection(self)
        self._sections.append(self._turnover_ratios_section)
        self._tax_and_social_section = TaxAndSocialDefaultsSection(self)
        self._sections.append(self._tax_and_social_section)
        self._billing_analysis_section = BillingAnalysisSection(self)
        self._sections.append(self._billing_analysis_section)

    @property
    def reader(self):
        return self._reader

    def get_text(self, page_number):
        """
        Get text from page
        :param page_number: int, page number to get text from
        :return text from page
        """
        page = self._reader.pages[page_number]
        return page.extract_text()

    def find_tag_in_page(self,
                         tag: str,
                         page_number: int) -> Optional[Tuple[str, int, int]]:
        """
        Find tag in page
        :param tag: str, string to find
        :param page_number: int, page number to search in
        :return tuple of [matching tag, page number, position] if found, None otherwise
        """
        page = self._reader.pages[page_number]
        text = page.extract_text()
        tag_position = tu.normalize(text).find(tu.normalize(tag))
        if tag_position >= 0:
            return tag, page_number, tag_position
        else:
            return None

    def find_tag_in_document(self, tag: str) -> Optional[Tuple[str, int, int]]:
        """
        Find tag in document
        :param tag: str, string to find
        :return tuple of (tag, number of first page where tag is found, tag position) if found, None otherwise

        """
        for page_number, page in enumerate(self._reader.pages):
            text = page.extract_text()
            tag_position = tu.normalize(text).find(tu.normalize(tag))
            if tag_position >= 0:
                return tag, page_number, tag_position
        return None

    def locate_sections(self):
        for section in self._sections:
            section.locate_in_document(self)


class DocumentCollector(object):

    def __init__(self, path: str):
        self._path = path
        self._documents = pd.DataFrame(columns=["Size",
                                                "Nb pages",
                                                "Nb tables pypdf",
                                                "Nb tables tabula",
                                                "Nb tables camelot"])

    def collect_documents(self):
        """
            a function that scans a directory for pdf files and collects documents from them
            :return:
            """
        files = os.listdir(self._path)
        for file in files:
            doc = CreditDocument(os.path.join(self._path, file))
            # get the file size
            self._documents.loc[file, "Size"] = os.path.getsize(os.path.join(self._path, file))
            self._documents.loc[file, "Nb pages"] = len(doc.reader.pages)

        pass

    def write_doc_stats(self):
        """
        Write document stats to csv file
        :return:
        """
        self._documents.to_csv(os.path.join("./", "doc_stats.csv"))


class DocumentSection(object):

    def __init__(self,
                 document: CreditDocument,
                 starttaglist: List[str] = None,
                 endtaglist: List[str] = None,
                 expected_start_page: int = None,
                 expected_end_page: int = None):
        self._document = document
        self._starttaglist = starttaglist
        self._endtaglist = endtaglist
        self._expected_start_page = expected_start_page
        self._expected_end_page = expected_end_page
        self._start_page = -1
        self._end_page = -1
        self._start_tag = None
        self._end_tag = None
        self._start_tag_position = -1
        self._end_tag_position = -1

    def locate_in_document(self, doc: CreditDocument):
        """
        Locate section in document from start and end tags
        :param doc: CreditDocument, document to locate section in
        :return: None. Self attributes are updated
        """
        for start_tag in self._starttaglist:
            start_tag_tuple = doc.find_tag_in_document(start_tag)
            if start_tag_tuple is not None:
                self._start_tag, self._start_page, self._start_tag_position = start_tag_tuple
                break
        for end_tag in self._endtaglist:
            end_tag_tuple = doc.find_tag_in_document(end_tag)
            if end_tag_tuple is not None:
                self._end_tag, self._end_page, self._end_tag_position = end_tag_tuple
                break
        pass

    def read_tables_in_section(self,
                               use_tabula: bool = True):
        """
        Read tables in section
        :param use_tabula: bool, use tabula to read tables
        :return: None. Self attributes are updated
        """
        pass


class SummarySection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Société destinataire"],
                         endtaglist=["Identité"],
                         expected_start_page=0,
                         expected_end_page=0)


class IdentitySection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Identité"],
                         endtaglist=["Activité"],
                         expected_start_page=0,
                         expected_end_page=0)


class ActivitySection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Activité-Modèle économique"],
                         endtaglist=["Gestion de crise"],
                         expected_start_page=0,
                         expected_end_page=0)


class BankSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["informations bancaires"],
                         endtaglist=["Informations financieres"],
                         expected_start_page=0,
                         expected_end_page=0)


class KeyFinancialsSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["informations financieres", "Chiffres clés"],
                         endtaglist=["BFR"],
                         expected_start_page=0,
                         expected_end_page=0)


class BFRSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["BFR"],
                         endtaglist=["Analyse structurelle"],
                         expected_start_page=0,
                         expected_end_page=0)


class StructuralAnalysisSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Analyse structurelle"],
                         endtaglist=["Ratios de rotation"],
                         expected_start_page=0,
                         expected_end_page=0)


class TurnoverRatiosSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Ratios de rotation"],
                         endtaglist=["Analyse des postes d'achat"],
                         expected_start_page=0,
                         expected_end_page=0)


class TaxAndSocialDefaultsSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Defauts de paiements sociaux et fiscaux"],
                         endtaglist=["Analyse de factures fournisseurs"],
                         expected_start_page=0,
                         expected_end_page=0)


class BillingAnalysisSection(DocumentSection):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Analyse de factures fournisseurs"],
                         endtaglist=["Votre expérience de paiement"],
                         expected_start_page=0,
                         expected_end_page=0)
