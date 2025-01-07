# TelegramBotImage2
This is a Telegram bot that can generate an image according to prompt.
Here is huge a description about how it works. 
First of all you can see 3 files here. 
Tokens, which stores api for tgbot and stable-diffusion AI, and users.db, that stores users' nicknames and id's, are small files that are not really involved into the main logics of a program. Meanwhile, main.py is a dump, that processes everything, starting from creating and storing values in db, till the generating images and stylizing them. 
! Dont forget to input tokens of your tg bot and ai into Tokens file. 

Ok let's review the code. 
Starting from modules that i have used:
    telebot - to interract with telegram, send message, connect bot.
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto - to display user specific elements, like buttons and photos
    request - to interract with ai
    pil - is essential when i worked with images as well as io. They both are used in translation of image from binary representation to the real image.
    random - was used to make random images. Not 1 copy.
    logging - was used in debugging
    sqlite3 - was used in databases, as a dbms.
    atexit - closes data bases and ensures that. Bruh yapping.
Finally Tokens. From there we import bot_token and ai directly. So we can fetch their value and connect their services later. 
Firstly we have initialized our tgbot into bot variable, so we can access it easier later. 
Then we have created data base, namely users. If it exists then we don't create a new one, thanks to the condition and prediction.
Now we have created id row, which is default, when you work with data bases. Primary key and autoincrement are parameters that ensure uniqueness of all id's and the fact that they increate each row. 
The next row is username which is tg username. It has parameter of text so it ensure that the value of username should be string
Third row is telegram_id which stores user's id as a number, since it has integer parameter.
Finally, created_at row has a time value, when user has started a bot. 
