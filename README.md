# @FNTbot
The easy and comfortable way to get information about movie sessions at [planetakino.ua](https://planetakino.ua/lvov/) cinemas in Lviv.
## About
- ##### Requests.

It has two variant to get requests: just write text message like as `kingcross, 01.07` or choose a cinema and the date from the suggested options by the bot.
- ##### Available commands:

/help - send an instruction of using the bot to the user.

/stop - send 'bye-message' to the user and delete him from users' list.

/start -
  - First step. Shows a keyboard with available cinemas. When a user chooses one, a bot will create MovieSession object with following fields: today, period, cinema. Updates cinema field, that will represent URL of chosen cinema.
  - Second step. Shows another keyboard with variants of available dates; when a user chooses one, the bot will update the period field with the chosen date.
  - Third step. Bot parses an XML data with sessions in selected cinema. Sends parsed data to the user with following information: a title of film, description, available session and technology at the needed date, URL where you can to buy a ticket.
## Requirements
- Python 3.6.x
- Telegram bot [token](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
## How to run bot locally?
   1. Clone this repository and cd into the cloned folder.
       - SSH - `$ git clone git@github.com:PetrushynskyiOleksii/telegram-bot.git`
       - HTTPS - `$ git clone https://github.com/PetrushynskyiOleksii/telegram-bot.git`
   2. Install virtual virtual environment.
       - using [pyenv](https://github.com/pyenv/pyenv) - `$ pyenv virtualenv 3.6.5 <name of virtualenv>`
       - using [venv](https://docs.python.org/3/library/venv.html#creating-virtual-environments) - `$ python3 -m venv /path/to/new/virtual/environment`
   3. Activate virtual environment.
       - pyenv - `$ pyenv local <name of virtualenv>`
       - venv - `$ source <venv>/bin/activate`
   4. Install project requirements.
      - Base: `$ pip install -r requirements.txt`
      - Dev: `$ pip install -r requirements-dev.txt`
   5. Create config.py file in main module and add a variable the with a token bot.
   `token = <API TOKEN>`
   6. Run main.py file from main module.
   `$ python3 main/main.py`
