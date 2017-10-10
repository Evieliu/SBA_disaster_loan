
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np

# import data
loan = pd.read_csv('Disaster.csv')
disaster = pd.read_csv('Dislook.csv')
# check column data type
loan.dtypes
disaster.dtypes


# In[2]:

# change column data type
loan['LOANTYPE'] = loan['LOANTYPE'].astype(str)
loan['ZIP'] = loan['ZIP'].astype(str)
loan['LOANAPPVDT'] = loan['LOANAPPVDT'].astype(str)
loan['SICCD'] = loan['SICCD'].astype(str)
loan['NAICSCD'] = loan['NAICSCD'].astype(str)
disaster['Service Office'] = disaster['Service Office'].astype(str)
disaster['Declaration FY'] = disaster['Declaration FY'].astype(int)


# In[3]:

# merge two datasets by primary key
loan = loan.merge(disaster, left_on='Disaster Nbr', right_on='Disaster Nbr', how='left')


# In[4]:

# clean column names
loan = loan.rename(columns = {
                                "APPROVALAMT":"Approval_Amt",
                                "LOANAPPVDT":"Approval_Dt",
                                "LOANTYPE":"Loan_Type",
                                "STATE":"Loan_state",
                                "CITY":"Loan_city",
                                "State":"Disaster_state",
                                "Disaster Type":"Disaster_Type",
                                "Disaster Nbr":"Disaster_Nbr", 
                                "Disaster Name":"Disaster_Name", 
                                "Service Office":"Service_Office", 
                                "Declaration Dt":"Declaration_Dt",
                                "Declaration FY":"Declaration_FY",
                                "Deadline Dt": "Deadline_Dt",
                                "Rec Created Dt": "Rec_Created_Dt",
                                "Declaration Type Cd": "Declaration_Type_Cd"
                            })
# add approval year column
loan['Approval_FY'] = loan.Approval_Dt.str[:4].astype(int)


# In[5]:

# select home (not business) loan only
loan = loan.loc[loan['Loan_Type'].isin(['1'])]
# check records with no match
loan[pd.isnull(loan['Declaration_FY'])].Approval_FY.unique()
# all no match records are before 1990, getting rid of them won't affect the analysis
loan = loan.loc[loan['Approval_FY'] > 1990]


# In[6]:

# select disasters declared in past 10 years
loan = loan.loc[loan['Declaration_FY'] >= 2006]


# In[7]:

# transform key dates to correct data type
loan['Approval_Dt2'] = pd.to_datetime(loan['Approval_Dt'], errors='coerce')
loan['Deadline_Dt2'] = pd.to_datetime(loan['Deadline_Dt'], errors='coerce')
loan['Declaration_Dt2'] = pd.to_datetime(loan['Declaration_Dt'], errors='coerce')


# In[8]:

# check if there is any null value for key dates
loan[pd.isnull(loan['Approval_Dt2'])].shape
loan[pd.isnull(loan['Deadline_Dt2'])].shape
loan[pd.isnull(loan['Declaration_Dt2'])].shape


# In[9]:

# calculate days between key dates
loan['appv_ddl'] = (loan['Approval_Dt2'] - loan['Deadline_Dt2']).astype('timedelta64[D]')
loan['appv_dcl'] = (loan['Approval_Dt2'] - loan['Declaration_Dt2']).astype('timedelta64[D]')
loan['ddl_dcl'] = (loan['Deadline_Dt2'] - loan['Declaration_Dt2']).astype('timedelta64[D]')


# In[10]:

# check if there is any minus number between dates
loan.loc[loan['ddl_dcl'] < 0].shape
loan.loc[loan['appv_dcl'] < 0].shape
loan.loc[loan['appv_ddl'] < 0].shape


# In[11]:

# which types of disaster incurred most SBA disaster loan?
disaster_type_by_value = pd.pivot_table(loan, 
                          values=['Approval_Amt'],
                          index=['Disaster_Type'],
                          aggfunc=np.sum)
disaster_type_by_value = disaster_type_by_value.sort_values(by=['Approval_Amt'], ascending=False)
disaster_type_by_value
# answer: hurricane


# In[12]:

# how much did hurricane relief make up the total SBA disaster loan in the past decade?
hurricane_percentage = disaster_type_by_value['Approval_Amt'][0]/disaster_type_by_value['Approval_Amt'].sum()
hurricane_percentage
# answer: 52%


# In[13]:

# get ready to analyze hurricane relief loans
import matplotlib.pyplot as plt
hurricane = loan.loc[loan['Disaster_Type'] == '8']


# In[14]:

# correlation between loan amount and waiting time
ax = hurricane.plot.scatter(x='appv_dcl',y='Approval_Amt',figsize=(12, 8),s=5,
                            label='Days after disaster declaration',color='g')
hurricane.plot.scatter(x='appv_ddl',y='Approval_Amt',figsize=(12, 8),s=5,
                       label='Days after application deadline',color='r',ax=ax)
plt.xlabel('Waiting days')
plt.ylabel('Approved loan amount')
plt.savefig('hurricane_scatter.png')
# conclusion: no correlation


# In[15]:

# distribution of waiting time after declaration
plt.figure()
ax = hurricane['appv_dcl'].plot.hist(bins=20,figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('hurricane_histogram.png')


# In[16]:

# compare between states
# which states have received most SBA disaster loan?
state_by_value = pd.pivot_table(loan, 
                          values=['Approval_Amt'],
                          index=['Disaster_state'],
                          aggfunc=np.sum)
state_by_value.sort_values(by=['Approval_Amt'], ascending=False).head(5)
# answer: NY, NJ, TX, FL, LA


# In[17]:

# waiting time distribution of New York
plt.figure()
ny = loan.loc[loan['Disaster_state'] == 'NY']
ny['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('NY_histogram.png')


# In[18]:

# waiting time distribution of New Jersey
plt.figure()
nj = loan.loc[loan['Disaster_state'] == 'NJ']
nj['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('NJ_histogram.png')


# In[19]:

# waiting time distribution of Texas
plt.figure()
tx = loan.loc[loan['Disaster_state'] == 'TX']
tx['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('TX_histogram.png')


# In[20]:

# waiting time distribution of Florida
plt.figure()
fl = loan.loc[loan['Disaster_state'] == 'FL']
fl['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('FL_histogram.png')


# In[21]:

# waiting time distribution of Louisiana
plt.figure()
la = loan.loc[loan['Disaster_state'] == 'LA']
la['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('LA_histogram.png')


# In[22]:

# waiting time distribution of Puerto Rico (added for news value)
plt.figure()
pr = loan.loc[loan['Disaster_state'] == 'PR']
pr['appv_dcl'].plot.hist(bins=range(0, 1200, 20),figsize=(12, 8))
plt.xlabel('Waiting days')
plt.savefig('PR_histogram.png')

# conclusion: Florida applicants weren't getting SBA loans as fast as other states.


# In[23]:

fl_100 = fl.loc[fl['appv_dcl'] >= 100]
fl_100.shape[0]*100/fl.shape[0]
# 85% of SBA loan applicants in Florida had to wait more than three months for approval


# In[24]:

ny_100 = ny.loc[ny['appv_dcl'] >= 100]
ny_100.shape[0]*100/ny.shape[0]
# only 31% New York applicants waited that long


# In[25]:

# what's the largest disaster loan approved in the past decade?
loan.sort_values(by=['Approval_Amt'],ascending=False)[['BORROWERNAME','Loan_state','Loan_city',
                                                       'Disaster_Nbr','Disaster_Name', 'Disaster_Type',
                                                       'Declaration_Dt2','Deadline_Dt2',
                                                       'Approval_Dt2','Approval_Amt'
                                                      ]].head(5)
# answer: the largest loan is worth $561,900


# In[26]:

# who's been waiting the longest to get their SBA disaster loan approved?
loan.sort_values(by=['appv_dcl'],ascending=False)[['BORROWERNAME','Loan_state','Loan_city',
                                                       'Disaster_Nbr','Disaster_Name', 'Disaster_Type',
                                                       'Declaration_Dt2','Deadline_Dt2',
                                                       'Approval_Dt2','Approval_Amt','appv_dcl'
                                                      ]].head(5)
# answer: William Grella from New York waited almost three years for the loan approval after Hurricane Sandy

