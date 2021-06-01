#!/usr/bin/env python
# coding: utf-8

# # <u>Find The Right Cigar</u>

# <b>
#     You struggle to find a cigar that fits your budget but also your quality expectations ? </b>
# <br>
# <br>
# In this project, I propose to build a cigars dataset from scratch. Then I will save it as an Excel file that you will be able to filter by your own in order to find cigars that will fit your expectations.

# <b>In this notebook I will use :</b>
# <br>
# - Web scraping for collecting data on a website.
# - Object oriented programming.
# - Data cleaning for making the datas standardized and usable.
# - Data analysis for checking data quality and getting insights.

# ### 1) Import Python librairies

# In[1]:


from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import warnings;
warnings.filterwarnings('ignore')

get_ipython().run_line_magic('matplotlib', 'inline')


# ### 2) Web Scraping

# Cigars are made in almost all latin american and caribbean countries but there are four main producers : 
# - Cuba. 
# - Dominican Republic.
# - Nicaragua.
# - Honduras.
# <br>
# 

# In[2]:


url = 'https://www.maison-du-cigare.be/cigares/'
terroirs = ['cubains','dominicains','honduriens','nicaraguayens']   


# In[3]:


all_brands = []


for terroir in terroirs:
    

    page = requests.get(url + terroir + '/')
    soup = BeautifulSoup(page.content,'html.parser')
    tableau = soup.find_all(class_='flex_column_table av-equal-height-column-flextable -flextable')



    for i in range(len(tableau)):
        
        for j in tableau[i].find_all('a'):
            text = j.text
            text = text.replace("«\xa0","").replace("\xa0»"," ")
            all_brands.append([text,terroir])
            


# In[7]:


print(all_brands[5:18:2])


# In[8]:


len(all_brands)


# In[9]:


all_cigars = []

for liste in all_brands:
    
    

    page = requests.get('https://www.maison-du-cigare.be/cigares/'+liste[1]+'/'+liste[0]+'/')
    soup = BeautifulSoup(page.content,'html.parser')
    tableau = soup.find_all(class_='av-catalogue-item-inner')

    

    for i in range(len(tableau)):
        
        for j in tableau[i].find_all('div',{'class':'av-catalogue-title av-cart-update-title'}):
            l1 = []
            l1.append(liste[0])
            l1.append(liste[1])
            text = j.text
            text = text.replace("«\xa0","").replace("\xa0»","")
            l1.append(text)
            
            for k in tableau[i].find_all('span',{'class':"woocommerce-Price-amount amount"}):
                text = k.text
                text = text.replace("€","").replace(",",".")
                l1.append(text)
    
            for n in tableau[i].find_all('div',{'class':'av-catalogue-content'}):
                text = n.text 
                text = text.replace(",",".")
                l2 = re.findall(r"[-+]?\d*\.\d+|\d+",text)
                l1 += l2
            
        
        
        all_cigars.append(l1) 


# ### 3) Data quality check & data cleaning

# <b>We can observe in each list the following ranking :</b>
# - list[0] : Unitary Price
# - list[1] : Box Price
# - list[2] : Units per Box
# - list[3] : Cigar Diameter
# - list[4] : Cigar Length
# - list[5] : Cigar Name
# - list[6] : Brand Name
# - list[7] : Origin

# In[10]:


print(all_cigars[:5])


# In[13]:


len(all_cigars[1])


# In[18]:


len8 = 0
other = 0

for sublist in all_cigars:
    
    if len(sublist) == 8:
        len8 += 1
        
    else:
        other += 1
    
print(other*100/len8)


# ### 4) Dataset Creation

# In[19]:


column_name = ['brand', 'origin', 'name','unit_price_eur', 'box_price_eur', 'cig_per_box', 'diameter_cm', 'length_cm']

df = pd.DataFrame(all_cigars, columns=column_name)


# In[20]:


df


# In[23]:


for col in  ["unit_price_eur","box_price_eur","cig_per_box","diameter_cm","length_cm"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')


# In[24]:


df.describe()


# In[25]:


terroirs_dict = {'cubains':'Cuba','dominicains':'Dominican Rep.',
                 'honduriens':'Honduras','nicaraguayens':'Nicaragua'}

for i in range(len(df)):
    if df.iat[i,1] in terroirs_dict:
        df.iat[i,1] = terroirs_dict[df.iat[i,1]]
    else:
        pass


# In[26]:


df.head()


# In[27]:


df.to_excel('cigars_dataset.xlsx', index=False)


# ### 5) Data Analysis

# In[29]:


df[['origin','unit_price_eur','diameter_cm','length_cm']].groupby(['origin']).describe().transpose()


# In[89]:


dmean = df[['origin','unit_price_eur','length_cm','diameter_cm']].groupby(['origin']).mean()

fig = dmean.plot.bar(Edgecolor='black',figsize=(15,4))
fig.tick_params(axis='x', labelrotation = 0)


# In[76]:


fig, (ax1, ax2, ax3) = plt.subplots(1,3,figsize=(15,4))

ax1.hist(df[['diameter_cm']])
ax1.set_title('Diameter Repartition')

ax2.hist(df[['length_cm']])
ax2.set_title('Length Repartition')

ax3.hist(df[['unit_price_eur']])
ax3.set_title('Price Repartition')


# <b>Top 5 : Less and more expensive brands</b>

# In[82]:


company = df[['brand','unit_price_eur']].groupby(['brand']).mean()


# In[83]:


col = ['unit_price_eur']
print("5 most expensive brands :",company.nlargest(5, col))
print("")
print("5 less expensive brands :",company.nsmallest(5, col))


# ### 6) Application

# In[80]:


def find_cigars(PriceMin=df['unit_price_eur'].min(),
                PriceMax=df['unit_price_eur'].max(),
                DiamMin=df['diameter_cm'].min(),
                DiamMax=df['diameter_cm'].max(),
                LenMin=df['length_cm'].min(),
                LenMax=df['length_cm'].max(),
                Origin=['Cuba','Nicaragua','Dominican Rep.','Honduras']):
    
    choices =  df.loc[(df['unit_price_eur'] <= PriceMax) & 
                  (df['unit_price_eur'] >= PriceMin) &
                  (df['diameter_cm'] <= DiamMax) &
                  (df['diameter_cm'] >= DiamMin) &
                  (df['length_cm'] <= LenMax) &
                  (df['length_cm'] >= LenMin) &
                  (df['origin'].isin(Origin))]
    
    return choices


# In[81]:


find_cigars(PriceMin=5,PriceMax=6,Origin=['Cuba'])

