import tweepy
import csv
from sec_api import QueryApi
import time

#Used to ensure repeat tweets are not made
companiesListed = []

#API keys ("consumer keys" for OAuth 1.1 and "client keys" for OAuth 2.0) for the twtiter API
api_key = "ENTER_KEY"
api_key_secret = "ENTER_SECRET_KEY"

#Bearer token
bearer_token_c = "ENTER_BEARER_TOKEN"

#Access tokens
access_key = "ENTER_ACCESS_KEY"
access_key_secret = "ENTER_SECRET_KEY"

# --optional-- Client id & Client secret ID
client_ID = "ENTER_CLIENT_ID"
client_secret_ID = "ENTER_CLIENT_SECRET_ID"

#Creates a Client object from the Client class; uses OAuth 2.0 
clientObj = tweepy.Client(bearer_token=bearer_token_c, consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_key, access_token_secret=access_key_secret)

#Key for SEC API
sec_edgar_key = "ENTER_SEC_API_KEY"

#Creates a QueryAPI object
secAPI = QueryApi(api_key=sec_edgar_key)

#Where "ENTER_TICKER" = ticker symbol of company, "formType" = form type being scraped, and "size" = number of forms to be returned (returned by latest published)
query = {
  "query": { "query_string": { 
      "query": "ticker:ENTER_TICKER AND formType:\"SC 13D\"",
      "time_zone": "America/New_York"
  } },
  "from": "0",
  "size": "10",
  "sort": [{ "filedAt": { "order": "desc" } }]
}

response = secAPI.get_filings(query)
filings = response['filings']

#Every item in dict_names represents a filing parameter
dict_names = ["id", "accessionNo", "companyName", "companyNameLong", "ticker", 
               "cik", "filedAt", "items", "formType", "periodOfReport", 
               "linkToHtml", "linkToFilingDetails", "linkToTxt", "description", 
               "documentFormatFiles", "dataFiles", "seriesAndClassesContractsInformation",  
               "linkToXbrl", "entities", "groupMembers"]

#Loop which checks SEC.gov through API and creates tweet
while(True):
    group_members = []
    dates_filed = []
    #Opens or overwrites a CSV file and creates a DictWriter object (stores data like keys essentially)
    with open('filings.csv', 'w', encoding='UTF8') as f:
        writer = csv.DictWriter(f, fieldnames=dict_names)
        writer.writeheader()
        writer.writerows(filings)
   
    #Takes the completed CSV file and opens it in "read" mode
    #Ensures that amendment files are not read (if you do not know what an amendment file is, no problem)
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
            
    #Turns the group_members list into a single string
    strippedTextCompany = str(group_members).replace('[','').replace(']','').replace('\'','').replace('\"','')
    
    #Indexes the date filed into a readable string using the first 9 characters (Y/D/M format)
    date_changed = str(dates_filed[0])[0:10]

    #Checks to see if company name has been repeated, and, if so, ends the program to avoid repeating dates
    companiesListed.append(strippedTextCompany)
    for name in companiesListed:
        if strippedTextCompany == name:
            break

    #Text to be posted in tweet
    theText = "Latest documents from  SEC.gov shows that Apollo Global Management LTD has had a SC 13D filed on " + date_changed + " with " + strippedTextCompany + " listed as well. Feel free to take a look!"
    
    #Sends out tweet
    clientObj.create_tweet(text=theText)

    #Waits 24hrs in order to check SEC.gov again
    time.sleep(86400)