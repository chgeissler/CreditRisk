import os


import credit.document as doc
import camelot
import pandas as pd


class CreditDocument(doc.DocumentWithSections):

    def __init__(self,
                 path: str):
        super().__init__(path=path)
        summary_section = doc.DocumentSection(self,
                                              starttaglist=["Société destinataire"],
                                              endtaglist=["Identité"])
        self.add_section(secname="Summary", sec=summary_section)

        self._identity_section = doc.DocumentSection(document=self,
                                                     starttaglist=["Identité"],
                                                     endtaglist=["Activité"])
        self.add_section(secname="Identity", sec=self._identity_section)

        self._bank_section = doc.DocumentSection(self,
                                                 starttaglist=["informations bancaires"],
                                                 endtaglist=["informations financieres"])
        self.add_section(secname="Bank", sec=self._bank_section)

        self._key_financials_section = doc.DocumentSection(self,
                                                           starttaglist=["informations financieres", "Chiffres clés"],
                                                           endtaglist=["BFR"])
        self.add_section(secname="KeyFinancials", sec=self._key_financials_section)

        self._bfr_section = doc.DocumentSection(self,
                                                starttaglist=["BFR"],
                                                endtaglist=["Analyse structurelle"])
        self.add_section(secname="BFR", sec=self._bfr_section)

        self._structural_analysis_section = doc.DocumentSection(self,
                                                                starttaglist=["Analyse structurelle"],
                                                                endtaglist=["Ratios de rotation"])
        self.add_section(secname="StructuralAnalysis", sec=self._structural_analysis_section)

        self._turnover_ratios_section = doc.DocumentSection(self,
                                                            starttaglist=["Ratios de rotation"],
                                                            endtaglist=["Analyse des postes d'achat"])
        self.add_section(secname="TurnoverRatios", sec=self._turnover_ratios_section)

        self._tax_and_social_defaults_section = doc.DocumentSection(self,
                                                                    starttaglist=["Defauts de paiements \
                                                                    sociaux et fiscaux"],
                                                                    endtaglist=["Analyse de factures fournisseurs"])
        self.add_section(secname="TaxAndSocialDefaults", sec=self._tax_and_social_defaults_section)

        self._billing_analysis_section = doc.DocumentSection(self,
                                                             starttaglist=["Analyse de factures fournisseurs"],
                                                             endtaglist=["Votre expérience de paiement"])

        self.add_section(secname="BillingAnalysis", sec=self._billing_analysis_section)

    @property
    def summary_section(self):
        return self._sections['Summary']

    @property
    def identity_section(self):
        return self._sections['Identity']

    @property
    def bank_section(self):
        return self._sections['Bank']

    @property
    def key_financials_section(self):
        return self._sections['KeyFinancials']

    @property
    def bfr_section(self):
        return self._sections['BFR']

    @property
    def structural_analysis_section(self):
        return self._sections['StructuralAnalysis']

    @property
    def turnover_ratios_section(self):
        return self._sections['TurnoverRatios']

    @property
    def tax_and_social_defaults_section(self):
        return self._sections['TaxAndSocialDefaults']

    @property
    def billing_analysis_section(self):
        return self._sections['BillingAnalysis']

    def get_requested_amount(self) -> str:
        """
        Get requested amount from section
        :return: float, requested amount
        """
        amount_str = ""
        iline, line, match, rightbit = self.summary_section.get_tag_candidates_lines(["demandee - duree",
                                                                                     "demandee",
                                                                                      "demande",
                                                                                      "pedida"])
        if iline >= 0:
            amount_str = rightbit
        return amount_str

    def get_granted_amount(self) -> str:
        """
        Get requested amount from section
        :return: float, requested amount
        """
        amount_str = ""
        iline, line, match, rightbit = self.summary_section.get_tag_candidates_lines(["accordee - duree",
                                                                                      "accordee",
                                                                                      "accorde",
                                                                                      "accordada"])
        if iline >= 0:
            amount_str = rightbit
        return amount_str


class CreditDocumentCollector(doc.DocumentCollector):

    def __init__(self, path: str):
        super().__init__(path=path)

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
                doct = CreditDocument(os.path.join(self._path, file))
                doct.locate_sections()
                self._documents.loc[file, "Requested amount"] = doct.get_requested_amount()
                self._documents.loc[file, "Granted amount"] = doct.get_granted_amount()
        pass

    def write_doc_stats(self, name: str):
        """
        Write document stats to csv file
        :return:
        """
        self._documents.to_csv(os.path.join("./", name))



