from bs4 import BeautifulSoup
from decimal import Decimal


def convert(amount, cur_from, cur_to, date, requests):
    response = requests.get("http://www.cbr.ru/scripts/XML_daily.asp", params={"date_req": date})
    soup = BeautifulSoup(response.content, "xml")
    val1 = Decimal(soup.find('CharCode', text=cur_from).find_next_sibling('Value').string.replace(',', '.'))
    nom1 = int(soup.find('CharCode', text=cur_from).find_next_sibling('Nominal').string.replace(',', '.'))
    amount_rur = Decimal(amount * (val1/nom1))
    val2 = Decimal(soup.find('CharCode', text=cur_to).find_next_sibling('Value').string.replace(',', '.'))
    nom2 = int(soup.find('CharCode', text=cur_to).find_next_sibling('Nominal').string.replace(',', '.'))
    res = Decimal(amount_rur / (val2/nom2))
    result = res.quantize(Decimal('.0001'))
    return result
