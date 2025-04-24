import requests
import telebot
from telebot import types
BOT_TOKEN = "7990991763:AAGWrst_9nnmscCP1GVZjw3A-Nkg_oZ4ItY"
FLASK_SERVER_URL = "http://127.0.0.1:5000/api/update_player"
bot = telebot.TeleBot(BOT_TOKEN)
@bot.message_handler(commands=['join'])
def join_game(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"User{user_id}"
    player_data = {
        "name": username,
        "cat_x": 0,
        "cat_y": 0,
        "coins_collected": 0
    }
    try:
        response = requests.post(FLASK_SERVER_URL, json=player_data, timeout=5)  # Таймаут 5 секунд
        if response.status_code == 200:
            bot.send_message(user_id, "Вы успешно присоединились к игре!")
        else:
            bot.send_message(user_id, "Ошибка при подключении к серверу.")
    except requests.exceptions.RequestException as e:
        bot.send_message(user_id, f"Ошибка подключения к серверу: {e}")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row1 = ["Up"]
    row2 = ["Left", "Down", "Right"]
    keyboard.add(*row1)
    keyboard.row(*row2)
    bot.send_message(user_id, "Управляйте котом с помощью кнопок:", reply_markup=keyboard)
@bot.message_handler(func=lambda m: m.text in ["Up", "Down", "Left", "Right"])
def handle_movement(message):
    user_id, username = message.from_user.id, message.from_user.username or f"User{user_id}"
    direction = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}[message.text]
    try:
        game_state = requests.get("http://127.0.0.1:5000/api/get_game_state", timeout=5).json()
        player = next((p for p in game_state["players"] if p["name"] == username), None)
        if not player:
            bot.send_message(user_id, "Игрок не найден.")
            return
        new_x, new_y = player["cat_x"] + direction[0], player["cat_y"] + direction[1]
        if not (0 <= new_x < 32 and 0 <= new_y < 32):
            bot.send_message(user_id, "Выход за карту!")
            return
        coin_collected = any(c["x"] == new_x and c["y"] == new_y for c in game_state["coins"])
        requests.post(FLASK_SERVER_URL, json={"name": username, "cat_x": new_x, "cat_y": new_y, "coins_collected": player["coins_collected"] + coin_collected}, timeout=5)
        bot.send_message(user_id, f"Кот переместился {message.text}!" + (" Монета собрана!" if coin_collected else ""))
    except Exception as e:
        bot.send_message(user_id, f"Ошибка: {e}")
if __name__ == '__main__':
    bot.polling(none_stop=True)