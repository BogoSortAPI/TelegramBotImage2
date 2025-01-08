# TelegramBotImageFREE
This is a Telegram bot that can generate an image according to prompt.

Here is huge a description of my code. 

First of all, you can see 3 files here. 
Tokens, which stores api for tgbot and stable-diffusion AI, and users.db, that stores users' nicknames and id's, are small files that are not really involved into the main logics of a program. Meanwhile, main.py is a dump, that processes everything, starting from creating and storing values in db, till the generating images and stylizing them. 
! Dont forget to input tokens of your tg bot and ai into Tokens file. 

Ok let's review the code. 
Starting from modules that i have used:

    telebot - to interact with telegram, send message, connect bot.
    
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto - to display user specific elements, like buttons and photos
    
    request - to interact with ai
    
    pil - is essential when i worked with images as well as io. They both are used in translation of images from binary representation to the real image.
    
    random - was used to make random images. Not 1 copy.
    
    logging - was used in debugging
    
    sqlite3 - was used in databases, as a dbms.
    
    atexit - closes data bases and ensures that. Bruh yapping.

    Finally, Tokens. From there we import bot_token and ai directly. So, we can fetch their value and connect their services later. 

Firstly, we have initialized our tgbot into bot variable, so we can access it easier later. 
Then we have created database, namely users. If it exists then we don't create a new one, thanks to the condition and prediction.
Now we have created id row, which is base, when you work with data bases. Primary key and autoincrement are parameters that ensure uniqueness of all id's and the fact that they increase its value each row. 
The next row is username which is tg username. It has parameter of text so it ensures that the value of username should be string
Third row is telegram_id which stores user's id as a number, since it has integer parameter.
Finally, created_at row has a time value, when user has started a bot. 
At this stage we initialize all the changes and close connection to our bot.
The following step is connecting ai. At this stage we have 3 variables that are used in stylization. So basically our prompt to bot looks like style(extra_prompt) + our prompt(), but it will be initialized later. 

Now we have language content multi-dimensional dictionary. In order to get text from this dictionary you have to use the next format: LANGUAGE_CONTENT["language"]["message that we need"]
For example, to get message "This is Amazing! ✅", we have to use LANGUAGE_CONTENT["english"]["btn_good"]
User_data dictionary is used in selecting languages.

Function starting_message sends user language selection. Btw, user cannot send prompt if he did not choose language since we have if chat_id not in user_data condition in our generate_images function. At this stage we also add user's username and id into our database. Nearly forgot to mention, this function works when either user clicks start button or types /start command.

Function set language activates when user chose a language itself. Condition "if selected_language in LANGUAGE_CONTENT" ensures that chosen language is in the content. content variable is used to reduce the code. To clarify instead of writing "LANGUAGE_CONTENT["english"]["btn_good"]" 
we can easily write content["btn_good"]. Btw if user wants to change his language he can go to the starting message and choose the language that he wants.

Function query_image creates an image according to the styled prompt. "seed": random.randint(0, 2 ** 32 - 1) ensures that for the same prompt we have random images.
The rest of the code basically makes a request to our api and handles possible error: "except requests.exceptions.RequestException as e"

Function generate_images, meanwhile, sends us generated images. Also, it saves our last input in user_data, so we can address it later when we will stylize our image. At this stage it creates 3 images and converts them into media group so these photos will be sent as 1 message. Also, it creates feedback buttons. 

Buttons and function of their handling:
Btn_Good – has no functionality. Just informs user that he can send image again.
Btn_Regenerate – regenerates image using last_user_prompt.
Btn_stylize – sends options for stylizing images. These options are in buttons. I think there is no need to explain how these buttons are created. So, each iteration it creates a button with text style, which is fetched from the content dictionary.

Function apply_style basically applies style and generates images, but now styled images. It is almost same as generate_image() but it does not generate feedback buttons.

How to use this bot?

Start the bot and select preferred language.

Write a promt. Wait until image is generated. Now give feedback according to the image.

If it satisfies, then click It is awesome and then optionally you can write a new prompt. 

If you do not like it, then click regenerate. But if it is still garbage then you can again regenerate and regenerate again and again, but not so often since api might give an error.

If you want to stylize this image then you can click stylize button. Select your preferred style and image will be regenerated according to this style. 

What am I going to do next? SOON Updates.

Code stuffs: No one cares.
-	Create content variables outside of functions to make them global and reduce code.
-	If message of user is not text, then handle error and send user that he has to send a prompt.
-	Use generate_images() function inside of apply_style.

Content stuffs
-	Create /style command where you can stylize your picture with whatever style you want.
-	Create double stylizing function.
-	Add AI that will generate prompts (He can suggest or improve user_prompts).


