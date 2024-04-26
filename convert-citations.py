#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
from docx import Document
from pybtex.database.input import bibtex

WORD_FILE = 'Book Chapter_ Evaluating Social Impact of Generative AI Systems.docx'
BIBTEX_FILE = 'social_impact.bib'
ACM_REFS = 'social_impact_ref_list.txt'


# In[2]:


# PARSE BIB FILE ENTRIES

parser = bibtex.Parser()
bib_data = parser.parse_file(BIBTEX_FILE)

bib_dict = {}

for k in bib_data.entries.keys():
    title = bib_data.entries[k].fields['title'].replace('{', '').replace('}', '')
    if 'doi' in bib_data.entries[k].fields:
        url = 'https://doi.org/' + bib_data.entries[k].fields['doi']
    elif 'url' in bib_data.entries[k].fields:
        url = bib_data.entries[k].fields['url']
    else:
        url = ''
    
    bib_dict[k] = (title, url)


# In[3]:


# GET UNIQUELY IDENTIFYING INFO (e.g., title, URL, DOI) FROM ACM REFS

bib_match = {}
without_bib = []

with open(ACM_REFS) as f:
    for l in f.readlines():
        bib_id = re.search('\[\d+\]\s*', l)

        num = l[bib_id.span()[0]:bib_id.span()[1]].strip()[1:-1]
        
        rest = l[bib_id.span()[1]:]
        year = re.search('\d+\.\s+', rest)

        if year is not None:
            rest = rest[year.span()[1]:]

        title = re.search('\.', rest)
        title = rest[:title.span()[1] - 1].lower()

        match = None
        for k in bib_dict:
            if bib_dict[k][0].lower() == title:
                match = k
           
        if match is None:
            url = re.search("(?P<url>https?://[^\s]+)", l)
        
            if url is not None:
                url = url.group("url")

                match = None
                for k in bib_dict:
                    if bib_dict[k][1] == url:
                        match = k
        
        if match is None:
            without_bib.append(l)
        else:
            bib_match[num] = match


# In[4]:


bib_match


# In[5]:


# REPLACE IN-TEXT CITATIONS WITH BIB ENTRIES

document = Document(WORD_FILE)

for paragraph in document.paragraphs:
    while True:
        m = re.search('(\[\d+-\d+\]|\[\d+(,\s*\d+)*\])', paragraph.text)
        if m is None:
            break
        
        cites = m.group(0)[1:-1]
        
        replacement = []
        for c in cites.split(','):
            if c.strip() in bib_match:
                replacement.append(bib_match[c.strip()])
            else:
                replacement.append('p' + c.strip())
        
        paragraph.text = paragraph.text[:m.span()[0]] + \
                        '\citep{' + ', '.join(replacement) + '}' + \
                        paragraph.text[m.span()[1]:]
    
    print(paragraph.text)

document.save('WITH BIB ' + WORD_FILE)


# In[6]:


# SAVE REFS WITHOUT CORRESPONDING BIB ENTRY

with open('without_bib.txt', 'w') as f:
    f.writelines(without_bib)


# In[ ]:




