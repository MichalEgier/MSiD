import requests
import string
import json
import time

markets = ['bitbay.net','bittrex.com','bitstamp.net','cex.io']

currency_pairs = [("ETH","USD"),("LTC","BTC"),("ETH","EUR"),("ETH","BTC")]

def orderbook_url(market, currency_pair):
    source_currency = currency_pair[0]
    target_currency = currency_pair[1]
    if market == 'bitbay.net':
        return 'https://bitbay.net/API/Public/' + source_currency + target_currency + '/orderbook.json'
    if market == 'bittrex.com':
        return 'https://api.bittrex.com/api/v1.1/public/getorderbook?market=' + source_currency + '-' + target_currency + "&type=both"
    if market == 'bitstamp.net':
        return 'https://www.bitstamp.net/api/v2/order_book/' + source_currency.lower() + target_currency.lower() + '/'
    if market == 'cex.io':
        return 'https://cex.io/api/order_book/' + source_currency + "/" + target_currency
    return ""

#L5

def last_transaction(market, currency_pair):
    if currency_pair[0] == currency_pair[1]:
        print("Same: " + currency_pair[0] + " " + currency_pair[1])
        return 1.0              #Jezeli chcemy konwersji np z BTC do BTC to nie liczymy tylko dajemy ze 1.0 mnoznik
    url = ticker_url(market,currency_pair)
    req = requests.get(url)
    if str(req) != "<Response [200]>":
#        print(str(req))
        return None         #Jezeli nie mozna polaczyc sie z danym url to zwroc None
    jsonText = req.json()
    repairedJson = str(jsonText).replace("\'", "\"")
    if "message" in repairedJson:
        return -1.0		#Jezeli w wiadomosci jest fragment "message" to znaczy ze cos poszlo nie tak, nigdy go nie ma 
    print(repairedJson)									#jak jest wszystko dobrze
    #		print(repairedJson)
    dict = json.loads(repairedJson)
    #print(float(dict['last']))
    if 'last' in dict.keys():
        return float(dict['last'])
    return -1.0              #Jezeli wystapil inny blad (np. dostaniemy poprawna odpowiedz od API, ze nie ma takiej
                                        # pary walut w systemie, to zwracamy -1.0

                #Waluty musza byc zapisane w pliku wielkimi literami
def get_json_from_file(filename):
    with open(filename) as f:
        return json.load(f)

#Funkcja z pierwszej czesci - bez sprawdzania dalszych marketow    
                     #Funkcja odczytuje dane z pliku JSON o podanej ścieżce w argumencie wywołania funkcji
def old_summarize_wallet(market, filename):         #Zwraca pare (Waluta, Wartosc), ktora mowi jaka jest waluta w ktorej podajew
    sum = 0.0                                       #I ile posiadamy w tej walucie pieniedzy
    jsonText = get_json_from_file(filename)
    repairedJson = str(jsonText).replace("\'", "\"")
    dict = json.loads(repairedJson)
    if "base_currency" not in dict.keys():
        print("Error - no base currency specified in JSON file!")
        return None
    base_curr = dict['base_currency']
    #print(str(dict))
    dict.pop("base_currency")
    #print(str(dict))
                        #Dla kazdej waluty w jakiej mamy srodki (key = waluta)
    for key in dict.keys():
        print("Key: " + key)
        pair = (key, base_curr)
        print("Pair: " + str(pair))
        last_trans = last_transaction(market, pair)
        if last_trans == None:
            print("Error - can't connect to API or no pair " + str(pair) + " in market " + market)
        elif last_trans == -1.0:
            print("No pair " + str(pair) + " in market " + market)
        else:
            sum = sum + float(dict[key]) * last_trans
    return (base_curr, sum)


#Task 2

def sort_tuples_list_by_first_elem(tup_l):  
    tup_l.sort(key = lambda x: x[0])  
    return tup_l  

		#Zwraca liste par (kurs, ilosc) posortowane wedlug kursu
def get_buy_offers_sorted(market, currency_pair):
    url = orderbook_url(market,currency_pair)
    req = requests.get(url)
    if str(req) != "<Response [200]>":
#        print(str(req))
        return None         #Jezeli nie mozna polaczyc sie z danym url to zwroc None
    jsonText = req.json()
    repairedJson = str(jsonText).replace("\'", "\"")
    if "message" in repairedJson:
        return None		#Jezeli w wiadomosci jest fragment "message" to znaczy ze cos poszlo nie tak, nigdy go nie ma 
    print(repairedJson)									#jak jest wszystko dobrze
    dict = json.loads(repairedJson)
    l1 = dict['asks']
    return sort_tuples_list_by_first_elem(l1) 

                        #Funkcja odczytuje dane z pliku JSON o podanej ścieżce w argumencie wywołania funkcji
def summarize_wallet(filename):         #Zwraca pare (Waluta, Wartosc), ktora mowi jaka jest waluta w ktorej podajew
    sum = 0.0                                       #I ile posiadamy w tej walucie pieniedzy
    jsonText = get_json_from_file(filename)
    repairedJson = str(jsonText).replace("\'", "\"")
    dict = json.loads(repairedJson)
    if "base_currency" not in dict.keys():
        print("Error - no base currency specified in JSON file!")
        return None
    base_curr = dict['base_currency']
    #print(str(dict))
    dict.pop("base_currency")
    #print(str(dict))
    market = markets[0]
    found = True
    i = 0	#Licznik, ktory market teraz sprawdzamy - wazny, jezeli jakiejs waluty w jednym nie ma zawartej
                        #Dla kazdej waluty w jakiej mamy srodki (key = waluta)
    for key in dict.keys():
        curr_left = dict[key]
        pair = (key, base_curr)
        offers_list = get_buy_offers_sorted(markets[i],pair)
        if offers_list == None						#	========
            i=i+1
	    while i<len(markets) and offers_list == None:		#	W tych liniach zaimplementowane jest szukanie
                offers_list = get_buy_offers_sorted(markets[i],pair)	#	par walut w kolejnych marketach, jesli brakuje ich 
	    if offers_list == None:					#	w poprzednich	
                return None						#	========
	while curr_left > 0:						#	========
	    if offers_list[0][1] > curr_left:
                sum = sum + curr_left * offers_list[0][0]
                curr_left = 0						#	W tych liniach zaimplementowane jest zamienianie walut
            else:							#	z kolejnych najlepszych ofert
                sum = sum + offers_list[0][1] * offers_list[0][0]	#	uwzgledniajac wolumen w ofercie
                curr_left = curr_left - offers_list[0][1]
                offers_list.pop[0]					#	========

    return (base_curr, sum)


#Dodatkowy feature - sprawdzanie ile mielibysmy w portfelu, jezeli wszystko kupowalibysmy po najlepszych dla nas ofertach
#										zarejestrowanych w ciagu ostatnich 24h
def last_day_best_buy_offer(market, currency_pair):
    if currency_pair[0] == currency_pair[1]:
        print("Same: " + currency_pair[0] + " " + currency_pair[1])
        return 1.0              #Jezeli chcemy konwersji np z BTC do BTC to nie liczymy tylko dajemy ze 1.0 mnoznik
    url = ticker_url(market,currency_pair)
    req = requests.get(url)
    if str(req) != "<Response [200]>":
#        print(str(req))
        return None         #Jezeli nie mozna polaczyc sie z danym url to zwroc None
    jsonText = req.json()
    repairedJson = str(jsonText).replace("\'", "\"")
    if "message" in repairedJson:
        return -1.0		#Jezeli w wiadomosci jest fragment "message" to znaczy ze cos poszlo nie tak, nigdy go nie ma 
    print(repairedJson)									#jak jest wszystko dobrze
    #		print(repairedJson)
    dict = json.loads(repairedJson)
    #print(float(dict['last']))
    if 'last' in dict.keys():
        return float(dict['last'])
    return -1.0              #Jezeli wystapil inny blad (np. dostaniemy poprawna odpowiedz od API, ze nie ma takiej


def main():
    pair = summarize_wallet("input.json")
    dict = {"base_currency":pair[0],"ammount":pair[1]}
    print(str(dict))
    with open("output.json",'w') as f:
        json.dump(dict,f)


main()

#sample = {"BTC" : "0.123", "LTC" : "1.345"}

#with open('result.json', 'w') as fp:
#    json.dump(sample, fp)

#print(get_json_from_file("result.json"))

#Pobrac liste walut w jakich mamy z pliku w formacie JSON
#Na samym poczatku jest pod kluczem base_currency waluta do ktorej chcemy przeliczac
#Sprawdzic tylko w jednym wybranym markecie wszystkie waluty
#Wszystko na biezaco przeliczac do wybranej wczesniej waluty
#Jezeli nie bedzie takiej pary walut w markecie to wyswietlamy wiadomosc odpowiednia (req != 200 OR "last" not in dict.keys)
#
