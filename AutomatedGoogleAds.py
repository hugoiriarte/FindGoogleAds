# -*- coding: utf-8 -*-
#Imports
from selenium import webdriver
import time
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from more_itertools import split_after
from selenium.webdriver.chrome.options import Options
import schedule
import datetime
import schedule


def googleSearch():
    """
    Function crawls google searching for Ads using states list and keywords list. If ads are found it will submit found Ad Title with the unique Google Ad URL
    This program will not work unless you replace the output.
    """
    print('')
    print('Executing main function')
    
    #Variables
    states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware', 'Florida','Georgia','Guam','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Marshall Islands','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Palau','Pennsylvania','Puerto Rico','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virgin Island','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
    keywords = ['Marijuana Card', 'Marijuana Clinic', 'Marijuana Doctor', 'MMJ Card', 'MMJ Doctor', 'Cannabis Doctor', 'Medical Marijuana', 'Medical Cannabis', 'Green Harvest', 'Marijuana', 'Cannabis', 'MMJ', 'Weed', 'Marijuana Doctor Cancer']
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    chromedriver = desktop + '/chromedriver'
    #Headless options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('AdCheck-4a4222e376ec.json', scope)
    #Nested for loop to append the keyword with state
    for i in keywords:
        for y in states:
            print('Navigating to google')
            driver.get('https://www.google.com/')
            inputs = driver.find_elements_by_tag_name('input')
            inputs[2].click()
            inputs[2].send_keys(i + ' ' + y, Keys.ENTER)    
            ads = driver.find_elements_by_class_name('ads-ad')
            #User output length of ads found
            print('Found ' + str(len(ads)) + ' ads')
            href = driver.find_elements_by_css_selector('.ads-ad > div > a:nth-child(2)')
            hrefs = []
            #Payload
            splitAds = []
            for q in ads:
                splitAds.append(q.text.split('\n'))
            for w in href:
                hrefs.append(w.get_attribute('href'))
            lenAd = len(splitAds)
            lenHref = len(hrefs)
            if lenAd == lenHref:
                for e in range(lenAd):
                    splitAds[e].append(hrefs[e])
            #If ad was found connect to google sheets to append new row with time stamp
            if len(ads) > 0:
                print('Connecting to Google Sheets API..')
                client = gspread.authorize(creds)
                print('Connection successful')
                sheet = client.open('Google Ads Found').sheet1
                #shet values
                data = sheet.get_all_values()
                #time stamp time
                nowP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M").split(' ')
                hour = now[1].split(':')
                #Am or PM
                if int(hour[0]) > 12:
                    timestamp = ["Web Crawler Timestamp: " + str(nowP) + ' PM']
                else:
                    timestamp = ["Web Crawler Timestamp: " + str(nowP) + ' AM']
                #+ 2 to take to account headers
                lastRow = len(data) + 2
                #insert the time stamp
                sheet.insert_row(timestamp, lastRow)
                data = sheet.get_all_values()       
                #Remove empty string
                data = [list(filter(None, lst)) for lst in data]
                #+1 to take timestamp to account
                lastRow = len(data) + 1
                #Append the list of ads to google sheets
                for r in splitAds:
                    #Only if the ad is not in the data pulled from google sheets
                    if r not in data:
                        print('Inserting new row')
                        print(r)
                        sheet.insert_row(r, lastRow)
                    #Output to user that specific ad was already found
                    else:
                        print('Already added')
            print('')
            
    #loop to find just the keywords
    for i in keywords:
        print('Navigating to google')
        driver.get('https://www.google.com/')
        inputs = driver.find_elements_by_tag_name('input')
        inputs[2].click()
        inputs[2].send_keys(i, Keys.ENTER)    
        ads = driver.find_elements_by_class_name('ads-ad')
        print('Found ' + str(len(ads)) + ' ads')
        href = driver.find_elements_by_css_selector('.ads-ad > div > a:nth-child(2)')
        hrefs = []
        #payload
        splitAds = []
        for q in ads:
            splitAds.append(q.text.split('\n'))
        for w in href:
            hrefs.append(w.get_attribute('href'))
        lenAd = len(splitAds)
        lenHref = len(hrefs)
        if lenAd == lenHref:
            for e in range(lenAd):
                splitAds[e].append(hrefs[e])
        if len(ads) > 0:
            print('Connecting to Google Sheets API..')
            client = gspread.authorize(creds)
            print('Connection successful')
            sheet = client.open('Google Ads Found').sheet1
            data = sheet.get_all_values()
            nowP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M").split(' ')
            hour = now[1].split(':')
            if int(hour[0]) > 12:
                timestamp = ["Web Crawler Timestamp: " + str(nowP) + ' PM']
            else:
                timestamp = ["Web Crawler Timestamp: " + str(nowP) + ' AM']
            lastRow = len(data) + 2
            sheet.insert_row(timestamp, lastRow)
            data = sheet.get_all_values()       
            #Remove empty string
            data = [list(filter(None, lst)) for lst in data]
            lastRow = len(data) + 1
            for r in splitAds:
                if r not in data:
                    print('Inserting new row')
                    print(i)
                    sheet.insert_row(r, lastRow)
                else:
                    print('Already Added')
        print('')
        time.sleep(10)
    driver.quit()
    print('End of program')
    print('Will run again in 1 hour..')

#Run main function every hout
schedule.every(60).minutes.do(googleSearch)

while 1:
    schedule.run_pending()
    time.sleep(1)

