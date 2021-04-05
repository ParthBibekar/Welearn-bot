from requests import Session
from bs4 import BeautifulSoup as bs
import requests
import re
import shutil, os

with Session() as s:
    site = s.get("https://welearn.iiserkol.ac.in/login/")
    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("input", {"name":"logintoken"})["value"]
    login_data = {"username":"aaa19ms000","password":"Enter_password", "logintoken":token}
    s.post("https://welearn.iiserkol.ac.in/login/",login_data)
    home_page = s.get("https://welearn.iiserkol.ac.in/my/")
    # print(home_page.content)
    soup = bs(home_page.content, "html.parser")
    with open("output.html", "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify()))
        
    # We need to scrape objects with class="aalink coursename mr-2" 
    # URL from which pdfs to be downloaded
    PH2202 = s.get("https://welearn.iiserkol.ac.in/course/view.php?id=1062")
    # print(PH2202)
    # print(PH2202.content)
    soup = bs(PH2202.content, "html.parser")
    with open("PH2202.html", "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify()))
    
    links = soup.find_all('a',class_="aalink")
    # print(links)
    with open("links.html", "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string
        for link in links:
            file.write(str(link.get('href')) + "\n")
            #print(link.get('href'))
    i=0
    for link in links:
        if ('/mod/resource/view.php' in link.get('href')):
            i += 1
            print("Downloading file: ", i)
  
            # Get response object for link
            response = s.get(link.get('href'))
            
            # Check for already downloaded files files 
            f = open("output.txt", "w")
            f1 = open("output.txt","a")
            print(link, file=f1)
            with open("output.txt") as txt_file:
                for line in txt_file:
                    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', line)
                    
            # Write content in pdf file        
            for j in range(len(urls)):
                if not(j in link):
                    pdf = open(str(i) + ".pdf", 'wb')
                    pdf.write(response.content)
                    pdf.close()
                    
                    # Move files to designated folder
                    #path = os.path.abspath(str(i)+".pdf")
                    #shutil.move(path,"/PH2202")
                    
            print("File ", i, " downloaded")
