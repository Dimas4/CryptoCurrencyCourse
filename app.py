#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
import sqlite3
import urllib
import hmac, hashlib
import requests

from urllib.parse import urlparse, urlencode
import time


class Binance():
    methods = {
        # public methods
        'ping': {'url': 'api/v1/ping', 'method': 'GET', 'private': False},
        'time': {'url': 'api/v1/time', 'method': 'GET', 'private': False},
        'exchangeInfo': {'url': 'api/v1/exchangeInfo', 'method': 'GET', 'private': False},
        'depth': {'url': 'api/v1/depth', 'method': 'GET', 'private': False},
        'trades': {'url': 'api/v1/trades', 'method': 'GET', 'private': False},
        'historicalTrades': {'url': 'api/v1/historicalTrades', 'method': 'GET', 'private': False},
        'aggTrades': {'url': 'api/v1/aggTrades', 'method': 'GET', 'private': False},
        'klines': {'url': 'api/v1/klines', 'method': 'GET', 'private': False},
        'ticker24hr': {'url': 'api/v1/ticker/24hr', 'method': 'GET', 'private': False},
        'tickerPrice': {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},
        'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
        # private methods
        'createOrder': {'url': 'api/v3/order', 'method': 'POST', 'private': True},
        'testOrder': {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
        'orderInfo': {'url': 'api/v3/order', 'method': 'GET', 'private': True},
        'cancelOrder': {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
        'openOrders': {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
        'allOrders': {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
        'account': {'url': 'api/v3/account', 'method': 'GET', 'private': True},
        'myTrades': {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
    }

    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytearray(API_SECRET, encoding='utf-8')

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            kwargs.update(command=name)
            return self.call_api(**kwargs)

        return wrapper

    def call_api(self, **kwargs):

        command = kwargs.pop('command')
        api_url = 'https://api.binance.com/' + self.methods[command]['url']

        payload = kwargs
        headers = {}

        if self.methods[command]['private']:
            payload.update({'timestamp': int(time.time() * 1000)})

            sign = hmac.new(
                key=self.API_SECRET,
                msg=urllib.parse.urlencode(payload).encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            payload.update({'signature': sign})
            headers = {"X-MBX-APIKEY": self.API_KEY}

        if self.methods[command]['method'] == 'GET':
            api_url += '?' + urllib.parse.urlencode(payload)

        response = requests.request(method=self.methods[command]['method'], url=api_url, data=payload, headers=headers)
        return response.json()

bot = Binance(
    API_KEY='key',
    API_SECRET='key'
)

async_mode = None
sl_f = []
l_f = []
l_s = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    zapros = bot.tickerPrice()
    s = 0
    id = 0
    sl_f = {}
    for i in zapros:
        if i['symbol'][-3:] == 'ETH':
            sl_f[i['symbol']] = i['price']

    while s != 120:
        schet = time.time()
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Tex SET js = ? WHERE id = ?", (str(sl_f), id))
        print('Обновило ' + str(id))
        conn.commit()
        cursor.close()
        conn.close()
        id += 1
        s += 1
        n = time.time() - schet
        if n >= 5:
            pass
        else:
            time.sleep(5 - n)
        print('Время ' + str(time.time() - schet))

    print('Вышли из 1-го цикла')
    naz = []
    sl = {}
    id = 0
    idd = 0
    count = 0
    otprav_f = {}
    otprav_s = {}

    while True:
        naz = []
        eto = time.time()
        sred_5min = []
        sred_10min = []
        all_price_new = []
        st_price = []
        st_price_5 = []
        zap = bot.tickerPrice()
        # print(zap)
        for i in zap:
            if i['symbol'][-3:] == 'ETH':
                sl[i['symbol']] = i['price']
                all_price_new.append(i['price'])
                naz.append(i['symbol'])

        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        if count >= 120:
            count = count - 120
        cursor.execute("UPDATE Tex SET js = ? WHERE id = ?", (str(sl), count+1))
        conn.commit()
        cursor.close()
        conn.close()

        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        cursor.execute("SELECT js FROM Tex WHERE id=?", (str(id),))
        all_price_old = cursor.fetchone()

        conn.commit()

        idd = id + 60
        if idd >= 120:
            idd = idd - 120

        cursor.execute("SELECT js FROM Tex WHERE id=?", (str(idd),))
        all_price_old_5 = cursor.fetchone()
        # print(all_price_old_5)

        cursor.close()
        conn.close()
        all_price_old_5 = all_price_old_5[0]
        all_price_old = all_price_old[0]
        all_price_old_5 = eval(all_price_old_5)
        all_price_old = eval(all_price_old)

        for i in all_price_old_5:
            if i[-3:] == 'ETH':
                st_price_5.append(all_price_old_5[i])

        for i in all_price_old:
            if i[-3:] == 'ETH':
                st_price.append(all_price_old[i])

        for i in range(0, len(st_price)):
            sred_10min.append((float(all_price_new[i]) - float(st_price[i])) / float(st_price[i]) * 100)
            sred_5min.append((float(all_price_new[i]) - float(st_price_5[i])) / float(st_price_5[i]) * 100)

        id += 1

        count += 1

        otprav_f['Name'] = naz
        otprav_f['Price'] = sred_10min
        otprav_s['Name'] = naz
        otprav_s['Price'] = sred_5min

        socketio.emit('my_pos',
                      {'data': otprav_f, 'count': count, 'vt' : otprav_s},
                      namespace='/test')
        print(otprav_f)
        tek_t = time.time() - eto
        if tek_t >= 5:
            pass
        else:
            time.sleep(time.time() - tek_t)
        print('Время ' + str(time.time() - tek_t))


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
