from PyPDF2 import PdfReader, PageObject
from typing import List, Dict, Tuple, Optional
import credit.textutils as tu


class CreditDocument(object):
    def __init__(self, path):
        self._path = path
        self._reader = PdfReader(path)
        self._blocks = []
        self._summary_block = SummaryBlock(self)
        self._blocks.append(self._summary_block)
        self._identity_block = IdentityBlock(self)
        self._blocks.append(self._identity_block)
        self._activity_block = ActivityBlock(self)
        self._blocks.append(self._activity_block)
        self._bank_block = BankBlock(self)
        self._blocks.append(self._bank_block)
        self._key_financials_block = KeyFinancialsBlock(self)
        self._blocks.append(self._key_financials_block)
        self._bfr_block = BFRBlock(self)
        self._blocks.append(self._bfr_block)
        self._structural_analysis_block = StructuralAnalysisBlock(self)
        self._blocks.append(self._structural_analysis_block)
        self._turnover_ratios_block = TurnoverRatiosBlock(self)
        self._blocks.append(self._turnover_ratios_block)
        self._tax_and_social_block = TaxAndSocialDefaultsBlock(self)
        self._blocks.append(self._tax_and_social_block)
        self._billing_analysis_block = BillingAnalysisBlock(self)
        self._blocks.append(self._billing_analysis_block)

    def get_text(self, page_number):
        """
        Get text from page
        :param
            page_number: int, page number to get text from
        :return:
            text from page
        """
        page = self._reader.pages[page_number]
        return page.extract_text()

    def find_tag_in_page(self,
                         tag: str,
                         page_number: int) -> Optional[Tuple[str, int, int]]:
        """
        Find tag in page
        :param
            tag: str, string to find
        :param
            page_number: int, page number to search in
        :return:
            tuple of tag and page number if found, None otherwise
        """
        page = self._reader.pages[page_number]
        text = page.extract_text()
        tag_position = tu.normalize(text).find(tu.normalize(tag))
        if tag_position >= 0:
            return tag, page_number, tag_position

    def find_tag_in_document(self, tag: str) -> Optional[Tuple[str, int, int]]:
        """
        Find tag in document
        :param
            tag: str, string to find
        :return:
            tuple of (tag, number of first page where tag is found, tag position) if found, None otherwise

        """
        for page_number, page in enumerate(self._reader.pages):
            text = page.extract_text()
            tag_position = tu.normalize(text).find(tu.normalize(tag))
            if tag_position >= 0:
                return tag, page_number, tag_position
        return None

    def locate_blocks(self):
        for block in self._blocks:
            block.locate_in_document(self)


class DocumentBlock(object):

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


class SummaryBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Société destinataire"],
                         endtaglist=["Identité"],
                         expected_start_page=0,
                         expected_end_page=0)


class IdentityBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Identité"],
                         endtaglist=["Activité"],
                         expected_start_page=0,
                         expected_end_page=0)


class ActivityBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Activité-Modèle économique"],
                         endtaglist=["Gestion de crise"],
                         expected_start_page=0,
                         expected_end_page=0)


class BankBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["informations bancaires"],
                         endtaglist=["Informations financieres"],
                         expected_start_page=0,
                         expected_end_page=0)


class KeyFinancialsBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["informations financieres", "Chiffres clés"],
                         endtaglist=["BFR"],
                         expected_start_page=0,
                         expected_end_page=0)


class BFRBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["BFR"],
                         endtaglist=["Analyse structurelle"],
                         expected_start_page=0,
                         expected_end_page=0)


class StructuralAnalysisBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Analyse structurelle"],
                         endtaglist=["Ratios de rotation"],
                         expected_start_page=0,
                         expected_end_page=0)


class TurnoverRatiosBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Ratios de rotation"],
                         endtaglist=["Analyse des postes d'achat"],
                         expected_start_page=0,
                         expected_end_page=0)


class TaxAndSocialDefaultsBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Defauts de paiements sociaux et fiscaux"],
                         endtaglist=["Analyse de factures fournisseurs"],
                         expected_start_page=0,
                         expected_end_page=0)


class BillingAnalysisBlock(DocumentBlock):

    def __init__(self, document: CreditDocument):
        super().__init__(document=document,
                         starttaglist=["Analyse de factures fournisseurs"],
                         endtaglist=["Votre expérience de paiement"],
                         expected_start_page=0,
                         expected_end_page=0)
