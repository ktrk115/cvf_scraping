from bs4 import BeautifulSoup
import urllib.request as req
from IPython import embed
import pandas as pd
import arxiv
import datetime

url = "http://cvpr2018.thecvf.com/program/main_conference"
res = req.urlopen(url)
soup = BeautifulSoup(res, "html.parser")

df = pd.DataFrame(index=list(range(980)), columns=["Paper ID", "Presentation", "Title", "Authors", "Title (arxiv)", "Abstract", "URL"])
pa_tables = soup.select("table")[1:]
index = 0
date_format = "%Y-%m-%dT%H:%M:%SZ"
done = set()
flag = False
for j in range(len(pa_tables)):
    pa_table = pa_tables[j]
    for i in range(len(pa_table.find_all('td'))):
        i_column = i % 4
        if flag:
            if i_column == 0:
                flag = False
            else:
                continue
        if i_column == 0:
            paper_id = pa_table.find_all('td')[i].string
            if paper_id in done:
                flag = True
                continue
        if pa_table.find_all('td')[i].string is not None:
            df.iloc[index, i_column] = pa_table.find_all('td')[i].string
        if i_column == 3:
            title = df.iloc[index, 2]
            tokens = title.replace(":", "").replace("-"," ").strip().split()
            s = tokens[0]+"+AND+all:"+"+AND+all:".join(tokens[1:])

            try:
                results = arxiv.query(s, prune=True, start=0, max_results=10)
            except:
                pass

            if len(results) != 0:
                _, i_most_recent = sorted([(datetime.datetime.strptime(results[t]['updated'], date_format), t) for t, date in enumerate(results)])[-1]

                df.iloc[index, 4] = results[i_most_recent]['title'].replace("\n ", "")
                df.iloc[index, 5] = results[i_most_recent]['summary'].replace("\n", " ")
                df.iloc[index, 6] = results[i_most_recent]['pdf_url']

            print(str(index)+"/980 done")
            done.add(paper_id)
            index += 1

df.to_csv('paper_lists.csv')
