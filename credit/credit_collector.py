import datetime
import os
import re

import credit_document as cd
import textutils as tu
import numpy as np
import pandas as pd
from typing import Union
from company import Company
import credit_request as cr


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

    def collect_objects(self,
                        do_parse: bool = True,
                        verbose: bool = False,
                        doclist: list = None,
                        istart: int = 0,
                        iend: int = 1000,
                        types_to_collect: int = 255) -> pd.DataFrame:
        """

        :param types_to_collect:
        :type doclist: list
        :param doclist:
        :param do_parse:
        :param verbose:
        :param istart:
        :param iend:
        :param types_to_collect:
        :return:
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
        # 1: credit request
        b_credit_request = int(bin(types_to_collect)[3]) == 1
        # 2: financials
        # 3: scoring
        # 4: all
        # please write a function that extract a given bit from a number
        # and returns it as a boolean

        for ifile, file in enumerate(files):
            if doclist or istart <= ifile <= iend:
                if verbose:
                    print(f"Collecting document {file}")
                docu = cd.CreditDocument(path=self._docpath, name=file)
                docu.locate_sections()
                a_comp = None
                if b_company:
                    a_comp = Company()
                    a_comp.link_to_document(docu)
                    a_comp.detect_document_language()
                    a_comp.fill_text_from_credit_document()
                    if do_parse:
                        a_comp.parse()
                    a_comp.insert(self._company_table)
                if b_credit_request:
                    req_id = file.split(".")[0]
                    a_req = cr.CreditRequest(req_id=req_id)
                    a_req.link_to_company(document=docu, cp=a_comp)
                    a_req.fill_text_from_credit_document()
                    if do_parse:
                        a_req.parse()
                    a_req.insert(self._credit_request_table)
        return self._company_table

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


if __name__ == "__main__":
    data_path = "/home/cgeissler/local_data/CCRCredit/FichesCredit"
    out_path = "/home/cgeissler/local_data/CCRCredit/Tables"
    debug_mode = False
    outfilename = "collect_test1"
    if not debug_mode:
        collector = CreditCollector(data_path)
        collector.collect_objects(verbose=True, istart=0, iend=10000, types_to_collect=3)
        collector.write_objects(out_path, outfilename)
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

