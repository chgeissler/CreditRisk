import PyPDF2.errors
from PyPDF2 import PdfReader, PageObject
import tabula as tbl
from typing import List, Dict, Tuple, Optional
import credit.textutils as tu
import pandas as pd
import os


class DocumentWithSections(object):
    def __init__(self,
                 path: str,
                 name: str):
        self._path = path
        self._name = name
        fullpath = os.path.join(path, name)
        # Checking if fullpath exists as a file and ia a pdf
        if not os.path.isfile(fullpath):
            raise FileNotFoundError("File {} not found".format(fullpath))
        if not name.endswith(".pdf"):
            raise TypeError("File {} is not a pdf".format(fullpath))
        try:
            self._pypdf_reader = PdfReader(fullpath)
        except PyPDF2.errors.PdfReadError:
            raise TypeError("File {} could not be read by PyPDF2".format(fullpath))
        # self._tbl_tables = tbl.read_pdf(path,
        #                                 pages="all",
        #                                 multiple_tables=True
        #                                 )
        self._tbl_tables = []
        self._sections = {}
        self._pages_text = {}

    def add_section(self, secname: str, sec: "DocumentSection"):
        self._sections[secname] = sec

    @property
    def sections(self):
        return self._sections.values()

    @property
    def pypdf_reader(self):
        return self._pypdf_reader

    @property
    def nb_pages(self):
        return len(self._pypdf_reader.pages)

    @property
    def tbl_tables(self):
        return self._tbl_tables

    @property
    def nb_tbl_tables(self):
        return len(self._tbl_tables)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def get_page_text(self, page_number):
        """
        Get text from page
        :param page_number: int, page number to get text from
        :return text from page
        """
        page = self._pypdf_reader.pages[page_number]
        if page_number in self._pages_text.keys():
            page_text = self._pages_text[page_number]
        else:
            page_text = page.extract_text()
            self._pages_text[page_number] = page_text
        return page_text

    def find_tag_in_page(self,
                         tag: str,
                         page_number: int,
                         space_sensitive=False,
                         max_spaces_number=1) -> Tuple[str, int, int, int, int]:
        """
        Find tag in page

        :param max_spaces_number:
        :param tag: str, string to find
        :param page_number: int, page number to search in
        :param space_sensitive: bool; if false, will look for a match up to random spaces
        :return tuple of [matching tag, page number, position] if found, None otherwise
        """
        # extract full text from page
        text = self.get_page_text(page_number)
        # normalize text
        ntext = tu.normalize(text)
        # get tag position in normalized text
        tag_position = ntext.find(tu.normalize(tag))
        iline = -1
        tag_position_in_line = -1
        if tag_position >= 0:
            # get lines from text
            # warning: this is not robust to line breaks
            nlines = ntext.split("\n")
            # look for the first line containing the tag
            for iline, nline in enumerate(nlines):
                if tu.normalize(tag) in nline:
                    tag_position_in_line, _ = tu.search_for_tag(tag, nline, space_sensitive=space_sensitive)
                    return tag, page_number, tag_position, iline, tag_position_in_line
        return tag, page_number, tag_position, iline, tag_position_in_line

    def find_tag_in_document(self,
                             tag: str,
                             min_page=0,
                             max_page=1000000,
                             min_line=0,
                             max_line=1000
                             ) -> Tuple[str, int, int, int, int]:
        """
        Find tag in document
        :param min_page: the first page to look for the tag in
        :param max_page:    the last page to look for the tag in
        :param min_line:    the first line to look for the tag in
        :param max_line:    the last line to look for the tag in
        :param tag: str, string to find
        :return tuple of (tag, number of first page where tag is found, tag position) if found, None otherwise

        """
        res = (tag, -1, -1, -1, -1)
        for page_number, page in enumerate(self._pypdf_reader.pages):
            if min_page <= page_number <= max_page:
                res = self.find_tag_in_page(tag, page_number)
                # look for the position of the first tag occurence in the page
                if res[2] >= 0:
                    return res
        return res

    def locate_sections(self):
        """
        Locate all sections in a document
        :return: modifies each section in the sections list
        """
        for section in self.sections:
            section.locate_in_document(self)

    def get_full_text(self,
                      start_page: int,
                      start_position: int,
                      end_page: int,
                      end_position: int) -> str:
        """
        Get full text from document in a specified section,
        taking into account a start and end page, and a start and end position in these pages
        :param start_page: int, page number where to start
        :param start_position: int, position in start page where to start
        :param end_page: int, page number where to end
        :param end_position: int, position in end page where to end
        :return: str, full text from pages interval
        """
        text = ""
        for ipage, page in enumerate(self._pypdf_reader.pages):
            if start_page <= ipage <= end_page:
                page_text = self.get_page_text(ipage)
                if ipage == start_page:
                    text += page_text[start_position:]
                elif ipage == end_page:
                    text += page_text[:end_position]
                else:
                    text += page_text
        return text


class DocumentCollector(object):

    def __init__(self, path: str):
        self._path = path
        self._documents = pd.DataFrame()

    def collect_documents(self,
                          istart: int = 0,
                          iend: int = 1000000,
                          verbose: bool = False):
        """
            a function that scans a directory for pdf files and collects documents from them
            :param istart: int, index of first file to collect
            :param iend: int, index of last file to collect
            :param verbose: bool, if True, print information about the process
            :return:
            """
        files = os.listdir(self._path)
        for ifile, file in enumerate(files):
            if istart <= ifile <= iend:
                if verbose:
                    print("Collecting document {}".format(file))
                fullpath = os.path.join(self._path, file)
                doc = DocumentWithSections(self._path, file)
                doc.locate_sections()
                # get the file size
                self._documents.loc[file, "Size"] = os.path.getsize(fullpath)
                # get the number of pages
                self._documents.loc[file, "Nb pages"] = len(doc.pypdf_reader.pages)
        pass

    def write_doc_stats(self, name: str):
        """
        Write document stats to csv file
        :return:
        """
        self._documents.to_csv(os.path.join("./", name))


class DocumentSection(object):

    def __init__(self,
                 document: DocumentWithSections,
                 starttaglist: List[str] = None,
                 endtaglist: List[str] = None):
        self._document = document
        self._full_text = ""
        self._starttaglist = starttaglist
        self._endtaglist = endtaglist
        self._start_page = -1
        self._end_page = -1
        self._start_tag = None
        self._end_tag = None
        self._start_tag_position = -1
        self._end_tag_position = -1
        self._start_tag_line_number = -1
        self._start_tag_position_in_line = -1

    @property
    def full_text(self):
        return self._full_text

    @property
    def start_page(self):
        return self._start_page

    @property
    def end_page(self):
        return self._end_page

    @property
    def start_position(self):
        return self._start_tag_position

    @property
    def end_position(self):
        return self._end_tag_position

    @property
    def start_tag(self):
        return self._start_tag

    @property
    def end_tag(self):
        return self._end_tag

    @property
    def start_tag_line_number(self):
        return self._start_tag_line_number

    @property
    def start_tag_position_in_line(self):
        return self._start_tag_position_in_line

    @property
    def is_located(self):
        return (self._start_page >= 0
                and self._start_tag_position >= 0)

    def locate_in_document(self,
                           d: DocumentWithSections,
                           min_page=0,
                           max_page=1000000):
        """
        Locate section in document from start and end tags
        :param min_page: first page to look for tags in
        :param max_page:   last page to look for tags in
        :param d: CreditDocument, document to locate section in
        :return: None. Self attributes are updated
        """
        # look for the first tag in the starting list matching the document
        for start_tag in self._starttaglist:
            start_tag_tuple = d.find_tag_in_document(start_tag, min_page=min_page, max_page=max_page)
            if start_tag_tuple[1] >= 0:
                (self._start_tag,
                 self._start_page,
                 self._start_tag_position,
                 self._start_tag_line_number,
                 self._start_tag_position_in_line) = start_tag_tuple
                break
        # look for the first tag in the starting list matching the document
        # The purpose is to delimitate the section starting with the first tag
        for end_tag in self._endtaglist:
            end_tag_tuple = d.find_tag_in_document(end_tag, min_page=self._start_page, max_page=max_page)
            if end_tag_tuple[1] >= 0:
                (self._end_tag,
                 self._end_page,
                 self._end_tag_position, _, _) = end_tag_tuple
                break
        pass

    def get_full_section_text(self):
        """
        Get full section text
        :return: str, full section text
        """
        self._full_text = self._document.get_full_text(self._start_page,
                                                       self._start_tag_position,
                                                       self._end_page,
                                                       self._end_tag_position)

    def get_tag_line(self,
                     tag: str,
                     space_sensitive=False,
                     max_space_number=1) -> Tuple[int, int, str, str, str]:
        """
        Get the first line in full text containing tag
        :param space_sensitive:
        :param max_space_number:
        :param tag: str, tag to get line from
        :return: index of first line containing tag,
                 index of continuation line in case the tag is split by \n,
                 bit of line starting with match,
                 first match of tag in line,
                 right section of line following match as str
        """
        if not self.is_located:
            self.locate_in_document(self._document)
        if self._full_text == "":
            self.get_full_section_text()
        ntag = tu.normalize(tag)
        ntext = tu.normalize(self._full_text)
        # looks first for the tag in the original text, not split into lines
        position = -1
        position, _ = tu.search_for_tag(ntag,
                                        text=ntext,
                                        space_sensitive=space_sensitive,
                                        max_spaces_number=max_space_number)
        if position < 0:
            return -1, -1, "", "", ""
        # cut the text into lines along carriage returns
        lines = ntext.split("\n")
        for iline, line in enumerate(lines):
            inextline = iline + 1
            # find start position and effective match of ntag
            position, match = tu.search_for_tag(ntag,
                                                line,
                                                space_sensitive=space_sensitive,
                                                max_spaces_number=max_space_number)
            # if tag is found up to spaces
            if position >= 0:
                return iline, iline, line[position:-1], match, tu.right_bit_after_tag(line, match)
            # if tag is not found in a line that could contain it:
            elif inextline < len(lines):
                line += lines[inextline]
                position, match = tu.search_for_tag(ntag,
                                                    line,
                                                    space_sensitive=space_sensitive,
                                                    max_spaces_number=max_space_number)
                if position >= 0:
                    right_bit = tu.right_bit_after_tag(line, match)
                    # if the string bit following the match in current line is empty,
                    # and if end has not been reached, then look for next string
                    if len(tu.compactify(right_bit)) == 0 and inextline < len(lines) - 1:
                        inextline += 1
                        line += lines[inextline]
                    return iline, inextline, line[position:-1], match, tu.right_bit_after_tag(line, match)

        return -1, -1, "", "", ""

    def get_tag_candidates_lines(self, tags: List[str]) -> Tuple[int, str, str, str]:
        """
        returns the coordinates of the first tag from a given list found in the section
        :param tags: list of str, tags to look for
        :return: the position of first matching string found,
                 the mathing string
                 the line containing the matching tag
                 the right bit of line after the match
        """
        iline = -1
        for tag in tags:
            iline, _, line, match, rightbit = self.get_tag_line(tag)
            if iline >= 0:
                return iline, line, match, rightbit
        return iline, "", "", ""

    def get_start_tag_line(self) -> Tuple[int, int, str, str, str]:
        """
        Get the first line in full text containing start tag
        :return: first matching line index,
                 continuation line index,
                 full start tag line,
                 line bit following tag
        """
        return self.get_tag_line(self._start_tag)

    def read_tables_in_section(self,
                               use_tabula: bool = True):
        """
        Read tables in section
        :param use_tabula: bool, use tabula to read tables
        :return: None. Self attributes are updated
        """
        pass


