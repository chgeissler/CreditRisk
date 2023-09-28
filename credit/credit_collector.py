import datetime
import os
from . import credit_document as cd
import pandas as pd
from . import company as cp
from . import credit_request as cr
from datetime import date


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
        self._stats_table = pd.DataFrame()

    def collect_objects(self,
                        do_parse: bool = True,
                        verbose: bool = False,
                        doclist: list = None,
                        istart: int = 0,
                        iend: int = 1000,
                        types_to_collect: int = 255):
        """

        :param types_to_collect:
        :type doclist: list
        :param doclist:
        :param do_parse:
        :param verbose:
        :param istart:
        :param iend:
        :param types_to_collect:
        :return: Modifies self in place
        """
        if doclist is None:
            doclist = []
        if not doclist:
            files = os.listdir(self._docpath)
        else:
            files = doclist
        # find the first bit of the types_to_collect that is set
        # this is the type of object to collect
        # 0: company
        b_company = int(bin(types_to_collect)[2]) == 1
        if b_company:
            self._stats_table.loc["Companies", "Nb_parsed"] = 0
        # 1: credit request
        b_credit_request = int(bin(types_to_collect)[3]) == 1
        if b_credit_request:
            self._stats_table.loc["Requests", "Nb_parsed"] = 0
        # 2: financials
        # 3: scoring
        # 4: all
        # please write a function that extract a given bit from a number
        # and returns it as a boolean
        nfiles = max(1, min(len(files), iend - istart))
        for ifile, file in enumerate(files):
            if doclist or istart <= ifile <= iend:
                if verbose:
                    print(f"Collecting document {ifile}/{nfiles}: {file}")
                docu = cd.CreditDocument(path=self._docpath, name=file)
                docu.locate_sections()
                a_comp = None
                if b_company:
                    a_comp = cp.Company()
                    a_comp.link_to_document(docu)
                    a_comp.detect_document_language()
                    a_comp.fill_text_from_credit_document()
                    if do_parse:
                        a_comp.parse()
                    a_comp.insert(self._company_table)
                    if a_comp.is_parsed:
                        self._stats_table.loc["Companies", "Nb_parsed"] += 1
                if b_credit_request:
                    req_id = file.split(".")[0]
                    a_req = cr.CreditRequest(req_id=req_id)
                    a_req.link_to_company(document=docu, cp=a_comp)
                    a_req.fill_text_from_credit_document()
                    if do_parse:
                        a_req.parse()
                    a_req.insert(self._credit_request_table)
                    if a_req.is_parsed:
                        self._stats_table.loc["Requests", "Nb_parsed"] += 1
        self._stats_table.loc["Companies", "%_parsed"] = float(self._stats_table.loc["Companies", "Nb_parsed"]
                                                               / nfiles)
        self._stats_table.loc["Companies", "%_parsed"] = float(self._stats_table.loc["Requests", "Nb_parsed"]
                                                               / nfiles)

    def write_objects(self, path: str, name: str):
        """
        Write companies table to file
        :param path: path
        :param name: name
        :return:
        """
        self._company_table.to_csv(os.path.join(path, f"{name}_companies.csv"))
        self._credit_request_table.to_csv(os.path.join(path, f"{name}_credit_requests.csv"))
        pass

    def write_stats(self, out_path: str):
        """

        :param out_path:
        :return:
        """
        today = date.today().strftime("%d-%m-%Y")
        self._stats_table.to_csv(os.path.join(out_path, f"Collect_stats_{today}.csv"))


