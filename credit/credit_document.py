import os
from . import document as doc
import pandas as pd


class CreditDocument(doc.DocumentWithSections):

    def __init__(self,
                 path: str,
                 name: str):
        super().__init__(path=path, name=name)
        self._language = ""
        self._summary_section = doc.DocumentSection(self,
                                                    starttaglist=["Etude client", "Etude garantie",
                                                                  "Etude", "Business report"],
                                                    endtaglist=["Identité"])
        self.summary_section_declare_fields()

        self.add_section(secname="Summary", sec=self._summary_section)

        self._identity_section = doc.DocumentSection(document=self,
                                                     starttaglist=["Identité"],
                                                     endtaglist=["Activité - Modèle économique", "Activité"])
        self.add_section(secname="Identity", sec=self._identity_section)
        self.identity_section_declare_fields()

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

    def summary_section_declare_fields(self):
        """
        Declare fields in Summary section
        :return:
        """
        self._summary_section.declare_field(name="RequestedAmount", tags=["garantie demandee - duree",
                                                                          "garantie demandee",
                                                                          "encours demande",
                                                                          "pedida"])
        self._summary_section.declare_field(name="GrantedAmount", tags=["garantie accordee - duree",
                                                                        "garantie accordee",
                                                                        "encours accorde",
                                                                        "accordada"])
        self._summary_section.declare_field(name="RequestDate", tags=["Date"])
        self._summary_section.declare_field(name="StartDate", tags=["Date debut", "Debut de la garantie"])
        self._summary_section.declare_field(name="EndDate", tags=["Date fin", "Fin de la garantie"])

    def identity_section_declare_fields(self):
        """
        Declare fields in Identity section
        :return:
        """
        self._identity_section.declare_field(name="Identifier", tags=["Siren", "Identifiant"])
        self._identity_section.declare_field(name="VatNumber", tags=["N° TVA", "TVA"])
        self._identity_section.declare_field(name="CreationDate", tags=["Date de création"])
        self._identity_section.declare_field(name="ActivityDescription", tags=["Activité"])
        self._identity_section.declare_field(name="FullName", tags=["Raison sociale", "Nom"])
        self._identity_section.declare_field(name="IndustryCode", tags=["Code APE"])
        self._identity_section.declare_field(name="ZipCode", tags=["Code postal"])
        self._identity_section.declare_field(name="Address", tags=["Adresse"])
        self._identity_section.declare_field(name="City", tags=["CP, Ville", "Ville"])
        self._identity_section.declare_field(name="BankActivity", tags=["Activité bancaire"])
        self._identity_section.declare_field(name="Capital", tags=["Capital social", "Capital"])
        self._identity_section.declare_field(name="LegalForm", tags=["Forme juridique"])
        self._identity_section.declare_field(name="NbEmployees", tags=["Effectif"])
        self._identity_section.declare_field(name="Director", tags=["Dirigeant"])
        self._identity_section.declare_field(name="BusinessAssets", tags=["Fonds de commerce"])
        self._identity_section.declare_field(name="LegalProceedings", tags=["Procédures judiciaires",
                                                                            "Poursuites judiciaires"])

    def bank_section_declare_fields(self):
        self._bank_section.declare_field(name="BankName", tags=["Banques"])
        self._bank_section.declare_field(name="BankName", tags=["Concours bancaires"])

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

    @property
    def language(self):
        return self._language

    def set_language(self, language: str):
        self._language = language

    def insert(self, table: pd.DataFrame):
        """
        Insert document features into a table
        :param table:
        :return: modifies table in place
        """
        doc_idx = self._name
        if doc_idx == "":
            return table
        table.loc[doc_idx, "Language"] = self.language
        table.loc[doc_idx, "NbPages"] = self.nb_pages
        table.loc[doc_idx, "NbSections"] = len(self.sections)
        table.loc[doc_idx, "NbMissingSections"] = self.nb_sections_unlocated()


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
                fullpath = os.path.join(self._path, file)
                doct = CreditDocument(self._path, file)
                doct.locate_sections()
                self._documents.loc[file, "Nb pages"] = doct.nb_pages
                self._documents.loc[file, "Nb sections"] = len(doct.sections)
                self._documents.loc[ifile, "Nb located sections"] = doct.nb_sections_located()
                self._documents.loc[ifile, "Nb missing sections"] = doct.nb_sections_unlocated()
        pass

    def write_doc_stats(self, name: str):
        """
        Write document stats to csv file
        :return:
        """
        self._documents.to_csv(os.path.join("./", name))



