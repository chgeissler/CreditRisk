import datetime
import os
import re

import credit_document as cd
import textutils as tu
import numpy as np
import pandas as pd
from typing import Union
from company import Company


class CreditRequest(object):
    """
    This class represents a credit request issued by a company at a given date
    """

    def __init__(self):
        self._request_date: datetime.date = datetime.date(1900, 1, 1)
        self._company: Union[Company, None] = None
        self._requested_amount: float = 0
        self._granted_amount: float = 0
        self._start_date: datetime.date = datetime.date(1900, 1, 1)
        self._end_date: datetime.date = datetime.date(1900, 1, 1)
        self._duration: float = 0
        self._document: Union[cd.CreditDocument, None] = None
        self._is_parsed = False
        self._bug_report: str = ""

    def link_to_company(self,
                        document: cd.CreditDocument,
                        cp: Company):
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
        self._request_date = cdoc.locate_field_in_section("Request", "RequestDate")
        self._requested_amount = cdoc.locate_field_in_section("Request", "RequestedAmount")
        self._granted_amount = cdoc.locate_field_in_section("Request", "GrantedAmount")
        self._start_date = cdoc.locate_field_in_section("Request", "StartDate")
        self._end_date = cdoc.locate_field_in_section("Request", "EndDate")

    def parse(self):
        """
        Parse credit request from text fields
        :return:
        """
        bug_met = False
        self._bug_report = ""
        # traitement de la date de demande
        if type(self._request_date) == str:
            try:
                field = tu.search_date(str(self._request_date).replace("-", "/"))
            except ValueError:
                bug_met = True
                self._bug_report += f"Date {self._request_date} invalide.\n"
            if field == "":
                bug_met = True
                self._bug_report += f"Date {self._request_date} invalide.\n"
            else:
                self._request_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()
        # traitement du montant demandé
        if self._requested_amount != "":
            try:
                self._requested_amount = tu.currency_to_float(str(self._requested_amount), "eur")
            except ValueError:
                bug_met = True
                self._requested_amount = np.nan
            if np.isnan(self._requested_amount):
                bug_met = True
        # traitement du montant accordé
        if self._granted_amount != "":
            try:
                self._granted_amount = tu.currency_to_float(str(self._granted_amount), "eur")
            except ValueError:
                bug_met = True
                self._granted_amount = np.nan
            if np.isnan(self._granted_amount):
                bug_met = True
        # traitement de la date de début
        if type(self._start_date) == str:
            try:
                field = tu.search_date(str(self._start_date).replace("-", "/"))
            except ValueError:
                bug_met = True
                self._bug_report += f"Date {self._start_date} invalide.\n"
            if field == "":
                bug_met = True
                self._bug_report += f"Date {self._start_date} invalide.\n"
            else:
                self._start_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()
        # traitement de la date de fin
        if type(self._end_date) == str:
            try:
                field = tu.search_date(str(self._end_date).replace("-", "/"))
            except ValueError:
                bug_met = True
                self._bug_report += f"Date {self._end_date} invalide.\n"
            if field == "":
                bug_met = True
                self._bug_report += f"Date {self._end_date} invalide.\n"
            else:
                self._end_date = datetime.datetime.strptime(field, "%d/%m/%Y").date()
