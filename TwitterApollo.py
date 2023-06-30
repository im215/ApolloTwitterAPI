import tweepy
import csv
from sec_api import QueryApi
import time

companiesListed = []
#Keys for the twtiter API
api_key = "H5gJK1iLo12EjuKVqvwLmOfUE"
api_key_secret = "IsZ4y3cCVUMAYkrSgAqFCNyeBk8t4kuKwUkJ8PU1QE7t0EJHDT"

#Token for OAuth 2.0
bearer_token_c = "AAAAAAAAAAAAAAAAAAAAAKoOogEAAAAAXuyssMw9XN3%2F4Kp0HR2tPPdebog%3DY5Uh2SemvNu5xWBSXRLMqSYQvh2A9tjxsNsccHQcCVY8fbWrPP"

#Esentially username & password
access_key = "1674579809026940928-EPoXZndMWqjLhOSWYuzQ1e5NTg0gUp"
access_key_secret = "LVi95omKELaYy9fJr2YEKh0KCwuKAh9YcyWVtywrTm9eO"

#Client id & Client secret ID; for accessing private data (OAuth 2.0)
client_ID = "NFRRbXZiMU1Vd0tGQnhqTzFRZVM6MTpjaQ"
client_secret_ID = "VjaG-8j5y14uJFUmuukWlEG8pDc64A8U4grKN_mhKUqSqNb_xs"

#Creates a Client object from the Client class; OAuth 2.0 
clientObj = tweepy.Client(bearer_token=bearer_token_c, consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_key, access_token_secret=access_key_secret)

#Key for SEC API
sec_edgar_key = "2f012d3805324e58772d9104da1cb9b2264cfdaf38b739e0d85bcaea7db926a7"

#Creates a QueryAPI object
secAPI = QueryApi(api_key=sec_edgar_key)

query = {
  "query": { "query_string": { 
      "query": "ticker:APO AND formType:\"SC 13D\"",
      "time_zone": "America/New_York"
  } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]
}

response = secAPI.get_filings(query)
filings = response['filings']

# every item in dict_names represents a filing parameter
# and the column name in the CSV file
dict_names = ["id", "accessionNo", "companyName", "companyNameLong", "ticker", 
               "cik", "filedAt", "items", "formType", "periodOfReport", 
               "linkToHtml", "linkToFilingDetails", "linkToTxt", "description", 
               "documentFormatFiles", "dataFiles", "seriesAndClassesContractsInformation",  
               "linkToXbrl", "entities", "groupMembers"]

while(True):
    group_members = []
    dates_filed = []
    #Opens or overwrites a CSV file and creates a DictWriter object (stores data like keys essentially)
    with open('filings.csv', 'w', encoding='UTF8') as f:
        writer = csv.DictWriter(f, fieldnames=dict_names)
        writer.writeheader()
        writer.writerows(filings)
   
    #Takes the completed CSV file and open it in "read" mode
    #Ensures that amendments repeat files are not read
    with open('filings.csv', 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            group_member = line['groupMembers']
            formTyping = line['formType']
            date = line['filedAt']
            if group_member and formTyping == "SC 13D":
                group_members.append(group_member)
                dates_filed.append(date)
                break
    #Turns the group_members item into an actual string
    strippedTextCompany = str(group_members).replace('[','').replace(']','').replace('\'','').replace('\"','')
    date_changed = str(dates_filed[0])[0:10]
    companiesListed.append(strippedTextCompany)


    theText = "Latest documents from SEC.gov shows that Apollo Global Management LTD has had a new SC 13D filed on " + date_changed + " with " + strippedTextCompany + " listed as well. Feel free to take a look!"
    clientObj.create_tweet(text=theText)
    time.sleep(86400)

