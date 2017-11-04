#!/usr/bin/env python3

import requests
import untangle
import re

import pdb

import aaindex

EMAIL = "kaleb.olson@gmail.com"

def efetch(pmid: str):
    baseurl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    payload = {"db":"pubmed","id":pmid, "tool":"my_tool", "retmode":"xml", "email":EMAIL} 
    r = requests.get(baseurl, params=payload)
    return untangle.parse(r.text)

def get_pmid_info(pmid: str):
    print("Processing PMID:{}".format(pmid))
    url = "https://www.ncbi.nlm.nih.gov/pubmed/" + pmid
    a = efetch(pmid)
    try:
        article = a.PubmedArticleSet\
                        .PubmedArticle\
                        .MedlineCitation\
                        .Article
    except:
        return {"title": "TODO", "abstract": "TODO", "url": url}

    title = article.ArticleTitle.cdata
    if article.get_elements("Abstract") and type(article.Abstract.AbstractText) is not list: # A very few abstracts have multiple AbstractText elements!
        abstract = article.Abstract.AbstractText.cdata
    else:
        abstract = "TODO"

    url = "https://www.ncbi.nlm.nih.gov/pubmed/" + pmid
    return {"title": title, "abstract": abstract, "url": url}

if __name__ == "__main__":
    aaindex.init_from_file("aaindex1")
    all_aa_records = aaindex.search("")

    condensed_records = {"N/A":[]}
    for record in all_aa_records:
        #print("<start>{}<end>".format(record.ref.strip()))
        if re.match(r'PMID:\s*[0-9]+', record.ref.strip()): # there are records with empty string
            pmid = record.ref.strip().split(":")[1].strip()
            if condensed_records.get(pmid):
                condensed_records[pmid].append(record)
            else:
                condensed_records[pmid] = [record]
        else:
            condensed_records["N/A"].append(record)


    annotated_records = []
    for key, record_set in condensed_records.items():
        if key == "N/A":
            continue
        features = "\n".join([" * {} -- {}".format(feature.key, feature.desc.strip()) for feature in record_set])
        features = re.sub(r'\(.*, [0-9]+\)', '', features)
        info = get_pmid_info(key)
        info["features"] = features
        annotated_records.append(info)

    formated_records = []
    for record in annotated_records:
        fmtstr = """
##{title}
###Abstract
{abstract}

[{url}]({url})

###Features

{features}

###Applicability
TODO
""".format(**record)

        formated_records.append(fmtstr)

    full_text = "\n".join(["% Annotated Amino Acid Features\n", *formated_records])
    with open("aa_annotated.md", 'w') as f:
        f.write(full_text)
