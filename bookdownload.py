#!/usr/bin/env python
# coding: utf-8

# In[1]:

import clipboard
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import wget
import requests as rqs
import urllib
import pandas as pd


# In[2]:


incomplete_book_name=clipboard.paste().replace(' ','+')
print (incomplete_book_name)


# In[3]:


# googlereq="https://www.google.com/search?q="+aaa
googleurl='https://www.google.com/search?q='+incomplete_book_name+ "+book+amazon"
print(googleurl)
#googleurl=f(make_googleurl)
#print (googleurl)


# In[4]:


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
#headers = {"user-agent" : USER_AGENT}
headers = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}
googleresp = rqs.get(googleurl, headers=headers)

google_soup=soup(googleresp.content,"html.parser")


# In[5]:


# grab each searching result
google_soup.findAll("div",{"class":"r"})
googlecontainers=google_soup.findAll("div",{"class":"r"})
googlecontainer=googlecontainers[0]
googlecontainer.a["href"]

#now move to amazon 
### stopped here. 
amazonurl=googlecontainer.a["href"]
print("this is amazonurl "+amazonurl)


# In[6]:


## get the full book name
try:
    firstslash=amazonurl.index("uk/")
    bookname1=amazonurl[firstslash+3:]
    secondslash=bookname1.index("/")
    bookname2=bookname1[:secondslash]
    print("this is a good book name from amazon "+bookname2)
except ValueError:
    firstslash=amazonurl.index("om/")
    bookname1=amazonurl[firstslash+3:]
    secondslash=bookname1.index("/")
    bookname2=bookname1[:secondslash]
    print("this is a good book name from amazon "+bookname2)


# In[ ]:


#amazonresp.status_code == 200

## now go to the lib genesis
### make the search string good for the website
bookname3=bookname2.replace("-", "+")
libgenurl="http://gen.lib.rus.ec/search.php?req="+bookname3+"&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
print("this is lib gen url "+libgenurl)


# In[ ]:


# Now we are on the page with many books to choose from. 
## Note that I only want PDF and Epub books

libgen_resp = rqs.get(libgenurl, headers=headers)
libgen_soup=soup(libgen_resp.content,"html.parser")

## now get all book link pdf and epub format.
libgen_soup.findAll("tr",{"valign":"top"})

### Note the first item is just the heading, so the for loop should start with list number 1.

libgen_containers=libgen_soup.findAll("tr",{"valign":"top"})


# book1=libgen_containers[1]
# book1info=book1.find_all("td",{"nowrap":""})
# book_year=book1info[4].text
# book_format=book1info[8].text
# book_download_link=book1info[9].a["href"]
# 
# print(book_year)
# 
# print(book_format)
#         
# print(book_download_link)

# ### now create a csv file

# In[ ]:


filename="{}.csv".format(bookname2)
f=open(filename,"w")


# ### initialize the csv file with a heading

# In[ ]:


csvheaders="book_year, book_format,book_download_link,final_link \n"


# In[ ]:


f.write(csvheaders)


# In[ ]:


#libgen_containers[1]


# In[ ]:


### now i am building the loop. 

for books in libgen_containers[1:]:
    book1info=books.find_all("td",{"nowrap":""})
    book_year=book1info[4].text
    book_format=book1info[8].text
    book_download_link=book1info[9].a["href"]
    
    #print (book_download_link)
    libgen_download_resp = rqs.get(book_download_link, headers=headers)
    libgen_download_soup=soup(libgen_download_resp.content,"html.parser")
    libgen_download_containers=libgen_download_soup.findAll("h2",{"style":"text-align:center"})
    final_link=libgen_download_containers[0].a["href"]
    f.write(book_year+","+book_format+","+  book_download_link+","+ final_link +"\n" )
    
    #print(final_link)


#     print(book_year)
#     print(book_format)
#     print(book_download_link)
#     print(final_link)

# In[ ]:


f.close()


# ## Now for the download link, I need go into the link and get the final download link. 
# libgen_download_resp = rqs.get(book_download_link_test, headers=headers)
# libgen_download_soup=soup(libgen_download_resp.content,"html.parser")
# libgen_download_containers=libgen_download_soup.findAll("h2",{"style":"text-align:center"})
# 
# print(libgen_download_containers)

# type(libgen_download_containers)

# libgen_download_containers[0].a["href"]

# final_link=libgen_download_containers[0].a["href"]
# print(final_link)

# # Now I have the final file link, I will download the latest book and only pdf and epub files. 
# firstly sort by epub, download the latest two;
# then sort by pdf, download the latest two as well. 

# First step is to only keep epub and pdf files. 

# In[ ]:


books = pd.read_csv(filename)


# In[ ]:


books


# In[ ]:


books.head()


# check why 'DataFrame' object has no attribute 'book_format', there is a white space! 

# In[ ]:


books.columns


# In[ ]:


books = books.rename(columns={' book_format': 'book_format'})
books = books.rename(columns={'final_link ': 'final_link'})


# In[ ]:


filter_list=['pdf','epub']
books[books.book_format.isin(filter_list)]
epubandpdfonlybooks=books[books.book_format.isin(filter_list)]


# ### Now download the latest 2 epub books

# In[ ]:


epub=epubandpdfonlybooks[epubandpdfonlybooks.book_format=="epub"].sort_values("book_year",ascending=False)[0:2]["final_link"]


# In[ ]:


epub


# In[ ]:


for links in epub:
    print(links)
    wget.download(links, '{}.epub'.format(bookname2))
    print("one epub downloaded!")


# Now download the latest 2 pdf books

# In[ ]:


pdf=epubandpdfonlybooks[epubandpdfonlybooks.book_format=="pdf"].sort_values("book_year",ascending=False)[0:2]["final_link"]


# In[ ]:


pdf


# In[ ]:


for links in pdf:
    print(links)
    wget.download(links, '{}.pdf'.format(bookname2))
    print("one pdf downloaded!")


# # Done!!!






