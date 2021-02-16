from bs4 import BeautifulSoup
import unittest
import re


def parse(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as html:
        soup = BeautifulSoup(html, "lxml")
        body = soup.find('div', id="bodyContent")

        all_imgs = body.find_all('img')
        fit_imgs = len(
            [x for x in all_imgs if x.get('width') and int(x.get('width')) >= 200]
        )
        imgs = fit_imgs

        all_headers = body.find_all(re.compile('^h[1-6]$'))
        fit_headers = 0
        for header in all_headers:
            child = header.find_all(recursive=False)
            if child:
                child_data = [x.getText() for x in child if x.getText()]
                try:
                    letter = child_data[0][0]
                    if letter in 'ETC':
                        fit_headers += 1
                except IndexError:
                    pass
            else:
                try:
                    letter = header.getText()[0]
                    if letter in 'ETC':
                        fit_headers += 1
                except IndexError:
                    pass
        headers = fit_headers

        links = body.find_all('a')
        max_len = 0
        for link in links:
            curr_max_len = 1
            siblings = link.find_next_siblings()
            for sibling in siblings:
                if sibling.name == 'a':
                    curr_max_len += 1
                    max_len = max(max_len, curr_max_len)
                else:
                    curr_max_len = 0
        linkslen = max_len

        all_lists = body.find_all(['ul', 'ol'])
        count_lists = 0
        for tag in all_lists:
            if not tag.find_parents(['ul', 'ol']):
                count_lists += 1
        lists = count_lists

    return [imgs, headers, linkslen, lists]


class TestParse(unittest.TestCase):
    def test_parse(self):
        test_cases = (
            ('wiki/Stone_Age', [13, 10, 12, 40]),
            ('wiki/Brain', [19, 5, 25, 11]),
            ('wiki/Artificial_intelligence', [8, 19, 13, 198]),
            ('wiki/Python_(programming_language)', [2, 5, 17, 41]),
            ('wiki/Spectrogram', [1, 2, 4, 7]),)

        for path, expected in test_cases:
            with self.subTest(path=path, expected=expected):
                self.assertEqual(parse(path), expected)


if __name__ == '__main__':
    unittest.main()
