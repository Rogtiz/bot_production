from typing import OrderedDict
import api_client
import pycountry
from aiogram.utils.markdown import link

GWENT_SITE_AVAILABILITY_ERROR_MESSAGE = ("Недостаточно данных: сезон только начался или возникли проблемы на стороне официального "
                    "сайта.\n\nThe command is currently unavailable due to a lack of data. The current season has "
                    "just started, or there are technical issues on playgwent.com.")

CHANNEL_LINK = link("Бутеры от Бужи", "https://t.me/gwentnews")

FACTIONS = {
    'Nilfgaard': '🔆 NG',
    'Scoiatael': '🐿 ST',
    'Syndicate': '💰 SY',
    'Monster': '👹 MO',
    'NorthernKingdom': '⚜️ NR',
    'Skellige': '⚓ SK'
}


def getCountry(code):
    return pycountry.countries.get(alpha_2=code).flag


def format_top_players(players: list[dict]) -> str:
    result = f"# - Country - Nickname - Matches - MMR\n\n"
    lines = []
    for player in players:
        lines.append(
            f"{player['place']}. - {player['country']}\t- {player['nickname']}\t- "
            f"{player['matches']}\t- {player['mmr']}"
        )
    return result + "\n".join(lines)


async def format_mmr_threshold_of_ranks():
    result = f"Place - Country - Nickname - Matches - MMR\n\n"
    # ranks = [8, 32, 200, 500]
    ranks_info = await api_client.get_mmr_threshold_of_ranks()
    ranks = {
        "rank8": 8,
        "rank32": 32,
        "rank200": 200,
        "rank500": 500
    }
    for rank in ranks.keys():
        if ranks_info is None:
            return GWENT_SITE_AVAILABILITY_ERROR_MESSAGE
        result += f"{ranks_info[rank]['place']} - {ranks_info[rank]['country']} - {ranks_info[rank]['nickname']} - {ranks_info[rank]['matches']} - {ranks_info[rank]['mmr']}\n"
    return result


async def format_username_by_place(place: int):
    info = await api_client.get_username_by_place(place)
    if info:
        return f"{info['place']} - {info['country']} - {info['nickname']} - {info['matches']} - {info['mmr']}\n"
    return GWENT_SITE_AVAILABILITY_ERROR_MESSAGE


async def format_ranking_info(username: str):
    user_id = await api_client.get_player_id(username)
    if user_id:
        user_id = user_id['user_id']
        ranking_info = await api_client.get_player_ranking(user_id)
        if ranking_info:
            if 'rank_progression' in ranking_info:
                if ranking_info['rank_progression']:
                    rank = 'Pro' if ranking_info['rank_progression']['rank'] == 0 else ranking_info['rank_progression']['rank']
                else:
                    rank = 'NA'
            else:
                rank = 'NA'
            fixed_username = ranking_info.get('username', username).replace("_", "\\_")
            # fixed_username = re.escape(user.get('username', username))
            # Nickname: [{fixed_username}](https://www.playgwent.com/ru/profile/{fixed_username})
            return (f"Nickname: {fixed_username}\nPlayer Level: {ranking_info['paragon']['player_level']}\n"
                    f"Prestige: {ranking_info['paragon']['paragon_level']}\n"
                    f"Rank: {rank}\n"
                    f"Global Position: {ranking_info.get('position', '0')}\nRegional Position: {ranking_info.get('continental_position', '0')}\n"
                    f"MMR: {ranking_info.get('score', '0')}\n\nRegion/Country: {ranking_info.get('continent', 'NA')}/{ranking_info.get('country', 'NA')}\n{CHANNEL_LINK}")
    return None


async def format_mmr_info(username: str):
    user_id = await api_client.get_player_id(username)
    if user_id:
        user_id = user_id['user_id']
        ranking_info = await api_client.get_player_ranking(user_id)
        if ranking_info:
            username = username.replace("_", "\\_")
            mmr_info = f"Nickname: {username}\n```\nFaction - Current MMR - Peak MMR - Top 4 - Matches\n"
            is_faction_progressions = ranking_info.get('faction_progressions', None)
            if is_faction_progressions is not None:
                # print(user['faction_progressions'])
                for index in range(len(ranking_info['faction_progressions'])):
                    mmr_info += (f"{FACTIONS[ranking_info['faction_progressions'][index]['faction']]}: "
                                 f"{ranking_info['faction_progressions'][index]['faction_progression']['real_score']} | "
                                 f"{ranking_info['faction_progressions'][index]['faction_progression']['real_score_peak']} | "
                                 f"{'Yes' if ranking_info['faction_progressions'][index]['faction_progression']['is_used_for_score_calculation'] else 'No '} | "
                                 f"{ranking_info['faction_progressions'][index]['faction_progression']['games_count']}\n")
            else:
                for key, value in FACTIONS.items():
                    mmr_info += (f"{value}: "
                                 f"1250 | "
                                 f"1250 | "
                                 f"No | "
                                 f"0\n")

            mmr_info += f"\n```\n{CHANNEL_LINK}"
            return mmr_info


async def format_seasonal_info(username: str):
    user_id = await api_client.get_player_id(username)
    if user_id:
        user_id = user_id['user_id']
        ranking_info = await api_client.get_player_ranking(user_id)
        if ranking_info:
            username = username.replace("_", "\\_")
            season_stats = f"Nickname: {username}\n```\nFaction - Wins - Losses - Draws - All - WinRate\n"
            is_faction_games_stats = ranking_info.get('faction_games_stats', None)
            if is_faction_games_stats is not None:
                ranking_info['faction_games_stats'] = sorted(ranking_info['faction_games_stats'],
                                                     key=lambda x: x['faction_games_stats']['wins_count'], reverse=True)
                for index in range(len(ranking_info['faction_games_stats'])):
                    winrate = round((ranking_info['faction_games_stats'][index]['faction_games_stats']['wins_count'] /
                                     ranking_info['faction_games_stats'][index]['faction_games_stats']['games_count']) * 100, 2) if \
                        ranking_info['faction_games_stats'][index]['faction_games_stats']['games_count'] != 0 else 0
                    if winrate == 0.0:
                        winrate = 0
                    season_stats += (f"{FACTIONS[ranking_info['faction_games_stats'][index]['faction']]}: "
                                     f"{ranking_info['faction_games_stats'][index]['faction_games_stats']['wins_count']} | "
                                     f"{ranking_info['faction_games_stats'][index]['faction_games_stats']['losses_count']} | "
                                     f"{ranking_info['faction_games_stats'][index]['faction_games_stats']['draws_count']} | "
                                     f"{ranking_info['faction_games_stats'][index]['faction_games_stats']['games_count']} | {winrate}%\n")

                overall_winrate = round((ranking_info['wins_count'] / ranking_info['games_count']) * 100, 2) if \
                    ranking_info['games_count'] != 0 else 0
                season_stats += (f"\nAll: {ranking_info['wins_count']} | {ranking_info['losses_count']} | "
                                 f"{ranking_info['draws_count']} | {ranking_info['games_count']} | "
                                 f"{overall_winrate}%\n\n```\n{CHANNEL_LINK}")
            else:
                for key, value in FACTIONS.items():
                    season_stats += (f"{value}: "
                                     f"0 | "
                                     f"0 | "
                                     f"0 | "
                                     f"0 | 0%\n")
                season_stats += (f"\nAll: 0 | 0 | "
                                 f"0 | 0 | "
                                 f"0%\n\n```\n{CHANNEL_LINK}")
            return season_stats


async def format_overall_wins_info(username: str):
    user_id = await api_client.get_player_id(username)
    if user_id:
        user_id = user_id['user_id']
        profile_data = await api_client.get_player_profile_data(user_id)
        if profile_data:
            username = username.replace("_", "\\_")
            overall_wins_info = f"Nickname: {username}\n```\nFaction - Wins\n"
            all_wins = 0
            profile_data['stats']['wins'] = dict(sorted(profile_data['stats']['wins'].items(), key=lambda x: x[1], reverse=True))
            for key in profile_data['stats']['wins']:
                all_wins += profile_data['stats']['wins'][key]
                overall_wins_info += f"{FACTIONS[key]}: {profile_data['stats']['wins'][key]}\n"

            overall_wins_info += (f"\nAll: {all_wins}\n```\nGG sent: {profile_data['stats']['ggs_sent_count']}\nGG received: "
                                  f"{profile_data['stats']['ggs_received_count']}\n{CHANNEL_LINK}")
            return overall_wins_info


async def format_collection_info(username: str):
    user_id = await api_client.get_player_id(username)
    if user_id:
        user_id = user_id['user_id']
        deck_info = await api_client.get_player_deck(user_id)
        if deck_info:
            username = username.replace("_", "\\_")
            collection_info = {
                'Neutral': {},
                '🔆 NG': {},
                '🐿 ST': {},
                '💰 SY': {},
                '👹 MO': {},
                '⚜️ NR': {},
                '⚓ SK': {}
            }
            all_current_cards, all_overall_cards = 0, 0
            for type_of_cards in deck_info['collection']['AllCards']:
                print(type_of_cards)
                for faction in deck_info['collection']['AllCards'][type_of_cards]:
                    print(faction)
                    if type_of_cards == 'any':
                        all_current_cards += deck_info['collection']['AllCards'][type_of_cards][faction]
                    if faction == 'Neutral':
                        collection_info[faction][type_of_cards] = deck_info['collection']['AllCards'][type_of_cards][faction]
                        continue
                    collection_info[FACTIONS[faction]][type_of_cards] = deck_info['collection']['AllCards'][type_of_cards][
                        faction]

            for type_of_cards in deck_info['full_collection']['AllCards']:
                for faction in deck_info['full_collection']['AllCards'][type_of_cards]:
                    if type_of_cards == 'any':
                        all_overall_cards += deck_info['full_collection']['AllCards'][type_of_cards][faction]
                    if faction == 'Neutral':
                        collection_info[faction][f'{type_of_cards}_overall'] = \
                            deck_info['full_collection']['AllCards'][type_of_cards][faction]
                        continue
                    collection_info[FACTIONS[faction]][f'{type_of_cards}_overall'] = \
                        deck_info['full_collection']['AllCards'][type_of_cards][faction]

            collection_result = f"Nickname: {username}\n```\nFaction - Default - Premium - All\n\n"
            neutral_info = (f"Neutral: {collection_info['Neutral']['non_premium']}/"
                            f"{collection_info['Neutral']['non_premium_overall']} - "
                            f"{collection_info['Neutral']['premium']}/{collection_info['Neutral']['premium_overall']}"
                            f" - {collection_info['Neutral']['any']}/{collection_info['Neutral']['any_overall']}\n\n")
            # collection_result = f"Nickname: {username}\n```\nFaction - Default - Premium - Any\nNeutral: {collection_info['Neutral']['non_premium']}/{collection_info['Neutral']['non_premium_overall']} - {collection_info['Neutral']['premium']}/{collection_info['Neutral']['premium_overall']} - {collection_info['Neutral']['any']}/{collection_info['Neutral']['any_overall']}\n\n"
            collection_info.pop('Neutral')
            collection_info = OrderedDict(sorted(collection_info.items(), key=lambda x: x[1]['any'], reverse=True))
            for faction, cards in collection_info.items():
                collection_result += (f"{faction}: {cards['non_premium']}/{cards['non_premium_overall']} - "
                                      f"{cards['premium']}/{cards['premium_overall']} - "
                                      f"{cards['any']}/{cards['any_overall']}\n")
            collection_result += f"\n{neutral_info}All: {all_current_cards}/{all_overall_cards}\n```\n{CHANNEL_LINK}"
            return collection_result


async def format_feedback():
    feedback = await api_client.get_feedback()
    if feedback:
        result = "Feedback:\n"
        for feedback_item in feedback:
            result += f"{feedback_item['id']}. {feedback_item['user_id']} - {feedback_item['message']} ({"fixed" if feedback_item['is_fixed'] else "unfixed"})\n"
        return result
    return "There is an error"