import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.enums import ChatMemberStatus
import logging
import re

from config import settings
import api_client
import formatter
import avatar_utils


logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

logger_info = logging.getLogger('info')
logger_info.setLevel(logging.INFO)
file_handler_info = logging.FileHandler('info.log', mode='w')
formatter_info = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_info.setFormatter(formatter_info)
logger_info.addHandler(file_handler_info)
CHANNEL_LOGS = '-1002020056365'
CHANNEL_SECRET_LOGS = '-1002560711136'

print(settings.TELEGRAM_SECRET_KEY)


bot = Bot(token="6876040609:AAFysbUD9RgQs7VRqO_YkJBAqwOf6JR6pS8")
dp = Dispatcher()

user_data = {}
username_pattern = re.compile(r'^[a-zA-Z0-9_\-.+\u4e00-\u9fff\u3040-\u30ff]{2,20}$', re.UNICODE)
# group_list = database.get_groups_list()

def get_keyboard(player_name):
    buttons = [
        [
            types.InlineKeyboardButton(text="Profile", callback_data=f"check>profile>{player_name}"),
            types.InlineKeyboardButton(text="Current Season", callback_data=f"check>currentseason>{player_name}"),
            types.InlineKeyboardButton(text="MMR Info", callback_data=f"check>mmrinfo>{player_name}")
        ],
        [
            types.InlineKeyboardButton(text="Collection", callback_data=f"check>collection>{player_name}"),
            types.InlineKeyboardButton(text="Overall Info", callback_data=f"check>overallinfo>{player_name}")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# def get_top_keyboard():
#     buttons = [
#         [
#             types.InlineKeyboardButton(text="Top 1 - 10", callback_data="top10"),
#             types.InlineKeyboardButton(text="Top 11 - 20", callback_data="top20"),
#             types.InlineKeyboardButton(text="Top 21 - 30", callback_data="top30")
#         ]
#     ]
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
#     return keyboard

def get_paged_top_keyboard(current_page: int) -> types.InlineKeyboardMarkup:
    buttons = []

    if current_page > 1:
        buttons.append(types.InlineKeyboardButton(text="◀️ Назад", callback_data=f"top_page:{current_page - 1}"))
    else:
        buttons.append(types.InlineKeyboardButton(text=" ", callback_data="noop"))

    buttons.append(types.InlineKeyboardButton(text=f"📄 Стр. {current_page}", callback_data="noop"))

    buttons.append(types.InlineKeyboardButton(text="▶️ Далее", callback_data=f"top_page:{current_page + 1}"))

    return types.InlineKeyboardMarkup(inline_keyboard=[buttons])


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.username is None:
            nick = message.from_user.first_name
            if nick is None:
                nick = message.from_user.id
        else:
            nick = message.from_user.username
        is_registered = await api_client.get_user_by_chat_id(str(message.chat.id))
        if is_registered:
            await bot.send_message(CHANNEL_SECRET_LOGS, f"Used /start, but already registered\n{str(is_registered)}")
        else:
            register_status = await api_client.create_user(str(message.chat.id), str(nick))
            # logger_info.info(f"Зарегистрирован пользователь {nick}")
            await bot.send_message(CHANNEL_SECRET_LOGS, str(register_status))
            if register_status:
                nick = nick.replace("_", "\\_")
                await bot.send_message(CHANNEL_LOGS, f"Зарегистрирован пользователь {nick}")
    await message.answer("Введите никнейм игрока в ГВИНТ, чтобы получить про него информацию\nНажмите на команду "
                         "/help, чтобы получить больше информации\n\nEnter the player’s Gwent nickname to find "
                         "information about that player.\nPress /help to get more information.")


@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer("Команды бота:\n/top - Топ 30 игроков ПРО ранга\n/ranksmmr - ММР игроков ПРО ранга на 8, "
                         "32, 200, 500 местах\n/place - Найти игрока по номеру его места в ПРО ранге\n\nЕсли вы "
                         "заметили "
                         "баг, или есть сообщение для автора бота — можете использовать встроенную команду "
                         "/feedback\n\nCommands:\n/top - Top 30 Pro Rank Players\n/ranksmmr - MMR for Pro Pank "
                         "Postions 8, 32, 200, 500\n/place - Find a player by their rank position\n\nTo report a bug "
                         "or leave a message for the bot’s developer, please use the /feedback command.",
                         parse_mode='Markdown')


# @dp.message(Command('top'))
# async def cmd_top(message: types.Message):
#     data, is_keyboard = gwent_handler.get_pro_rank(0, 10, 1)
#     keyboard = get_top_keyboard()
#     if is_keyboard:
#         await message.answer(data, reply_markup=keyboard)
#     else:
#         await message.answer(data, disable_web_page_preview=True)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    page = 1
    players = await api_client.get_top_players(page)
    if not players:
        return await message.answer("Информация о топе игроков сейчас недоступна.")
    
    text = formatter.format_top_players(players)
    keyboard = get_paged_top_keyboard(page)
    await message.answer(text, reply_markup=keyboard)


@dp.message(Command('ranksmmr'))
async def cmd_ranksmmr(message: types.Message):
    await message.answer(await formatter.format_mmr_threshold_of_ranks(), disable_web_page_preview=True)


@dp.message(Command('place'))
async def cmd_place(message: types.Message, command: CommandObject):
    text = command.args
    print(text)
    if text is not None:
        text = text.split()
        place_result = await formatter.format_username_by_place(int(text[0]))
        await message.answer(place_result)
    else:
        await message.answer("Enter /place [number], for example /place 23")


@dp.message(Command('feedback'))
async def cmd_feedback(message: types.Message, command: CommandObject):
    if message.chat.type != 'private':
        await message.reply("You can only leave feedback in private messages with me")
        return
    text = command.args
    if text is not None:
        print(str(message.chat.id), text)
        feedback = await api_client.create_feedback(str(message.chat.id), text)
        # logger_info.info(f"Пользователь {message.from_user.usernma} оставил feedback: {text}")
        # if message.from_user.username is None:
        #     nick = message.from_user.first_name
        #     if nick is None:
        #         nick = message.from_user.id
        # else:
        #     nick = message.from_user.username
        # nick = nick.replace("_", "\\_")
        nick = message.from_user.mention_markdown()
        await bot.send_message(CHANNEL_SECRET_LOGS, f"{nick} оставил feedback\n{str(feedback)}")
        await bot.send_message(CHANNEL_LOGS, f"{nick} оставил feedback", parse_mode="Markdown")
        await message.answer("Thank you for feedback ❤️")
    else:
        await message.answer("Enter /feedback [message]")


@dp.message(Command('check_rights'))
async def cmd_check_rights(message: types.Message, command: CommandObject):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if message.chat.type != 'private' or not user or user.get("admin_level") < 3:
        return
    text = command.args
    if text:
        text = text.split()
        bot_member = await bot.get_chat_member(chat_id=text[0], user_id=bot.id)

        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            # Теперь вы можете получить доступ к полям, описывающим права администратора
            response_text = "Мои права администратора в этом чате:\n"
            response_text += f"- Может менять информацию о чате: {bot_member.can_change_info}\n"
            response_text += f"- Может удалять сообщения: {bot_member.can_delete_messages}\n"
            response_text += f"- Может приглашать пользователей: {bot_member.can_invite_users}\n"
            response_text += f"- Может ограничивать участников: {bot_member.can_restrict_members}\n"
            response_text += f"- Может закреплять сообщения: {bot_member.can_pin_messages}\n"
            response_text += f"- Может добавлять новых администраторов: {bot_member.can_promote_members}\n"
            # Дополнительные права для каналов
            # if message.chat.type == types.ChatType.CHANNEL:
            #     response_text += f"- Может постить сообщения: {bot_member.can_post_messages}\n"
            #     response_text += f"- Может редактировать сообщения других: {bot_member.can_edit_messages}\n"
            #     response_text += f"- Может управлять видеочатами: {bot_member.can_manage_video_chats}\n"

            # Для aiogram 3.x, некоторые права могут быть вложены в ChatPermissions
            # if isinstance(member, types.ChatMemberAdministrator):
            #     if member.permissions:
            #         response_text += "\nДополнительные разрешения (если применимо):\n"
            #         response_text += f"- Может отправлять сообщения: {member.permissions.can_send_messages}\n"
            #         response_text += f"- Может отправлять медиа: {member.permissions.can_send_media_messages}\n"
            #         # И так далее для всех полей в ChatPermissions

            await message.reply(response_text)
        else:
            await message.reply("Я не администратор в этом чате.")
    else:
        await message.answer("Enter /check_rights [chat_id]")


@dp.message(Command('promote'))
async def cmd_promote(message: types.Message, command: CommandObject):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if message.chat.type != 'private' or not user or user.get("admin_level") < 3:
        return
    text = command.args
    if text:
        text = text.split()
        user_id = text[0]
        chat_id = text[1]
        rights_number = text[2]
        promote_rights = [False, True, False, True, True, True]
        demote_rights = [False, False, False, False, False, False]
        if rights_number = 0:
            rights = demote_rights
        else:
            rights = promote_rights
        try:
            # Получаем текущие права бота в чате
            bot_member = await bot.get_chat_member(chat_id, bot.id)
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR or not bot_member.can_promote_members:
                await message.reply("У меня нет прав для назначения администраторов в этом чате. "
                                    "Пожалуйста, убедитесь, что я администратор и имею право 'Добавление администраторов'.")
                return

            # Назначаем пользователя администратором с определёнными правами
            # Здесь вы можете выбрать, какие права дать новому админу
            # True означает, что право дано, False - нет
            await bot.promote_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                can_change_info=rights[0],        # Может менять информацию о чате
                can_delete_messages=rights[1],    # Может удалять сообщения
                can_invite_users=rights[2],       # Может приглашать пользователей по ссылкам
                can_restrict_members=rights[3],  # (НЕ) может ограничивать/банить участников
                can_pin_messages=rights[4],       # Может закреплять сообщения
                can_promote_members=rights[5],   # (НЕ) может добавлять новых администраторов (чтобы не создавалась цепочка админов)
                # Для каналов:
                # can_post_messages=True,      # Может постить сообщения (только для каналов)
                # can_edit_messages=True,      # Может редактировать сообщения других (только для каналов)
                # can_manage_video_chats=True, # Может управлять видеочатами (только для каналов)
            )
            await message.reply(f"Пользователь с ID {user_id} назначен администратором.")
        except Exception as e:
            await message.reply(f"Произошла ошибка при назначении администратора: {e}")
    else:
        await message.reply("Enter /promote [user_id] [chat_id] [0/1]")


@dp.message(Command('start_new_season'))
async def cmd_update_season(message: types.Message):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if user:
        if user["admin_level"] < 1:
            return
    current_season = await api_client.get_property(key="season_id")
    result = await api_client.update_property(key="season_id", value=str(int(current_season['value']) + 1))
    await bot.send_message(CHANNEL_SECRET_LOGS, f"{str(user)} сменил сезон с\n{str(current_season)} на\n{str(result)}")
    await message.reply(f"season_id successfully changed")


@dp.message(Command('return_previous_season'))
async def cmd_return_season(message: types.Message):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if user:
        if user["admin_level"] < 1:
            return
    current_season = await api_client.get_property(key="season_id")
    result = await api_client.update_property(key="season_id", value=str(int(current_season['value']) - 1))
    await bot.send_message(CHANNEL_SECRET_LOGS, f"{str(user)} сменил сезон с\n{str(current_season)} на\n{str(result)}")
    await message.reply(f"season_id successfully changed")


@dp.message(Command('get_logs'))
async def cmd_get_logs(message: types.Message):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if (user["admin_level"] < 2) or not (message.chat.type == 'private'):
        return
    logs = types.FSInputFile("log.log")
    await message.answer_document(logs)


@dp.message(Command('get_info'))
async def cmd_get_info(message: types.Message):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if (user["admin_level"] < 2) or not (message.chat.type == 'private'):
        return
    logs = types.FSInputFile("info.log")
    await message.answer_document(logs)


# @dp.message(Command('get_day_graphic'))
# async def cmd_get_day_graphic(message: types.Message, command: CommandObject):
#     text = command.args
#     is_players_count = False
#     if database.is_user_admin(message.from_user.username) < 2:
#         return
#     if text is not None:
#         text = text.split()
#         if len(text) == 2 or len(text) == 3:
#             date = text[0].split("/")
#             date = [int(i) for i in date]
#             if len(text) == 3:
#                 if text[2].lower() == 'true':
#                     is_players_count = True
#             result, games_info = winrate_graphics.create_day_winrate_graphic(date, text[1], message.from_user.id, is_players_count)
#             if result:
#                 day_graphic = types.FSInputFile(f"{message.from_user.id}_{text[1]}_barchart.png")
#                 if games_info:
#                     await message.answer_photo(day_graphic, caption=games_info, parse_mode="Markdown")
#                 else:
#                     await message.answer_photo(day_graphic)
#                 os.remove(f"{message.from_user.id}_{text[1]}_barchart.png")
#             else:
#                 await message.answer("Ошибка в команде, либо данная дата не найдена.")
#             return
#     await message.answer("Enter /get_day_graphic [date(example: 10/3/2024)] [table(winrate/winrate_top/winrate_rank)]")


# @dp.message(Command('get_period_graphic'))
# async def cmd_get_period_graphic(message: types.Message, command: CommandObject):
#     text = command.args
#     is_players_count = False
#     if database.is_user_admin(message.from_user.username) < 2:
#         return
#     if text is not None:
#         text = text.split()
#         if len(text) == 3 or len(text) == 4:
#             start_date = text[0].split("/")
#             start_date = [int(i) for i in start_date]
#             end_date = text[1].split("/")
#             end_date = [int(i) for i in end_date]
#             if len(text) == 4:
#                 if text[3].lower() == 'true':
#                     is_players_count = True
#             result, games_info = winrate_graphics.create_period_winrate_graphic(start_date, end_date, text[2],
#                                                                     message.from_user.id, is_players_count)
#             if result:
#                 period_graphic = types.FSInputFile(f"{message.from_user.id}_{text[2]}_graphic.png")
#                 if games_info:
#                     await message.answer_photo(period_graphic, caption=games_info, parse_mode="Markdown")
#                 else:
#                     await message.answer_photo(period_graphic)
#                 os.remove(f"{message.from_user.id}_{text[2]}_graphic.png")
#             else:
#                 await message.answer("Ошибка в команде, либо данная дата не найдена.")
#             return
#     await message.answer("Enter /get_period_graphic [start_date(example: 10/3/2024)] [end_date(example: 15/3/2024)] ["
#                          "table(winrate/winrate_top/winrate_rank)]")


# @dp.message(Command('send_broadcast_message'))
# async def cmd_send_broadcast_message(message: types.Message, command: CommandObject):
#     text = command.args
#     if (database.is_user_admin(message.from_user.username) < 2) or not (message.chat.type == 'private'):
#         return
#     if text is not None:
#         chat_ids = database.get_users_id()
#         for chat_id in chat_ids:
#             try:
#                 await bot.send_message(chat_id, text)
#             except Exception as e:
#                 logging.error(f"Ошибка {e} при отправке сообщения в чат {chat_id}")
#         await message.answer(f"Message broadcast is successful")
#     else:
#         await message.answer("Enter /send_broadcast_message [message]")


@dp.message(Command('get_feedback'))
async def cmd_get_feedback(message: types.Message):
    user = await api_client.get_user_by_chat_id(str(message.chat.id))
    if (user["admin_level"] < 2) or not (message.chat.type == 'private'):
        return
    feedback = await formatter.format_feedback()
    await message.answer(feedback)


# @dp.message(Command('answer_feedback'))
# async def cmd_answer_feedback(message: types.Message, command: CommandObject):
#     text = command.args
#     if (database.is_user_admin(message.from_user.username) < 2) or not (message.chat.type == 'private'):
#         return
#     if text is not None:
#         text = text.split()
#         if len(text) == 2:
#             await message.answer(database.fix_feedback_by_id(text[0]))
#             if text[1] != 'no':
#                 chat_id = database.get_chat_id_by_feedback_id(text[0])
#                 if chat_id is not None:
#                     await bot.send_message(chat_id, "Ответ от разработчика:")
#                     await bot.send_message(chat_id, text[1])
#             return
#     await message.answer("Enter /answer_feedback [id] [message/no]")


# @dp.message(Command('change_access'))
# async def cmd_change_access(message: types.Message, command: CommandObject):
#     text = command.args
#     user = await api_client.get_user_by_chat_id(str(message.chat.id))
#     if (user["admin_level"] < 2) or not (message.chat.type == 'private'):
#         return
#     if text is not None:
#         text = text.split()
#         if len(text) == 2:
#             database.change_ban_info(text[0], int(text[1]))
#             await message.answer(f"Access of user {text[0]} is successfully changed")
#             return
#     await message.answer("Enter /change_access [username] [0 - unban/1 - ban]")


async def update_check_text(message: types.Message, new_text, player_name, callback_id):
    try:
        await message.edit_text(
            new_text,
            reply_markup=get_keyboard(player_name),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except:
        await bot.answer_callback_query(callback_id, "Вы уже на выбранной странице!")


# async def update_top_text(message: types.Message, new_text, callback_id):
#     try:
#         await message.edit_text(
#             new_text[0],
#             reply_markup=get_top_keyboard()
#         )
#     except:
#         await bot.answer_callback_query(callback_id, "Вы уже на выбранной странице!")


@dp.message(lambda message: username_pattern.match(message.text))
async def handle_message(message: types.Message):
    print(message.text)
    username = message.text
    player_info = await formatter.format_ranking_info(username)
    # if (message.chat.type == 'group' or message.chat.type == 'supergroup'):
    #     group_name = message.chat.full_name
    #     if len(group_name) < 3:
    #         group_name = message.chat.username
    #     new_group = await api_client.create_group(name=str(group_name), chat_id=str(message.chat.id))
    #     await bot.send_message(CHANNEL_SECRET_LOGS, f"Добавлена новая группа: \n{str(new_group)}")
    # # if message.from_user.username is None:
    # #     nick = message.from_user.first_name
    # #     if nick is None:
    # #         nick = message.from_user.id
    # # else:
    # #     nick = message.from_user.username
    # # nick = nick.replace("_", "\\_")
    nick = message.from_user.mention_markdown()
    # # logger_info.info(f"{nick} чекает ник {username}")
    # # await bot.send_message(CHANNEL_LOGS, f"{nick} чекает ник {username}")
    if player_info:
        await avatar_utils.create_avatar(message.text)
        image_from_pc = types.FSInputFile(f"images/{username}.png")
        await message.answer_sticker(
            image_from_pc,
            caption="Изображение из файла на компьютере"
        )
        await message.answer(player_info, reply_markup=get_keyboard(message.text), parse_mode="Markdown", disable_web_page_preview=True)
        nick_of_player = username.replace("_", "\\_")
        await bot.send_message(CHANNEL_LOGS, f"{nick} чекает ник {nick_of_player}", parse_mode='Markdown')
        os.remove(f"images/{username}.png")
    else:
        if not (message.chat.type == 'private'):
            return
        await message.answer("Аккаунт пользователя не найден, либо данный пользователь не заходил в игру в текущем сезоне.\n"
                         "The user's account was not found, or this user has not logged into the game in the current season.")


@dp.callback_query(F.data.startswith("check"))
async def callbacks_check(callback: types.CallbackQuery):
    text = re.split(r'>', callback.data)
    action = text[1]
    callback_id = callback.id
    if callback.from_user.username is None:
        nick = callback.from_user.first_name
        if nick is None:
            nick = callback.from_user.id
    else:
        nick = callback.from_user.username
    nick = nick.replace("_", "\\_")
    logger_info.info(f"Nick: {nick}, user_id: {callback.from_user.id}")
    # nick = link(nick, f"tg://user?id={callback.from_user.id}")
    nick = callback.from_user.mention_markdown()
    logger_info.info(f"URL for profile: {nick}")
    # logger_info.info(f"Пользователь {nick} обновил информацию {action} об игроке {text[2]}")
    nick_of_player = text[2].replace("_", "\\_")
    await bot.send_message(CHANNEL_LOGS, f"{nick} обновил информацию {action} об {nick_of_player}",
                           parse_mode='Markdown')
    if action == "profile":
        await update_check_text(callback.message, await formatter.format_ranking_info(text[2]), text[2], callback_id)
    elif action == "collection":
        await update_check_text(callback.message, await formatter.format_collection_info(text[2]), text[2], callback_id)
    elif action == "currentseason":
        await update_check_text(callback.message, await formatter.format_seasonal_info(text[2]), text[2], callback_id)
    elif action == "overallinfo":
        await update_check_text(callback.message, await formatter.format_overall_wins_info(text[2]), text[2], callback_id)
    elif action == "mmrinfo":
        await update_check_text(callback.message, await formatter.format_mmr_info(text[2]), text[2], callback_id)

    await callback.answer()


# # @dp.callback_query(F.data.startswith("top"))
# # async def callbacks_top(callback: types.CallbackQuery):
# #     text = callback.data
# #     callback_id = callback.id
# #     if text == "top10":
# #         await update_top_text(callback.message, gwent_handler.get_pro_rank(0, 10, 1), callback_id)
# #     elif text == "top20":
# #         await update_top_text(callback.message, gwent_handler.get_pro_rank(10, 20, 1), callback_id)
# #     elif text == "top30":
# #         await update_top_text(callback.message, gwent_handler.get_pro_rank(0, 10, 2), callback_id)

# #     await callback.answer()

@dp.callback_query(F.data.startswith("top_page:"))
async def paginate_top(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[1])
    players = await api_client.get_top_players(page)

    if not players:
        await callback.answer("Нет данных на этой странице.", show_alert=True)
        return

    text = formatter.format_top_players(players)
    keyboard = get_paged_top_keyboard(page)

    await callback.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query(F.data == "noop")
async def handle_noop(callback: types.CallbackQuery):
    await callback.answer() 


async def main():
    # logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


