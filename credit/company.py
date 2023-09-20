import datetime
import os

import credit_document as cd
import textutils as tu
import numpy as np
import pandas as pd
from typing import Union


class Company(object):
    """
    This class represents a company as a time-invariant entity.
    """

    def __init__(self):
        self._identifier: str = ""
        self._vat_number: str = ""
        self._creation_date: datetime.date = datetime.date(1900, 1, 1)
        self._full_name: str = ""
        self._ape_code: str = ""
        self._zip_code: str = ""
        self._zip_code: str = ""
        self._city: str = ""
        self._address: str = ""
        self._activity_description: str = ""
        self._bank_activity: str = ""
        self._legal_form: str = ""
        self._capital: Union[float, str] = 0.0
        self._effectif: Union[int, str] = 0
        self._document = None
        self._is_parsed = False

    @property
    def identifier(self):
        return self._identifier

    def link_to_document(self,
                         document: cd.CreditDocument):
        """
        Link company to document
        :param document:
        :return:
        """
        self._document = document
        self._is_parsed = False

    def detect_document_language(self):
        """
        Detect document language
        :return:
        """
        doc = self._document
        assert (doc is not None)
        tag, page, _, _, _ = doc.find_tag_in_document("societe")
        if page >= 0:
            self._document.set_language("FR")
        else:
            tag, page, _, _, _ = doc.find_tag_in_document("sociedade")
            if page >= 0:
                self._document.set_language("PT")
            else:
                tag, page, _, _, _ = doc.find_tag_in_document("company")
                if page >= 0:
                    self._document.set_language("EN")
        pass

    def fill_text_from_credit_document(self):
        """
        Fill company attributes from credit document
        :return: modifies company attributes in place
        """
        cdoc = self._document
        self.detect_document_language()
        self._identifier = cdoc.locate_field_in_section("Identity", "Identifier")
        self._vat_number = cdoc.locate_field_in_section("Identity", "VatNumber")
        self._creation_date = cdoc.locate_field_in_section("Identity", "CreationDate")
        self._full_name = cdoc.locate_field_in_section("Identity",
                                                       "FullName")
        self._ape_code = cdoc.locate_field_in_section("Identity",
                                                      "IndustryCode",)
        self._zip_code = cdoc.locate_field_in_section("Identity",
                                                      "ZipCode",)
        self._city = cdoc.locate_field_in_section("Identity",
                                                  "City")
        self._address = cdoc.locate_field_in_section("Identity",
                                                     "Address")
        self._activity_description = cdoc.locate_field_in_section("Identity",
                                                                  "ActivityDescription")
        self._bank_activity = cdoc.locate_field_in_section("Identity",
                                                           "BankActivity")
        self._capital = cdoc.locate_field_in_section("Identity",
                                                     "Capital")
        self._legal_form = cdoc.locate_field_in_section("Identity",
                                                        "LegalForm")
        self._effectif = cdoc.locate_field_in_section("Identity",
                                                      "NbEmployees")

    def parse(self):
        """
        Parse company from text fields
        :return:
        """
        bug_met = False
        self._identifier = self._identifier.rstrip().lstrip()
        if len(self._identifier) != 9:
            bug_met = True
        if self._vat_number != "":
            self._vat_number = tu.compactify(self._vat_number)
            if len(self._vat_number) != 13:
                bug_met = True
        if type(self._creation_date) == str:
            try:
                self._creation_date = datetime.datetime.strptime(str(self._creation_date), "%d/%m/%Y").date()
            except ValueError:
                bug_met = True
        if self._full_name != "":
            self._full_name = self._full_name.rstrip().lstrip()
        if self._ape_code != "":
            self._ape_code = self._ape_code.rstrip().lstrip()
        if self._zip_code != "":
            self._zip_code = self._zip_code.rstrip().lstrip()
        if self._city != "":
            self._city = self._city.rstrip().lstrip()
        if self._address != "":
            self._address = self._address.rstrip().lstrip()
        if self._activity_description != "":
            self._activity_description = self._activity_description.rstrip().lstrip()
        if self._bank_activity != "":
            self._bank_activity = self._bank_activity.rstrip().lstrip()
        if self._capital != "":
            try:
                self._capital = tu.currency_to_float(str(self._capital), "eur")
            except ValueError:
                bug_met = True
                self._capital = np.nan
            if np.isnan(self._capital):
                bug_met = True
        if self._effectif != "":
            try:
                self._effectif = int(self._effectif)
            except ValueError:
                bug_met = True
                self._effectif = np.nan

        self._is_parsed = not bug_met

    def insert(self, df: pd.DataFrame):
        """
        Insert company into database
        :param df: database
        :return:
        """
        doc_idx = self._document.name if self._document is not None else self._identifier
        if doc_idx == "":
            return df
        df.loc[doc_idx, "Language"] = self._document.language if self._document is not None else ""
        df.loc[doc_idx, "NbPages"] = self._document.nb_pages if self._document is not None else 0
        df.loc[doc_idx, "Identifier"] = self._identifier
        df.loc[doc_idx, "VATNumber"] = self._vat_number
        df.loc[doc_idx, "CreationDate"] = self._creation_date
        df.loc[doc_idx, "FullName"] = self._full_name
        df.loc[doc_idx, "APECode"] = self._ape_code
        df.loc[doc_idx, "ZipCode"] = self._zip_code
        df.loc[doc_idx, "City"] = self._city
        df.loc[doc_idx, "Address"] = self._address
        df.loc[doc_idx, "ActivityDescription"] = self._activity_description
        df.loc[doc_idx, "BankActivity"] = self._bank_activity
        df.loc[doc_idx, "Capital"] = self._capital
        df.loc[doc_idx, "Effectif"] = self._effectif
        df.loc[doc_idx, "IsParsed"] = 1 if self._is_parsed else 0
        return df


class CompanyFinancials(object):
    """
    This class represents a company's financials at a given date.
    """

    def __init__(self,
                 comp: Company,
                 date: datetime.date):
        self._date = date
        self._company = comp
        self._balance_sheet: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                         index=["Sales",
                                                                "ExportSales",
                                                                "GrossOperatingIncome",
                                                                "OperatingIncome",
                                                                "EBIT",
                                                                "NetResult",
                                                                "OperatingCashFlow",
                                                                "Equity",
                                                                "BankDebt",
                                                                "OtherDebt"
                                                                ])
        self._income_statement: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                            index=["Sales"])
        self._working_capital: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                           index=["Inventory",
                                                                  "Receivables",
                                                                  "Payables",
                                                                  "OtherCurrentAssets",
                                                                  "BankFacilities",
                                                                  "OtherCurrentLiabilities"])
        self._structural_ratios: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                             index=["CapitalRatio",
                                                                    "DebtRatio",
                                                                    "FinancialAutonomy",
                                                                    "LiquidityRatio",
                                                                    "WorkingCapital",
                                                                    "RequiredWorkingCapital",
                                                                    "FinancialFeesToSalesRatio",
                                                                    "FinancialFeesToEBITRatio"])
        self._turnover_ratios: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                           index=["InventoryTurnover",
                                                                  "ReceivablesTurnover"])
        self._tax_and_social_defaults: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                                   index=["TaxLiensNumber",
                                                                          "TaxLiensAmount"
                                                                          "SocialLiensNumber",
                                                                          "SocialLiensAmount"])
        self._billing_analysis: pd.DataFrame = pd.DataFrame(columns=["Current", "Y-1", "Y-2"],
                                                            index=["NbBills",
                                                                   "NbBillsPaidOnTime",
                                                                   "NbBillsPaidAfter30days"
                                                                   "NbUnpaidBills"])
        self._qualitative_forecasts: str = ""


class Scoring(object):
    """
    This class represents a company's scoring at a given date.
    """

    def __init__(self,
                 comp: Company,
                 date: datetime.date):
        self._date = date
        self._company = comp
        self._score: int = 0
        self._scoring_comment: str = ""


class CreditRequest(object):
    """
    This class represents a credit request issued by a company at a given date
    """

    def __init__(self,
                 comp: Company,
                 date: datetime.date,
                 requested_amount: float,
                 granted_amount: float):
        self._request_date = date
        self._company = comp
        self._requested_amount = requested_amount
        self._granted_amount = granted_amount


class CreditCollector(object):
    """
    This class collects credit requests from a given directory
    """

    def __init__(self,
                 docpath: str):
        self._docpath = docpath
        self._company_table = pd.DataFrame()
        self._financials_table = pd.DataFrame()
        self._scoring_table = pd.DataFrame()
        self._credit_request_table = pd.DataFrame()

    def collect_companies(self,
                          do_parse: bool = True,
                          verbose: bool = False,
                          doclist: list = None,
                          istart: int = 0,
                          iend: int = 1000
                          ) -> pd.DataFrame:
        """

        :type doclist: list
        :param doclist:
        :param do_parse:
        :param verbose:
        :param istart:
        :param iend:
        :return:
        """
        if doclist is None:
            doclist = []
        if not doclist:
            files = os.listdir(self._docpath)
        else:
            files = doclist
        for ifile, file in enumerate(files):
            if doclist or istart <= ifile <= iend:
                if verbose:
                    print(f"Collecting document {file}")
                docu = cd.CreditDocument(path=self._docpath, name=file)
                a_comp = Company()
                a_comp.link_to_document(docu)
                a_comp.detect_document_language()
                a_comp.fill_text_from_credit_document()
                if do_parse:
                    a_comp.parse()
                a_comp.insert(self._company_table)
        return self._company_table

    def write_companies(self, path: str, name: str):
        """
        Write companies table to file
        :param path: path
        :param name: name
        :return:
        """
        self._company_table.to_csv(os.path.join(path, name))
        pass

    def collect_credit_requests(self,
                                verbose: bool = False,
                                istart: int = 0,
                                iend: int = 1000):
        """
        Collect credit requests from a given directory
        :param verbose: if True, print info
        :param istart: start index
        :param iend: end index
        :return:
        """
        pass

    def write_credit_requests(self,
                              output_file_path: str):
        """
        Write credit requests to file
        :param output_file_path: output file path
        :return:
        """
        pass


if __name__ == "__main__":
    data_path = "/home/cgeissler/local_data/CCRCredit/FichesCredit"
    out_path = "/home/cgeissler/local_data/CCRCredit/Tables"
    debug_mode = False
    outfilename = "companies_3.csv"
    if not debug_mode:
        collector = CreditCollector(data_path)
        collector.collect_companies(verbose=True, istart=0, iend=100)
        collector.write_companies(out_path, outfilename)
    else:
        companies = pd.read_csv(os.path.join(out_path, outfilename), index_col=0)
        for idx in companies.index:
            if companies.loc[idx, "IsParsed"] == 0:
                print(f"Re-parsing company {idx}")
                cred_doc = cd.CreditDocument(path=data_path, name=idx)
                company = Company()
                company.link_to_document(cred_doc)
                company.fill_text_from_credit_document()
                company.parse()
    pass
