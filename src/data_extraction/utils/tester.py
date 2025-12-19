from bs4 import BeautifulSoup
import re 


def check_no_classes(html):
    soup = BeautifulSoup(html,"html.parser")

    for tag in soup.find_all(['p','div','span']):
        classes = tag.get('class')
        print(classes)



check_no_classes('../../data/extracted_html/F2025C01071/OEBPS/document_1/document_1.html')