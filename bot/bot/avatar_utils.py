from urllib.request import urlretrieve
from PIL import Image
import os
import requests
from io import BytesIO

import api_client

# Set common size for everything
size = (512, 512)

base_url = "https://www.playgwent.com"

import os
import requests
from PIL import Image
from io import BytesIO


def download_image(url, path, resize_to=None):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # выбросит исключение при ошибке
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        if resize_to:
            img = img.resize(resize_to)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print(f"Image saved successfully: {path}")
        return img
    except Exception as e:
        print(f"Failed to download or process image: {url}, error: {e}")
        return None


async def create_avatar(username):
    avatar, frame, avatar_id = await get_avatar(username)
    if avatar is not None and frame is not None:
        try:
            image = Image.new("RGBA", size)
            image.putalpha(0)

            # Paste avatar onto background with positioning offset
            image.paste(avatar, (157, 160), avatar)
            # image.save('DEBUG-avatar-pasted.png')

            # Paste frame over avatar and background retaining transarency
            image.paste(frame, (0, 0), frame)
        except Exception as e:
            print(e)
            image = Image.open("images/unknown_avatar.jpg").resize((512, 512))
    elif avatar is not None:
        image = Image.open(f"images/{avatar_id}.png").resize((512, 512))
    else:
        image = Image.open("images/unknown_avatar.jpg").resize((512, 512))

    image.save(f'images/{username}.png', format='png')


async def get_avatar(username):
    avatar_img, frame = None, None
    user_id = await api_client.get_player_id(username)
    user_id = user_id['user_id']
    user = await api_client.get_player_ranking(user_id)
    avatar, border = None, None
    if not user.get('vanities', None):
        return avatar_img, frame, avatar
    for item in user['vanities']:
        if item['category'] == 'Border':
            border = item['item_definition_id']
        elif item['category'] == 'Avatar':
            avatar = item['item_definition_id']
    if os.path.exists(f"images/{avatar}.png"):
        avatar_img = Image.open(f"images/{avatar}.png").resize((200, 200))
    if os.path.exists(f"images/{border}.png"):
        frame = Image.open(f"images/{border}.png").resize(size)
    if avatar_img is None or frame is None:
        profile_image_data = await api_client.get_profile_image(username)
        if profile_image_data:
            # if avatar_img is None:
            #     avatar_url = profile_image_data.get("avatar_url", None)
            #     if avatar_url:
            #         try:
            #             urlretrieve(avatar_url, f'images/{avatar}.png')
            #             print("Avatar image saved successfully.")
            #             avatar_img = Image.open(f"images/{avatar}.png").convert("RGBA").resize((200, 200))
            #         except Exception:
            #             avatar_img = None
            # if frame is None:
            #     border_url = profile_image_data.get("border_url", None)
            #     if border_url:
            #         try:
            #             urlretrieve(border_url, f'images/{border}.png')
            #             print("Border image saved successfully.")
            #             frame = Image.open(f"images/{border}.png").convert("RGBA").resize(size)
            #         except Exception as e:
            #             print(e)
            #             frame = None
            if avatar_img is None:
                avatar_url = profile_image_data.get("avatar_url")
                if avatar_url:
                    avatar_img = download_image(avatar_url, f'images/{avatar}.png', resize_to=(200, 200))
            
            if frame is None:
                border_url = profile_image_data.get("border_url")
                if border_url:
                    frame = download_image(border_url, f'images/{border}.png', resize_to=size)


    return avatar_img, frame, avatar

# username = input()
# create_avatar(username)