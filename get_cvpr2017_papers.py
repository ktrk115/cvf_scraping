from bs4 import BeautifulSoup
import urllib.request as req
from IPython import embed
import pandas as pd
import arxiv

url = "http://cvpr2017.thecvf.com/program/main_conference#program_summary"
res = req.urlopen(url)
soup = BeautifulSoup(res, "html.parser")

df = pd.DataFrame(index=list(range(785)), columns=["Date", "Time", "Location", "#", "Session", "Session Title", "Paper ID", "Paper Title", "Authors", "Title-arxiv", "Abstract", "URL"])
pa_table = soup.select("table")[3]
index = 0
for i in range(len(pa_table.find_all('td'))):
    i_column = i % 9
    if pa_table.find_all('td')[i].string is not None:
        df.iloc[index, i_column] = pa_table.find_all('td')[i].string
    if i_column == 8:
        title = df.iloc[index, 7]
        tokens = title.replace(":", "").replace("-"," ").strip().split()
        s = tokens[0]+"+AND+all:"+"+AND+all:".join(tokens[1:])

        try:
            results = arxiv.query(s, prune=True, start=0, max_results=1)
        except:
            pass

        if len(results) != 0:
            df.iloc[index, 9] = results[0]['title'].replace("\n ", "")
            df.iloc[index, 10] = results[0]['summary'].replace("\n", " ")
            df.iloc[index, 11] = results[0]['pdf_url']

        print(str(index)+"/783 done")
        index += 1

df.to_csv('paper_lists.csv')
