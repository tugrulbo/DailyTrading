import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from binance.client import Client
import talib as ta
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import math
import json


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')
    print("mesaj gönderildi")


liste = ['BTCBUSD', 'ETHBUSD', 'BNBBUSD', 'NEOBUSD', 'LTCBUSD', 'QTUMBUSD', 'ADABUSD', 'XRPBUSD', 'EOSBUSD', 'IOTABUSD', 'XLMBUSD', 'ONTBUSD', 'TRXBUSD', 'ETCBUSD', 'ICXBUSD', 'VETBUSD', 'PAXBUSD', 'LINKBUSD', 'WAVESBUSD', 'BTTBUSD', 'HOTBUSD', 'ZILBUSD', 'ZRXBUSD', 'BATBUSD', 'XMRBUSD', 'ZECBUSD', 'IOSTBUSD', 'DASHBUSD', 'NANOBUSD', 'OMGBUSD', 'ENJBUSD', 'MATICBUSD', 'ATOMBUSD', 'ONEBUSD', 'ALGOBUSD', 'DOGEBUSD', 'TOMOBUSD', 'CHZBUSD', 'BANDBUSD', 'XTZBUSD', 'RVNBUSD', 'HBARBUSD', 'BCHBUSD', 'WRXBUSD', 'BNTBUSD', 'DATABUSD', 'SOLBUSD', 'CTSIBUSD', 'KNCBUSD', 'REPBUSD', 'LRCBUSD', 'COMPBUSD', 'SNXBUSD', 'DGBBUSD', 'GBPBUSD', 'SXPBUSD', 'MKRBUSD', 'MANABUSD', 'AUDBUSD', 'YFIBUSD', 'BALBUSD', 'JSTBUSD', 'SRMBUSD', 'ANTBUSD', 'CRVBUSD', 'SANDBUSD', 'OCEANBUSD', 'NMRBUSD', 'DOTBUSD', 'LUNABUSD',
         'RSRBUSD', 'TRBBUSD', 'BZRXBUSD', 'SUSHIBUSD', 'YFIIBUSD', 'KSMBUSD', 'EGLDBUSD', 'DIABUSD', 'RUNEBUSD', 'FIOBUSD', 'BELBUSD', 'WINGBUSD', 'UNIBUSD', 'NBSBUSD', 'OXTBUSD', 'SUNBUSD', 'AVAXBUSD', 'HNTBUSD', 'FLMBUSD', 'ORNBUSD', 'UTKBUSD', 'XVSBUSD', 'ALPHABUSD', 'AAVEBUSD', 'NEARBUSD', 'FILBUSD', 'INJBUSD', 'AUDIOBUSD', 'CTKBUSD', 'AKROBUSD', 'AXSBUSD', 'HARDBUSD', 'DNTBUSD', 'STRAXBUSD', 'UNFIBUSD', 'ROSEBUSD', 'AVABUSD', 'XEMBUSD', 'SKLBUSD', 'GRTBUSD', 'JUVBUSD', 'PSGBUSD', '1INCHBUSD', 'REEFBUSD', 'OGBUSD', 'ATMBUSD', 'ASRBUSD', 'CELOBUSD', 'RIFBUSD', 'BTCSTBUSD', 'TRUBUSD', 'CKBBUSD', 'TWTBUSD', 'FIROBUSD', 'LITBUSD', 'SFPBUSD', 'DODOBUSD', 'CAKEBUSD', 'ACMBUSD', 'BADGERBUSD', 'FISBUSD', 'OMBUSD', 'PONDBUSD', 'DEGOBUSD', 'ALICEBUSD', 'LINABUSD', 'PERPBUSD', 'RAMPBUSD', 'SUPERBUSD', 'CFXBUSD']
liste_json = []


class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)


def generateStochasticRSI(close_array, timeperiod):
    # 1) ilk aşama rsi değerini hesaplıyoruz.
    rsi = ta.RSI(close_array, timeperiod=timeperiod)

    # 2) ikinci aşamada rsi arrayinden sıfırları kaldırıyoruz.
    rsi = rsi[~np.isnan(rsi)]

    # 3) üçüncü aşamada ise ta-lib stoch metodunu uyguluyoruz.
    stochrsif, stochrsis = ta.STOCH(
        rsi, rsi, rsi, fastk_period=18, slowk_period=6, slowd_period=3)

    return stochrsif, stochrsis


def generateStochRSITable(pair, new_time, stochasticRsiF, stochasticRsiS):
    plt.figure(figsize=(11, 6))
    plt.plot(new_time[116:], stochasticRsiF[100:], label='StochRSI fast')
    plt.plot(new_time[116:], stochasticRsiS[100:], label='StochRSI slow')
    plt.xticks(rotation=90, fontsize=5)
    plt.title(f"Stochastic RSI - {pair} - (4h)")
    plt.xlabel("Open Time")
    plt.ylabel("Value")
    plt.legend()
    plt.show()


def generateSupertrend(close_array, high_array, low_array, atr_period, atr_multiplier):

    try:
        atr = ta.ATR(high_array, low_array, close_array, atr_period)
    except:
        print('exception in atr:', sys.exc_info()[0], 'pair', pair, flush=True)
        print('filename', filename, flush=True)
        return False, False

    previous_final_upperband = 0
    previous_final_lowerband = 0
    final_upperband = 0
    final_lowerband = 0
    previous_close = 0
    previous_supertrend = 0
    supertrend = []
    supertrendc = 0

    for i in range(0, len(close_array)):
        if np.isnan(close_array[i]):
            pass
        else:
            highc = high_array[i]
            lowc = low_array[i]
            atrc = atr[i]
            closec = close_array[i]

            if math.isnan(atrc):
                atrc = 0

            basic_upperband = (highc + lowc) / 2 + atr_multiplier * atrc
            basic_lowerband = (highc + lowc) / 2 - atr_multiplier * atrc

            if basic_upperband < previous_final_upperband or previous_close > previous_final_upperband:
                final_upperband = basic_upperband
            else:
                final_upperband = previous_final_upperband

            if basic_lowerband > previous_final_lowerband or previous_close < previous_final_lowerband:
                final_lowerband = basic_lowerband
            else:
                final_lowerband = previous_final_lowerband

            if previous_supertrend == previous_final_upperband and closec <= final_upperband:
                supertrendc = final_upperband
            else:
                if previous_supertrend == previous_final_upperband and closec >= final_upperband:
                    supertrendc = final_lowerband
                else:
                    if previous_supertrend == previous_final_lowerband and closec >= final_lowerband:
                        supertrendc = final_lowerband
                    elif previous_supertrend == previous_final_lowerband and closec <= final_lowerband:
                        supertrendc = final_upperband

            supertrend.append(supertrendc)

            previous_close = closec

            previous_final_upperband = final_upperband

            previous_final_lowerband = final_lowerband

            previous_supertrend = supertrendc

    return supertrend


def generateSuperTrend_new(interval, pair, atr_period, atr_multiplier):
    interval = interval

    pair = pair

    limit = 500

    klines = connection.client.get_klines(
        symbol=pair, interval=interval, limit=limit)

    high = [float(entry[2]) for entry in klines]
    low = [float(entry[3]) for entry in klines]
    close = [float(entry[4]) for entry in klines]

    close_array = np.asarray(close)
    high_array = np.asarray(high)
    low_array = np.asarray(low)

    supertrend = generateSupertrend(
        close_array, high_array, low_array, atr_period=atr_period, atr_multiplier=atr_multiplier)

    return supertrend


def generateStochasticRSI_new(connection, pair, interval, limit):
    klines = connection.client.get_klines(
        symbol=pair, interval=interval, limit=limit)

    high = [float(entry[2]) for entry in klines]
    low = [float(entry[3]) for entry in klines]
    close = [float(entry[4]) for entry in klines]

    close_array = np.asarray(close)

    stochasticRsiF, stochasticRsiS = generateStochasticRSI(close_array, 11)
    return stochasticRsiF, stochasticRsiS, close_array


def sendTelegramMsg(token, chat_id, msg):
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=msg, parse_mode="html")


if __name__ == '__main__':
    filename = 'credentials.txt'

    connection = BinanceConnection(filename)

    while 1:
        f = open("test.json",)
        liste_json = json.load(f)
        print(len(liste_json))
        for i in range(len(liste)):
            try:

                # coin listesini atama yapıyor
                pair = liste[i]

                # rsi, supertrend -> 30 dakikalık
                stochasticRsiF_30m, stochasticRsiS_30m, close_array_30m = generateStochasticRSI_new(
                    connection, pair, "30m", 66)
                supertrend_30m = generateSuperTrend_new('30m', pair, 10, 3)
                print("30dklık data getirildi")

                # rsi, supertrend -> 1 saatlik
                stochasticRsiF_1h, stochasticRsiS_1h, close_array_1h = generateStochasticRSI_new(
                    connection, pair, "1h", 66)
                supertrend_1h = generateSuperTrend_new('1h', pair, 10, 3)
                print("1 saatlik data getirildi")

                # rsi, supertrend -> 2 saatlik
                stochasticRsiF_2h, stochasticRsiS_2h, close_array_2h = generateStochasticRSI_new(
                    connection, pair, "2h", 66)
                supertrend_2h = generateSuperTrend_new('2h', pair, 10, 3)
                print("2 saatlik data getirildi")

                # rsi, supertrend -> 1 günlük
                supertrend_1d = generateSuperTrend_new("1d", pair, 10, 3)
                stochasticRsiF_1d, stochasticRsiS_1d, close_array_1d = generateStochasticRSI_new(
                    connection, pair, "1d", 66)
                print("3saatlik data getirildi")

                # rsi, supertrend -> 4 saatlik
                stochasticRsiF_4h, stochasticRsiS_4h, close_array_4h = generateStochasticRSI_new(
                    connection, pair, "4h", 66)
                supertrend_4h = generateSuperTrend_new('4h', pair, 10, 3)
                print("4 saatlik data getirildi")

                if (liste_json[i]['signalSend'] == False):
                    print(pair, close_array_1d[-1])
                    print(
                        "30: ", stochasticRsiF_30m[-1], stochasticRsiS_30m[-1])
                    print("1h: ", stochasticRsiF_1h[-1], stochasticRsiS_1h[-1])
                    print("2h: ", stochasticRsiF_2h[-1], stochasticRsiS_2h[-1])
                    print("3h: ", stochasticRsiF_1d[-1], stochasticRsiS_1d[-1])
                    print("4h: ", stochasticRsiF_4h[-1], stochasticRsiS_4h[-1])
                    # 1saatlik, 30 dakikalık, 2saatlik ve 4 saatlik grafiklerde supertrend var ise ilk aşama başarılı
                    if (close_array_1d[-1] > supertrend_1h[-1]) and (close_array_1d[-1] > supertrend_30m[-1]) and (close_array_1d[-1] > supertrend_2h[-1]) and (close_array_1d[-1] > supertrend_4h[-1]):

                        print("30 dakikalik, 1 saatlik, 2 saatlik, 4 saatlik grafiklerde Supertrend var - {} Fiyat: {} BUSD".format(
                            pair, close_array_1d[-1]))

                        # 15 dakikalık StochRSI değerlerinde Mavi kırmızı değerden küçükse veya eşitse ve mavi değer kırmızı değerden büyükse
                        # mavi veya kırmızı değerden biri 50 den küçük veya eşitse al
                        if (stochasticRsiF_1d[-2] <= stochasticRsiS_1d[-2]) and (stochasticRsiF_1d[-1] > stochasticRsiS_1d[-1]) and min(stochasticRsiF_1d[-1], stochasticRsiS_1d[-1]) <= 50:

                            print("Yeni - Super Trend Var - StochasticRSI var  - Value: ",
                                  pair, close_array_1d[-1], datetime.now().strftime("%H:%M:%S"))
                            msg = str(
                                "<pre> ## 3saatlik Alış Emri \n Super Trend: var \n StochasticRSI: var \n Birim: {} {}BUSD </pre>".format(pair, close_array_1d[-1]))
                            liste_json[i].update(
                                {"name": pair, "price": close_array_1d[-1], "supertrend": True, "stochrsi": True, "signalSend": True})
                            sendTelegramMsg('Telegram Bot Token', chat_id, msg)
                        else:
                            liste_json[i].update(
                                {"name": pair, "price": close_array_1d[-1], "supertrend": True, "stochrsi": False, "signalSend": False})
                    else:
                        print("SuperTrend yok")
                        liste_json[i].update({"name": pair, "price": close_array_1d[-1],
                                             "supertrend": False, "stochrsi": False, "signalSend": False})
                else:
                    print(pair)
                    print("F: ", stochasticRsiF_1d[-1])
                    print("S: ", stochasticRsiS_1d[-1])

                    # mavi kirmiziyi üstten keserse sat
                    if (stochasticRsiF_1d[-2] >= stochasticRsiS_1d[-2]) and (stochasticRsiF_1d[-2] >= stochasticRsiS_1d[-2]):
                        print("StochasticRSI 30 üstünde")

                        # json dosyasından koinin alınan fiyatı alınıp "bought_price" a atanıyor
                        bought_price = liste_json[i]['price']

                        # mavi, kırmızı çizgiyi yukarıdan kesitiği andaki fiyatı "sell_price" içine atanıyor
                        sell_price = close_array_1d[-1]

                        # kar oranı için yüzdelik hesaplar(burada aslında ayrı hesaplamalar yapmaya gerek yok ancak ileride gerekli olabilir)
                        # kar pozitif için yapılan hesap
                        if(sell_price > bought_price):
                            result = (sell_price-bought_price)*100/bought_price
                            msg = str(
                                "<pre>## Satış Emri \n Satış Fiyatı: {}BUSD \n Kar Oranı: +%{}</pre>".format(sell_price, result))
                            sendTelegramMsg('Telegram Bot Token', chat_id, msg)

                        elif(sell_price < bought_price):  # kar negatif için yapılan hesap
                            result = (sell_price-bought_price)*100/bought_price
                            msg = str(
                                "<code>## Satış Emri \n Satış Fiyatı: {}BUSD \n Kar Oranı: -%{}</code>".format(sell_price, result))
                            sendTelegramMsg('Telegram Bot Token', chat_id, msg)
                        else:
                            result = 0
                            msg = str(
                                "<code>## Satış Emri \n Satış Fiyatı: {}BUSD \n Kar Oranı: %{}</code>".format(sell_price, result))
                            sendTelegramMsg('Telegram Bot Token', chat_id, msg)

                        liste_json[i].update({"name": pair, "price": close_array_1d[-1],
                                             "supertrend": False, "stochrsi": False, "signalSend": False})

                print("-----------------------------------------------\n")
            except:
                continue

        json1 = json.dumps(liste_json, ensure_ascii=False)
        with open("test.json", "w", encoding="utf8") as f:
            f.write(json1)
