from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re
import requests
import os
import datetime
from sys import stdout
import dataDict
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ================== ENVIRONMENT CLEARANCE ================
print("="*13+" ENVIRONMENT CLEARANCE "+"="*13)
options = dataDict.environment_clearance_diCt
print("-" * 50)
print("{:<33} {:<10}".format("OPTIONS", "VALUE TO ENTER"))
print("-" * 50)
for key, value in options.items():
    print("{:<40} {:<10}".format(value[0], key))
print("-" * 50)
option_value = input("Enter Value : ")


#================== YEAR =========================
print("\n================ CHOOSE YEAR ==================")
print("  --  All\n  --  2020\n  --  2019\n  --  2018\n  --  2017\n  --  2016\n  --  2015\n  --  2014")
yearDict = dataDict.yearDict
year_choice = input("Enter year no or ( type 'All' for all year data) : ")

#===================== STATE ===============================
stateDict = dataDict.stateDict
print("\n================ CHOOSE STATE ==================")
print("-"*50)
print("{:<33} {:<10}".format("STATE", "VALUE TO ENTER"))
print("-"*50)
for key,value in stateDict.items():
    print("{:<40} {:<10}".format(key, value))
print("-"*50)
state_choice = input("Enter corresponding number for state : ")

#===================== Project Sector ===========================
project_sector_dict = dataDict.project_sector_dict
print("\n=============== CHOOSE PROJECT SECTOR =====================")
print("-"*57)
print("{:<43} {:<10}".format("PROJECT SECTOR", "VALUE TO ENTER"))
print("-"*57)
for key,value in project_sector_dict.items():
    print("{:<50} {:<10}".format(key, value))
print("-"*50)
project_sector_choice = input("Enter corresponding value for Project Sector : ")

dir_location = input("Enter directory location : ( eg. project/files ) : ")

try :
    main_url = "http://environmentclearance.nic.in/onlinesearch_parivesh_new.aspx?pid=" + options[option_value][1] + "&status=NA&state=" + state_choice + "&year=" + yearDict[year_choice] + "&cat=" + project_sector_choice
except:
    print("Please enter correct values!")
    quit()

data_base_url = "http://environmentclearance.nic.in/attachfileshow.aspx?proposal_no="
pdf_base_url = "http://environmentclearance.nic.in/"

def download_pdf(project_sector_list,year_number_list,data_urls,states_list,proposal_no_list,proposal_names_list,district_list,tehsil_list):
    state_counter = 0
    files_counter = 0
    # ================ Open Each Proposal Url for getting files ========================
    for url in data_urls:
        data_html = urlopen(url, context=ctx).read()
        data_soup = BeautifulSoup(data_html, "html.parser")
        data_tags = data_soup.findAll('a')
        # pdf_urls = []
        # counter += 1
        tag_counter = 0
        stdout.write("\rProposal being downloaded : %s" % proposal_names_list[state_counter])
        for tag in data_tags:
            tag_counter += 1
            pdf_url = pdf_base_url + tag['href']
            full_pdf_name = tag['href'].split("/")
            pdf_name = tag['title'].replace(".pdf", "")
            pdf_name = pdf_name.replace(" ", "_")  # pdf name under each proposal
            new_pdf_url = pdf_url.replace(" ", "%20")  # pdf url under each proposal
            try:
                response = urlopen(new_pdf_url)  # if response 404
            except:
                pass
            #dirname = os.path.dirname(__file__)  # current directory
            dirname = os.getcwd()
            relative_path = dir_location + "/"+ options[option_value][0].replace(" ","_")+'/'+project_sector_list[state_counter]+'/'+ states_list[state_counter] + "/" + district_list[state_counter] + "/" + \
                            tehsil_list[state_counter]+"/"+year_number_list[state_counter] + "/" + proposal_no_list[
                                state_counter]  # for creating directory for each proposal following current directory
            filename = os.path.join(dirname + "/" + relative_path)
            # print("Proposal being downloaded : ",proposal_names_list[state_counter],sep="\r",end="\r",flush=True)

            if not os.path.exists(filename):
                os.makedirs(filename)
            if ".pdf" not in full_pdf_name[-1] and ".PDF" not in full_pdf_name[-1]:
                my_file = relative_path + '/' + proposal_no_list[state_counter] + "_" + pdf_name + ".html"
            else:
                my_file = relative_path + '/' + proposal_no_list[state_counter] + "_" + pdf_name + ".pdf"
            file = open(my_file, 'wb')
            datetime_file = open(relative_path + "/downloaded_on.txt", "w")
            now = datetime.datetime.now()
            date_now = now.strftime("%y-%m-%d")
            time_now = now.strftime("%H:%M:%S")
            datetime_file.write("Downloaded-On : \n")
            datetime_file.write("Date : " + date_now + "\n")
            datetime_file.write("Time : " + time_now + "\n")
            file.write(response.read())
            files_counter+=1
            datetime_file.close()
            file.close()
        state_counter += 1
        print("\nTotal Proposal downloaded till now : ",str(state_counter))
    # pdf_urls.append(pdf_url.replace(" ", "%20"))
    # pdf_urls_list.append(pdf_urls)
    print("-"*59)
    print("Number of proposals downloaded: ",str(state_counter))
    print("Number of files downloaded : ",str(files_counter))


def extract_pdf(soup,page_no="Page 1"):
    tags = soup.findAll('a', {'onclick': re.compile('Openwindowfiles')})
    states          = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_stdname1')})
    proposal_names  = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_Label2')})
    district_names  = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_lbldis1')})
    tehsil_names    = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_lblvill1')})
    year_numbers    = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_datehtml')})
    project_sectors = soup.findAll('span',{'id':re.compile('ctl00_ContentPlaceHolder1_GridView1_.*_std$')})
    print("Proposals found on "+page_no+" : ", str(len(tags)))
    data_urls = []                  # Project Pdf Url List
    states_list = []                # State Names List
    proposal_no_list = []           # Proposal Num List
    proposal_names_list = []        # Proposal Names List
    district_list = []              # District List
    tehsil_list = []                # Tehsil List
    year_number_list = []           # Year Numbers List
    project_sector_list = []        # Project Sectors List
    for i in range(len(tags)):
        s = tags[i]['onclick']
        project_sec = project_sectors[i].text.split("/")[2]
        try:
            project_sec_name = list(project_sector_dict.keys())[list(project_sector_dict.values()).index(project_sec)].replace(" ","_")  # Takes key using value
        except ValueError:
            project_sec = project_sectors[i].text.split("/")[1]
            project_sec_name = list(project_sector_dict.keys())[list(project_sector_dict.values()).index(project_sec)].replace(" ", "_") # Takes key using value if key not founc
        # print(project_sec_name)
        project_sector_list.append(project_sec_name)
        year_slice = year_numbers[i].text
        year_number_list.append(year_slice[-4:len(year_slice)])
        states_list.append(states[i].text)
        proposal_names_list.append(proposal_names[i].text.replace("/",""))
        district_list.append(district_names[i].text)
        tehsil_list.append(tehsil_names[i].text)
        value = s[s.find("(") + 1:s.find(")")].replace("'", "")
        formatted_value = value.split(",")
        p_no = formatted_value[0].replace("/","_")
        proposal_no_list.append(p_no)
        # ========== Getting Response for single proposal ===============
        url = data_base_url + formatted_value[0] + '&Type=' + formatted_value[1] + '&proposal_id=' + formatted_value[2]   # url for each proposal
        data_urls.append(url)
    download_pdf(project_sector_list,year_number_list,data_urls,states_list,proposal_no_list,proposal_names_list,district_list,tehsil_list) # call for downloading pdf

html = urlopen(main_url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")

view_state = soup.find_all("input", {"id":"__VIEWSTATE"})[0]['value']
eventvalidation = soup.find_all("input", {"id":"__EVENTVALIDATION"})[0]['value']
stategenerator = soup.find_all("input",{"id":"__VIEWSTATEGENERATOR"})[0]['value']

#======================= Keyword Search ============================
search_choice = input("Want to perform keyword search ? (y/n) : ")
if search_choice == 'y':
    keyword = input("Enter keyword ( river, sand, gravel ) : ")
    post_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': view_state,
        '__LASTFOCUS': '',
        '__VIEWSTATEENCRYPTED': '',
        # '__ASYNCPOST': 'true',
        'ctl00$ContentPlaceHolder1$textbox2':keyword,
        '__EVENTVALIDATION': eventvalidation,
        '__VIEWSTATEGENERATOR': stategenerator,
        'ctl00$ContentPlaceHolder1$btn': 'Search'
    }
    response = requests.post(main_url, data=post_data)
    soup = BeautifulSoup(response.content, "html.parser")
    extract_pdf(soup)
else :
    # =========== Getting Urls From Table ===================
    html = urlopen(main_url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    extract_pdf(soup)

# Getting Page Numbers
event_target = soup.find_all("a", {"href":re.compile("javascript:__doPostBack")})
event_target_list = []
for t in event_target:
    new_data = re.search('__doPostBack\(\'(.*)\',\'(.*)\'', t["href"])
    event_target_list.append(new_data)

page_size = len(event_target_list[0:])
for link in event_target_list[0:int(page_size/2)]:
    print(link.group(1),link.group(2))
    post_data = {
        '__EVENTTARGET': link.group(1),
        '__EVENTARGUMENT':link.group(2),
        '__VIEWSTATE': view_state,
        '__LASTFOCUS':'',
        '__VIEWSTATEENCRYPTED':'',
        # '__ASYNCPOST': 'true',
        '__EVENTVALIDATION': eventvalidation,
        '__VIEWSTATEGENERATOR':stategenerator
    }
    response = requests.post(main_url, data=post_data)
    next_soup = BeautifulSoup(response.content, "html.parser")
    extract_pdf(next_soup,link.group(2).replace("$"," "))