import datetime
import os
import re

import numpy as np
import pandas as pd
from typing import Union
from . import credit_document as cd
from . import textutils as tu
from . import company as cp


class CreditRequest(object):
    """
    This class represents a credit request issued by a company at a given date
    """

    def __init__(self, req_id: str):
        self._id: str = req_id
        self._request_date: datetime.date = datetime.date(1900, 1, 1)
        self._company: Union[cp.Company, None] = None
        self._requested_amount: float = 0
        self._granted_amount: float = 0
        self._start_date: datetime.date = datetime.date(1900, 1, 1)
        self._end_date: datetime.date = datetime.date(1900, 1, 1)
        self._duration: float = 0
        self._document: Union[cd.CreditDocument, None] = None
        self._is_parsed = True
        self._unmatched_fields = 0
        self._bug_report: str = ""

    @property
    def is_parsed(self):
        return self._is_parsed

    def link_to_company(self,
                        document: cd.CreditDocument,
                        cp: cp.Company):
        """
        Link credit request to document
        :param document: credit document containing the request
        :param cp: company requesting credit, mentioned in the document
        :return: modifies credit request attributes in place
        """
        self._document = document
        self._company = cp
        self._is_parsed = False

    def fill_text_from_credit_document(self):
        """
        Fill credit request attributes from credit document
        :return: modifies credit request attributes in place
        """
        cdoc = self._document
        self._request_date = cdoc.locate_field_in_section("Summary", "RequestDate")
        self._requested_amount = cdoc.locate_field_in_section("Summary", "RequestedAmount")
        self._granted_amount = cdoc.locate_field_in_section("Summary", "GrantedAmount")
        self._start_date = cdoc.locate_field_in_section("Summary", "StartDate")
        self._end_date = cdoc.locate_field_in_section("Summary", "EndDate")

    def parse(self):
        """
        Parse credit request from text fields
        :return:
        """
        bug_met = False
        self._bug_report = ""
        field = ""
        # traitement de la date de demande
        if type(self._request_date) == str:
            try:
                field = tu.search_date(str(self._request_date).replace("-", "/"))
            except ValueError:
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._request_date} invalide.\n"
            if field == "":
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._request_date} invalide.\n"
            else:
                self._request_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()
        # traitement du montant demandé
        if self._requested_amount != "":
            try:
                self._requested_amount = tu.currency_to_float(str(self._requested_amount), "eur")
            except ValueError:
                self._unmatched_fields += 1
                self._is_parsed = False
                self._requested_amount = np.nan
            if np.isnan(self._requested_amount):
                bug_met = True
        # traitement du montant accordé
        if self._granted_amount != "":
            try:
                self._granted_amount = tu.currency_to_float(str(self._granted_amount), "eur")
            except ValueError:
                self._unmatched_fields += 1
                self._is_parsed = False
                self._granted_amount = np.nan
            if np.isnan(self._granted_amount):
                bug_met = True
        # traitement de la date de début
        if type(self._start_date) == str:
            try:
                field = tu.search_date(str(self._start_date).replace("-", "/"))
            except ValueError:
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._start_date} invalide.\n"
            if field == "":
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._start_date} invalide.\n"
            else:
                self._start_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()
        # traitement de la date de fin
        if type(self._end_date) == str:
            try:
                field = tu.search_date(str(self._end_date).replace("-", "/"))
            except ValueError:
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._end_date} invalide.\n"
            if field == "":
                self._unmatched_fields += 1
                self._is_parsed = False
                self._bug_report += f"Date {self._end_date} invalide.\n"
            else:
                self._end_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()

        # calcul de la durée
        if type(self._start_date) == datetime.date and type(self._end_date) == datetime.date:
            self._duration = (self._end_date - self._start_date).days / 365.25



    def insert(self, table: pd.DataFrame):
        """
        Insert credit request into credit request table
        :return:
        """
        doc_idx = self._document.name if self._document is not None else self._id
        if doc_idx == "":
            return table
        table.loc[doc_idx, "RequestDate"] = self._request_date if self._request_date is not None else ""
        table.loc[doc_idx, "CompanyId"] = self._company.identifier if self._company is not None else ""
        table.loc[doc_idx, "CompanyName"] = self._company.full_name if self._company is not None else ""
        table.loc[doc_idx, "RequestedAmount"] = self._requested_amount if self._requested_amount is not None else ""
        table.loc[doc_idx, "GrantedAmount"] = self._granted_amount if self._granted_amount is not None else ""
        table.loc[doc_idx, "StartDate"] = self._start_date if self._start_date is not None else ""
        table.loc[doc_idx, "EndDate"] = self._end_date if self._end_date is not None else ""
        table.loc[doc_idx, "Duration"] = self._duration if self._duration is not None else ""
        table.loc[doc_idx, "BugReport"] = self._bug_report if self._bug_report is not None else ""
        pass