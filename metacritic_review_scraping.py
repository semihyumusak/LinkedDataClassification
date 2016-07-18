import os.path

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

codec = "utf-8"

with open('MetacriticReviewsNew/ALLLIST.txt', 'rb') as f:
    all = [x.decode("utf8").strip().split('\t') for x in f]
    prevID = 0
    for rec in all:
        try:

            if int(rec[0])>87533:
                try:
                    ID = rec[0]
                    albumURL = rec[1]
                    albumName = rec[2]
                    artistName = rec[3]
                    score = "NULL"
                except Exception as baseexpt:
                    print(rec[0]+baseexpt.__str__())
                with open('MetacriticReviewsNew/ALLLISTScored.txt', 'ab') as f1:


                    reviewURL = 'http://www.metacritic.com/music/'
                    reviewPATH1 = re.sub('[^0-9a-zA-Z-!+()]+', '-',albumName.replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
                    reviewPATH2 = re.sub('[^0-9a-zA-Z-!+()]+', '-',artistName.replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
                    if reviewPATH1.startswith("-"):
                        reviewPATH1 = reviewPATH1[1:len(reviewPATH1)]
                    if reviewPATH1.endswith("-"):
                        reviewPATH1 = reviewPATH1[0:len(reviewPATH1)-1]
                    if reviewPATH2.startswith("-"):
                        reviewPATH2 = reviewPATH2[1:len(reviewPATH2)]
                    if reviewPATH2.endswith("-"):
                        reviewPATH2 = reviewPATH2[0:len(reviewPATH2)-1]
                    reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+reviewPATH2.lower()+"/"+"critic-reviews"

                    try:
                        try:
                            req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                            webpage = urlopen(req).read()
                            soup = BeautifulSoup(webpage)

                            for souprow in soup('div', {'class': 'score_details metascore_details'}):
                                for souprowin in souprow('span', {'itemprop': 'ratingValue'}):
                                    try:
                                        score = (souprowin.text.strip())
                                    except BaseException as b:
                                       a=''# print(b)


                        except BaseException as b:
                            reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+"critic-reviews"
                            req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
                            webpage = urlopen(req).read()
                            soup = BeautifulSoup(webpage)

                            for souprow in soup('div', {'class': 'score_details metascore_details'}):
                                for souprowin in souprow('span', {'itemprop': 'ratingValue'}):
                                    try:
                                        score = (souprowin.text.strip())
                                    except BaseException as b:
                                       print (b.__str__())
                    except BaseException as b:
                         print (b.__str__())
                    print((ID + "\t" + albumURL + '\t' + albumName + '\t' + artistName +'\t' + score + "\n").encode('utf-8'))
                    f1.write((ID + "\t" + albumURL + '\t' + albumName + '\t' + artistName +'\t' + score + "\n").encode('utf-8'))
            prevID = rec[0]
        except BaseException as b:
            print (prevID)

from SPARQLWrapper import SPARQLWrapper, JSON

offset = 0
limit = 1000
count = offset
while offset < 185000:
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        select ?s ?albumname ?artistname  where {?s a dbo:Album. ?s a dbo:MusicalWork. ?s dbp:name ?albumname. ?s dbo:artist ?artist. ?artist dbp:name ?artistname}
        offset """ +
                    str(offset) + """
        limit """ +
                    str(limit))
    offset = offset + limit
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # for row in trainingsetAttributes:
    #     URI = row[1]
    #     ID = row[0]
    #     reviewURL = 'http://www.metacritic.com/music/'
    #     reviewPATH1 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[2].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
    #     reviewPATH2 = re.sub('[^0-9a-zA-Z-!+()]+', '-',row[3].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')

    for result in results["results"]["bindings"]:
        # print(result["s"]["value"] +'\t'+result["albumname"]["value"] +'\t'+result["artistname"]["value"] )


        URI = result["s"]["value"]
        count = count + 1
        ID = str(count)

        with open('MetacriticReviewsNew/ALLLIST.txt', 'ab') as f:
            f.write((ID + "\t" + result["s"]["value"] + '\t' + result["albumname"]["value"] + '\t' +
                     result["artistname"]["value"] + "\n").encode('utf-8'))

            # reviewURL = 'http://www.metacritic.com/music/'
            # reviewPATH1 = re.sub('[^0-9a-zA-Z-!+()]+', '-',result["albumname"]["value"].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
            # reviewPATH2 = re.sub('[^0-9a-zA-Z-!+()]+', '-',result["artistname"]["value"].replace(":",'').replace("(",'').replace(")",'').replace("$",'').replace("ÃƒÂ¡",'a').replace("ÃƒÂ¶",'o').replace("ÃƒÂ©",'e').replace("ÃƒÂ¯",'i').replace('Ã©','e').replace("\\",'').replace("/",'').replace("'",'').replace(".",'').replace(" ","-").replace('[','').replace(']','')).replace('---','-').replace('--','-')
            # if reviewPATH1.startswith("-"):
            #     reviewPATH1 = reviewPATH1[1:len(reviewPATH1)]
            # if reviewPATH1.endswith("-"):
            #     reviewPATH1 = reviewPATH1[0:len(reviewPATH1)-1]
            # if reviewPATH2.startswith("-"):
            #     reviewPATH2 = reviewPATH2[1:len(reviewPATH2)]
            # if reviewPATH2.endswith("-"):
            #     reviewPATH2 = reviewPATH2[0:len(reviewPATH2)-1]
            # reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+reviewPATH2.lower()+"/"+"critic-reviews"
            #
            # try:
            #     import os.path
            #     if not os.path.isfile('MetacriticReviewsNew/'+ID+'.txt'):
            #
            #         try:
            #             req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
            #             webpage = urlopen(req).read()
            #             soup = BeautifulSoup(webpage)
            #             with open('MetacriticReviewsNew/'+ID+'.txt', 'wb') as f:
            #                 f.write((URI+"\n").encode('utf-8'))
            #                 for souprow in soup('ol', {'class': 'reviews critic_reviews'}):
            #                     for souprowin in souprow('div', {'class': 'review_body'}):
            #                         try:
            #                             f.write((souprowin.text.strip()+"\n\t").encode('utf-8'))
            #                         except BaseException as b:
            #                            a=''# print(b)
            #
            #
            #         except BaseException as b:
            #             reviewURLPath = reviewURL+ reviewPATH1.lower()+"/"+"critic-reviews"
            #             req = Request(reviewURLPath, headers={'User-Agent': 'Mozilla/5.0'})
            #             webpage = urlopen(req).read()
            #             soup = BeautifulSoup(webpage)
            #             with open('MetacriticReviewsNew/'+ID+'.txt', 'wb') as f:
            #                 f.write((URI+"\n").encode('utf-8'))
            #                 for souprow in soup('div', {'class': 'review_body'}):
            #                     try:
            #                         f.write((souprow.text.strip()+"\n\t").encode('utf-8'))
            #                     except BaseException as b:
            #                         a=''#print(b)
            #
            # except BaseException as b:
            #     a=''#print(b.__str__() + ID +"-"+ reviewPATH1 +"-"+reviewPATH2)
