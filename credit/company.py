import datetime
import credit.credit_document as cd
import pandas as pd


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
        self._city: str = ""
        self._address: str = ""
        self._activity_description: str = ""
        self._bank_activity: str = ""

    @property
    def identifier(self):
        return self._identifier

    def fill_identifier_from_credit_document(self,
                                             credit_document: cd.CreditDocument):
        """
        get_identifier: gets identifier from credit document
        :param credit_document: credit document
        :return: identifier
        """
        self._identifier = credit_document.get_identifier()


class CompanyFinancials(object):
    """
    This class represents a company's financials at a given date.
    """

    def __init__(self,
                 company: Company,
                 date: datetime.date):
        self._date = date
        self._company = company
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
                 company: Company,
                 date: datetime.date):
        self._date = date
        self._company = company
        self._score: int = 0
        self._scoring_comment: str = ""


class CreditRequest(object):
    """
    This class represents a credit request issued by a company at a given date
    """

    def __init__(self,
                 company: Company,
                 date: datetime.date,
                 requested_amount: float,
                 granted_amount: float):
        self._request_date = date
        self._company = company
        self._requested_amount = requested_amount
        self._granted_amount = granted_amount


if __name__ == "__main__":
    cp = Company()
    cpf = CompanyFinancials(cp, datetime.date(2020, 1, 1))
    cps = Scoring(cp, datetime.date(2020, 1, 1))
    pass
