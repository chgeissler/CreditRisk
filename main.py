import os
import credit.credit_document as cd
import credit.credit_collector as cc
import credit.company as cp
import pandas as pd

# Path: main.py


if __name__ == "__main__":
    data_path = "/home/cgeissler/local_data/CCRCredit/FichesCredit"
    out_path = "/home/cgeissler/local_data/CCRCredit/Tables"
    debug_mode = False
    outfilename = "collect_test_2"
    if not debug_mode:
        collector = cc.CreditCollector(data_path)
        collector.collect_objects(verbose=True, istart=0, iend=10, types_to_collect=3)
        collector.write_objects(out_path, outfilename)
        collector.write_stats(out_path)
    else:
        companies = pd.read_csv(os.path.join(out_path, f"{outfilename}_companies.csv"), index_col=0)
        for idx in companies.index:
            if companies.loc[idx, "IsParsed"] == 0:
                print(f"Re-parsing company {idx}")
                cred_doc = cd.CreditDocument(path=data_path, name=idx)
                company = cp.Company()
                company.link_to_document(cred_doc)
                company.fill_text_from_credit_document()
                company.parse()
    pass






