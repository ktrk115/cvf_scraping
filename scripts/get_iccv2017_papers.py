from bs4 import BeautifulSoup
import urllib.request as req
from collections import defaultdict
from IPython import embed
import pandas as pd
import arxiv

url = "http://iccv2017.thecvf.com/program/main_conference#program_summary"
res = req.urlopen(url)
soup = BeautifulSoup(res, "html.parser")

df = pd.DataFrame(index=list(range(785)), columns=["Paper ID", "Paper Title", "Authors", "Title-arxiv", "Abstract", "URL"])
pa_table = soup.select("table")[0]
table = pa_table.find_all('td')
id2paper = defaultdict(dict)
for i in range(len(table)):
    i_column = i % 10
    if i_column == 7:
        paper_id = table[i].font.string.strip()
    elif i_column == 9:
        id2paper[paper_id]['authors'] = table[i].font.string.strip()
    elif i_column == 8:
        title = table[i].font.string.strip()
        id2paper[paper_id]['title'] = title
        tokens = title.replace(":", "").replace("-"," ").strip().split()
        s = tokens[0]+"+AND+all:"+"+AND+all:".join(tokens[1:])

        results = []
        try:
            results = arxiv.query(s, prune=True, start=0, max_results=1)
        except:
            pass

        if len(results) != 0:
            id2paper[paper_id]['arxiv_title'] = results[0]['title'].replace("\n ", "")
            id2paper[paper_id]['summary'] = results[0]['summary'].replace("\n", " ")
            id2paper[paper_id]['pdf_url'] = results[0]['pdf_url']

for i, key in enumerate(id2paper.keys()):
    paper = id2paper[key]
    df.iloc[i, 0] = key
    df.iloc[i, 1] = paper['title']
    df.iloc[i, 2] = paper['authors']
    if 'arxiv_title' in paper.keys():
        df.iloc[i, 3] = paper['arxiv_title']
        df.iloc[i, 4] = paper['summary']
        df.iloc[i, 5] = paper['pdf_url']
df.to_csv('iccv2017_papers.csv')
