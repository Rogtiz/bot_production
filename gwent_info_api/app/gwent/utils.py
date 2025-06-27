import math
import httpx
import pycountry
from bs4 import BeautifulSoup
from collections import OrderedDict
import datetime
import time

import requests

from app.gwent.dao import PlayersDAO
from app.bot.dao import PropertiesDAO

FACTIONS = {
    'Nilfgaard': '🔆 NG',
    'Scoiatael': '🐿 ST',
    'Syndicate': '💰 SY',
    'Monster': '👹 MO',
    'NorthernKingdom': '⚜️ NR',
    'Skellige': '⚓ SK'
}

# SEASON_ID = await PropertiesDAO.find_one_or_none(name="season_id").value
API_RANK_URL = 'https://gwent-rankings.gog.com/ranked_2_0/seasons/'


def get_country_flag(code: str) -> str:
    return pycountry.countries.get(alpha_2=code).flag


class GwentAPI:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def get_user_id(self, username: str) -> str | None:
        url = f'https://tournaments.playgwent.com/api/user/search/{username}'
        r = await self.client.get(url)
        if r.status_code == 200:
            data = r.json()
            if data:
                user_id = data[0]['id']
                await PlayersDAO.add_player_if_not_exists(user_id)
                return user_id

        token_resp = await self.client.get('https://auth.gog.com/token', params={
            'grant_type': 'password',
            'username': 'Gwent_Helper',
            'password': 'edwardRA1911',
            'client_id': '48242550540196492',
            'client_secret': 'd9571bba9c10784309a98aa59816696d018c445a0e7b8f979921fba639817392'
        })

        if token_resp.status_code == 200:
            token = token_resp.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            user_resp = await self.client.get(f'https://users.gog.com/users?username={username}', headers=headers)
            if user_resp.status_code == 200:
                data = user_resp.json()
                await PlayersDAO.add_player_if_not_exists(data['id'])
                return data['id']

        return None

    async def get_ranking_info(self, user_id: str, season_id: str) -> dict | None:
        url = f'{API_RANK_URL}{season_id}/users/{user_id}?_version=27'
        resp = await self.client.get(url)
        if resp.status_code == 200:
            return resp.json()
        return None

    async def get_profile_data(self, user_id: str) -> dict | None:
        url = f'https://gwent-profile.gog.com/users/{user_id}/public?_version=27'
        r = await self.client.get(url)
        if r.status_code == 200:
            return r.json()
        return None

    async def get_card_collection(self, user_id: str) -> dict | None:
        url = f'https://gwent-deck.gog.com/users/{user_id}/cards/public'
        params = {
            "_data_version": "111000",
            "_data_version_token": "6542314",
            "_version": "30",
            "build_region": "Global"
        }
        r = await self.client.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        return None

    async def get_profile_page(self, username: str) -> BeautifulSoup | bool:
        url = f"https://www.playgwent.com/en/profile/{username}"
        r = await self.client.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            if soup.find('h2', class_='icon-private'):
                return False
            return soup
        return False

    async def get_profile_image(self, username: str) -> dict | None:
        profile_page = await self.get_profile_page(username)
        if profile_page:
            avatar_img = profile_page.find('div', class_='l-player-details__avatar').find('img')
            if avatar_img:
                avatar_relative_url = avatar_img['src']
                avatar_url = f"https://www.playgwent.com{avatar_relative_url}"
                if avatar_url == "https://www.playgwent.com/img/profile/avatars/0-default.png":
                    avatar_url = None
            else:
                avatar_url = None
            border_img = profile_page.find('div', class_='l-player-details__border').find('img')
            if border_img:
                border_relative_url = border_img['src']
                border_url = f"https://www.playgwent.com{border_relative_url}"
            else:
                border_url = None
            return {
                "avatar_url": avatar_url,
                "border_url": border_url
            }
        return None

    # async def get_ranking_site_info(self, page):
    #     current_datetime = datetime.datetime.now()
    #     current_month_name = current_datetime.strftime("%B")
    #     url = f"https://masters.playgwent.com/en/rankings/gwentfinity-2/{current_month_name.lower()}-season-{current_datetime.year}/1/{page}"

    #     data = []
    #     r1 = await self.client.get(url)
    #     if r1.status_code == 200:
    #         soup = BeautifulSoup(r1.content, 'html.parser')
    #         rows = soup.select('div.c-ranking-table__body > div.c-ranking-table__tr')
    #         data.extend(rows)

    #         print(rows)
    #         print(data)

    #         r2 = await self.client.get(url + "/1/2")
    #         if r2.status_code == 200:
    #             soup2 = BeautifulSoup(r2.content, 'html.parser')
    #             rows2 = soup2.select('div.c-ranking-table__body > div.c-ranking-table__tr')
    #             data.extend(rows2)
    #             return data
    #     return False


class GwentProfileParser:
    def format_collection(self, username: str, user_data: dict) -> str:
        username = username.replace("_", "\\_")
        info = {
            'Neutral': {},
            '🔆 NG': {}, '🐿 ST': {}, '💰 SY': {},
            '👹 MO': {}, '⚜️ NR': {}, '⚓ SK': {}
        }

        all_current = all_total = 0
        for type_card, factions in user_data['collection']['AllCards'].items():
            for faction, val in factions.items():
                if type_card == 'any':
                    all_current += val
                if faction == 'Neutral':
                    info['Neutral'][type_card] = val
                else:
                    info[FACTIONS[faction]][type_card] = val

        for type_card, factions in user_data['full_collection']['AllCards'].items():
            for faction, val in factions.items():
                if type_card == 'any':
                    all_total += val
                if faction == 'Neutral':
                    info['Neutral'][f"{type_card}_overall"] = val
                else:
                    info[FACTIONS[faction]][f"{type_card}_overall"] = val

        result = f"Nickname: {username}\n```\nFaction - Default - Premium - All\n\n"
        neutral = info['Neutral']
        result += f"Neutral: {neutral['non_premium']}/{neutral['non_premium_overall']} - {neutral['premium']}/{neutral['premium_overall']} - {neutral['any']}/{neutral['any_overall']}\n\n"
        info.pop('Neutral')
        info = OrderedDict(sorted(info.items(), key=lambda x: x[1].get('any', 0), reverse=True))
        for faction, cards in info.items():
            result += f"{faction}: {cards['non_premium']}/{cards['non_premium_overall']} - {cards['premium']}/{cards['premium_overall']} - {cards['any']}/{cards['any_overall']}\n"
        result += f"\nAll: {all_current}/{all_total}\n```"
        return result


class GwentSiteParser:
    # async def get_pro_rank(self, number, end_number, page):
    #     # soup = cache.get_data('top_ranking_info')
    #     # if soup is None:
    #     #     soup = cache.get_ranking_site_info()
    #     #     cache.set_data('top_ranking_info', soup)
    #     soup = await GwentAPI().get_ranking_site_info(page)
    #     print(soup)
    #     if not soup:
    #         return ("Недостаточно данных: сезон только начался или возникли проблемы на стороне официального "
    #                 "сайта.\n\nThe command is currently unavailable due to a lack of data. The current season has "
    #                 "just started, or there are technical issues on playgwent.com."), False
    #     if page == 2:
    #         info = soup[1]
    #         places = 20
    #     else:
    #         info = soup[0]
    #         places = 0
    #     data = [[] for n in range(20)]
    #     for n in range(number, end_number):
    #         data[n].append(n + 1 + places)
    #         country_code = str(info[n].find('div').next_sibling.find('i')).split('icon-', 1)[-1].split('"', 1)[
    #             0].upper()
    #         country = get_country_flag(country_code)
    #         data[n].append(country)
    #         player = info[n].find('div').next_sibling.find('strong').text
    #         data[n].append(player)
    #         matches = info[n].find('div').next_sibling.next_sibling.find('p').text.split()[0]
    #         data[n].append(matches)
    #         mmr = info[n].find('div').next_sibling.next_sibling.next_sibling.text.strip()
    #         data[n].append(mmr)
    #         # nilfgaard_score = str(soup[n].findAll('div')[4]).split('">', 1)[-1].split('<', 1)[0].strip()
    #         # data[n].append(nilfgaard_score)
    #         # scoia_score = str(soup[n].findAll('div')[7]).split('">', 1)[-1].split('<', 1)[0].strip()
    #         # data[n].append(scoia_score)
    #         # north_score = str(soup[n].findAll('div')[10]).split('">', 1)[-1].split('<', 1)[0].strip()
    #         # data[n].append(north_score)
    #         # skellige_score = str(soup[n].findAll('div')[13]).split('">', 1)[-1].split('<', 1)[0].strip()
    #         # data[n].append(skellige_score)
    #         # monsters_score = str(soup[n].findAll('div')[16]).split('">', 1)[-1].split('<', 1)[0].strip()
    #         # data[n].append(monsters_score)
    #     result = f"# - Country - Nickname - Matches - MMR\n\n"
    #     for player in data:
    #         if player:
    #             result += f"{player[0]} - {player[1]}\t- {player[2]}\t- {player[3]}\t- {player[4]}\n"
    #     return result, True

    def get_top_ranks(self, page: int):
        if page > 30 or page < 1:
            return "Page can't be more than 30 or less than 1"
        else:
            current_datetime = datetime.datetime.now()
            current_month_name = current_datetime.strftime("%B")
            url = f"https://masters.playgwent.com/en/rankings/gwentfinity-2/{current_month_name.lower()}-season-{current_datetime.year}/1/{page}"
            result = []
            response = requests.get(url)
            counter = 0
            while response.status_code != 200:
                if counter == 4:
                    break
                response = requests.get(url)
                counter += 1
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # prorank_description = soup.find('li', {'class': 'current'}).text.strip().lower().capitalize()
                soup = soup.find('div', {'class': 'c-ranking-table__body'}).findAll('div', {'class': 'c-ranking-table__tr'})
                for i in range(20):
                    data = {
                            "place": None,
                            "country": None,
                            "nickname": None,
                            "matches": None,
                            "mmr": None
                        }
                    found_place = int(soup[i].find('div').find('p').text)
                    # if found_place == place:
                    data["place"] = found_place
                    country_code = str(soup[i].find('div').next_sibling.find('i')).split('icon-', 1)[-1].split('"', 1)[0].upper()
                    country = get_country_flag(country_code)
                    data["country"] = country
                    player = soup[i].find('div').next_sibling.find('strong').text
                    data["nickname"] = player
                    matches = soup[i].find('div').next_sibling.next_sibling.find('p').text.split()[0]
                    data["matches"] = matches
                    mmr = soup[i].find('div').next_sibling.next_sibling.next_sibling.text.strip()
                    data["mmr"] = mmr
                    # return f"{data[0]} - {data[1]} - {data[2]} - {data[3]} - {data[4]}"
                    result.append(data)
                if result:
                    return result
                return None
            else:
                return None


    def get_mmr_threshold(self, place):
        if place > 2860 or place < 1:
            return "Place can't be more than 2860 or less than 1"
        else:
            current_datetime = datetime.datetime.now()
            current_month_name = current_datetime.strftime("%B")
            url = f"https://masters.playgwent.com/en/rankings/gwentfinity-2/{current_month_name.lower()}-season-{current_datetime.year}/1/{math.ceil(place / 20)}"
            # response = requests.get(url)
            # response = requests.get(url)
            # response = requests.get(url)
            response = requests.get(url)
            counter = 0
            while response.status_code != 200:
                if counter == 4:
                    break
                response = requests.get(url)
                counter += 1
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # prorank_description = soup.find('li', {'class': 'current'}).text.strip().lower().capitalize()
                soup = soup.find('div', {'class': 'c-ranking-table__body'}).findAll('div', {'class': 'c-ranking-table__tr'})
                data = [place]
                for i in range(20):
                    found_place = int(soup[i].find('div').find('p').text)
                    if found_place == place:
                        country_code = str(soup[i].find('div').next_sibling.find('i')).split('icon-', 1)[-1].split('"', 1)[
                            0].upper()
                        country = get_country_flag(country_code)
                        data.append(country)

                        player = soup[i].find('div').next_sibling.find('strong').text
                        data.append(player)

                        matches = soup[i].find('div').next_sibling.next_sibling.find('p').text.split()[0]
                        data.append(matches)

                        mmr = soup[i].find('div').next_sibling.next_sibling.next_sibling.text.strip()
                        data.append(mmr)

                        # return f"{data[0]} - {data[1]} - {data[2]} - {data[3]} - {data[4]}"
                        return {
                            "place": data[0],
                            "country": data[1],
                            "nickname": data[2],
                            "matches": data[3],
                            "mmr": data[4]
                        }
                return None
            else:
                return None
        
    def get_mmr_threshold_of_ranks(self):
        result = {"rank8": None, "rank32": None, "rank200": None, "rank500": None}
        ranks = [8, 32, 200, 500]
        for rank in ranks:
            rank_info = self.get_mmr_threshold(rank)
            if rank_info is None:
                return None
            result[f"rank{rank}"] = rank_info
        return result

