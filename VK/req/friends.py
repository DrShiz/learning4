import requests
import datetime
import operator


ACCESS_TOKEN = 'be6db42abe6db42abe6db42a9dbe1d5269bbe6dbe6db42ae0e3b3c1a618dca561073307'
URL_u = 'https://api.vk.com/method/users.get'
URL_f = 'https://api.vk.com/method/friends.get'
CURRENT_YEAR = datetime.datetime.now().year


def calc_age(uid):
    payload_u = {'v': '5.71', 'method': 'users.get', 'oauth': '1', 'access_token': ACCESS_TOKEN, 'user_ids': uid}
    r = requests.get(URL_u, params=payload_u)
    json_data = r.json()['response']
    id = (json_data[0]['id'])
    payload_f = {'v': '5.71', 'method': 'friends.get', 'oauth': '1', 'access_token': ACCESS_TOKEN,
                 'user_id': id, 'fields': 'bdate'}
    r = requests.get(URL_f, params=payload_f)
    json_data = r.json()['response']['items']
    ages_list = list()
    for i in json_data:
        try:
            bd = i['bdate']
            bd = bd[bd.find(".") + 1:]
            bd = bd[bd.find(".") + 1:]
            age = CURRENT_YEAR - int(bd)
            if len(bd) == 4:
                ages_list.append(age)
        except KeyError:
            continue
    dct = {}
    answer = list()
    for i in ages_list:
        if i in dct:
            dct[i] += 1
        else:
            dct[i] = 1
    for i, j in dct.items():
        answer.append((i, j))
    answer = sorted(answer, key=operator.itemgetter(0))
    answer = sorted(answer, key=operator.itemgetter(1), reverse=True)
    return answer


if __name__ == '__main__':
    res = calc_age('reigning')
    print(res)
