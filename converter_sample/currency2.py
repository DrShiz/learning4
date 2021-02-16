from bs4 import BeautifulSoup
import requests


date = "17/02/2005"
response = requests.get("http://www.cbr.ru/scripts/XML_daily.asp", params={"date_req": date})
soup = BeautifulSoup(response.content, "xml")
cur_from = 'EUR'
print(soup.find('CharCode', text=cur_from).find_next_sibling('Value').string)
