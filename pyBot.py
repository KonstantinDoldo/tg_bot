import telebot
import time
import requests

TG_TOKEN = ''
OWM_TOKEN = ''
weather_url_forecast = "http://api.openweathermap.org/data/2.5/forecast"
weather_url_now = "http://api.openweathermap.org/data/2.5/weather"
moex_url = 'http://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities.json'

alert_hours = ["07:30:00", "12:00:00", "18:00:00"]

bot = telebot.TeleBot(TG_TOKEN)


def get_weather_now(city):
    querystring = {'q': city, 'appid': OWM_TOKEN, 'units': 'metric', 'mode': 'json', 'lang': 'RU'}
    response = requests.get(weather_url_now, params=querystring, timeout=60)
    return response.json()


def get_weather_forecast(city):
    querystring = {'q': city, 'appid': OWM_TOKEN, 'units': 'metric', 'mode': 'json', 'lang': 'RU', 'cnt': '4'}
    response = requests.get(weather_url_forecast, params=querystring, timeout=60)
    return response.json()


def get_exch_rates():
    querystring = {'iss.only': 'marketdata', 'marketdata.columns': 'SECID, LAST'}
    response = requests.get(moex_url, params=querystring, timeout=60)
    return response.json()


@bot.message_handler(content_types='text')
def alerter(message):
    id = message.chat.id  # получаем id чата

    bot.send_message(id, 'init..')
    city = message.text

    # обход значений json'а - к элементу словаря - по имени, к списку по индексу
    while True:
        # delete last message
        form_time = time.strftime("%H:%M:%S")
        if form_time in alert_hours:
            try:
                bot.delete_message(id, last_message.message_id)
            except:
                pass

            data_exch = get_exch_rates()
            weather_now = h6_forecast = h12_forecast = str_exc_rates = ''
            if data_exch['marketdata']['data'][35][1] is not None:
                if data_exch['marketdata']['data'][30][1] is not None:
                    # ~USDRUBTOD = EURRUB / EURUSD
                    str_exc_rates = '$:' + '{:4.1f}'.format(data_exch['marketdata']['data'][35][1] / data_exch['marketdata']['data'][30][1])
                    str_exc_rates += ' E:' + '{:4.1f}'.format(data_exch['marketdata']['data'][35][1])
                else:
                    str_exc_rates = 'exchData contains Null'
            if city.isalpha():
                # current weather
                str_weather_now = get_weather_now(city)
                temp_now = str_weather_now['main']['temp']
                feels_like_now = str_weather_now['main']['feels_like']
                description_now = str_weather_now['weather'][0]['description']
                sunset = str_weather_now['sys']['sunset']
                # lambda?
                weather_now = '{:+3.0f}'.format(temp_now) + '/' + '{:+3.0f}'.format(feels_like_now) + '/' + str(description_now)

                str_weather = get_weather_forecast(city)
                # +6h forecast
                temp = str_weather['list'][1]['main']['temp']
                feels_like = str_weather['list'][1]['main']['feels_like']
                description = str_weather['list'][1]['weather'][0]['description']
                h6_forecast = '+6h: ' + '{:+3.0f}'.format(temp) + '/' + '{:+3.0f}'.format(feels_like) + '/' + str(description)

                # +12h forecast
                temp = str_weather['list'][3]['main']['temp']
                feels_like = str_weather['list'][3]['main']['feels_like']
                description = str_weather['list'][3]['weather'][0]['description']
                h12_forecast = '+12h: ' + '{:+3.0f}'.format(temp) + '/' + '{:+3.0f}'.format(feels_like) + '/' + str(description)

            output = str_exc_rates + '\n' + weather_now + '\n' + h6_forecast + '\n' + h12_forecast
            last_message = bot.send_message(id, output)
            time.sleep(1)  # better way?


if __name__ == '__main__':
    bot.infinity_polling()
