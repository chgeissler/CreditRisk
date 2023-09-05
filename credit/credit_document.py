from PyPDF2 import PdfReader, PageObject
from typing import List, Dict, Tuple, Optional
import textutils as tu


class CreditDocument(object):
    def __init__(self, path):
        self._path = path
        self._reader = PdfReader(path)
        self._summary_block = None

    def get_text(self, page_number):
        page = self._reader.pages[page_number]
        return page.extract_text()

    def find_tag_in_page(self,
                         tag: str,
                         page_number: int) -> Optional[Tuple[str, int]]:
        page = self._reader.pages[page_number]
        text = page.extract_text()
        tag_position = tu.normalize(text).find(tu.normalize(tag))
        if tag_position >= 0:
            return tag, page_number, tag_position

    def find_tag_in_document(self, tag: str) -> Optional[Tuple[str, int, int]]:
        for page_number, page in enumerate(self._reader.pages):
            text = page.extract_text()
            tag_position = tu.normalize(text).find(tu.normalize(tag))
            if tag_position >= 0:
                return tag, page_number, tag_position
        return None


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
        self._start_page = None
        self._end_page = None
        self._start_tag = None
        self._end_tag = None

    def find_start(self, doc: CreditDocument):
        pass


class SummaryBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["Société destinataire"],
                         endtaglist=["Identité"],
                         expected_start_page=0,
                         expected_end_page=0)


class IdentityBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["Identité"],
                         endtaglist=["Activité"],
                         expected_start_page=0,
                         expected_end_page=0)


class ActivityBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["Activité-Modèle économique"],
                         endtaglist=["Gestion de crise"],
                         expected_start_page=0,
                         expected_end_page=0)


class BankBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["informations bancaires"],
                         endtaglist=["Informations financieres"],
                         expected_start_page=0,
                         expected_end_page=0)


class KeyFinancialsBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["informations financieres", "Chiffres clés"],
                         endtaglist=["BFR"],
                         expected_start_page=0,
                         expected_end_page=0)


class BFRBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["BFR"],
                         endtaglist=["Analyse structurelle"],
                         expected_start_page=0,
                         expected_end_page=0)


class StructuralAnalysisBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["Analyse structurelle"],
                         endtaglist=["Ratios de rotation"],
                         expected_start_page=0,
                         expected_end_page=0)


class TurnoverRatiosBlock(DocumentBlock):

    def __init__(self):
        super().__init__(starttaglist=["Ratios de rotation"],
                         endtaglist=["Analyse des postes d'achat"],
                         expected_start_page=0,
                         expected_end_page=0)



