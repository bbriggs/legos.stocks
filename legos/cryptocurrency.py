from Legobot.Lego import Lego
import requests
import logging
import json
import configparser

logger = logging.getLogger(__name__)


class Cryptocurrency(Lego):
    def __init__(self, baseplate, lock):
        super().__init__(baseplate, lock)
        self.crypto_index = configparser.ConfigParser()
        self.crypto_index.read('crypto_index.ini')
        if 'crypto_index' not in self.crypto_index.sections():
            self.crypto_index['crypto_index'] = {}
            self.crypto_index['crypto_index']['fsyms'] = 'BTC'
            self.crypto_index['crypto_index']['tsyms'] = 'USD,BTC'
            with open('crypto_index.ini', 'w') as configfile:
                self.crypto_index.write(configfile)

    def listening_for(self, message):
        if message['text'] is not None:
            try:
                return message['text'].split()[0] == '!crypto' or message['text'].split()[0] == '!hodl'
            except Exception as e:
                logger.error('''Stocks lego failed to check message text:
                            {}'''.format(e))
                return False

    def handle(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            logger.error('''Could not identify message source in message:
                        {}'''.format(message))

        if message['text'].split()[0] == '!hodl':
            self.reply(message, 'HODL!', opts)
        else:
            try:
                query = message['text'].split()[1]
            except:
                self.reply(message, "Invalid query", opts)
            self.reply(message, self._lookup_symbol(query), opts)

    def _lookup_symbol(self, query):
        query = query.upper()
        request_url = 'https://min-api.cryptocompare.com/data/price'
        params = {}
        params['fsym'] = query  # fsym, the SYMbol to convert From
        if query == 'BTC':
            params['tsyms'] = 'USD'  # tsyms, the SYMbolS to convert To
        else:
            params['tsyms'] = 'USD,BTC'  # tsyms, the SYMbolS to convert To
        request_url = self._build_index_url()
        api_response = requests.get(request_url, params=params)
        if api_response.status_code == requests.codes.ok:
            if 'There is no data for the symbol' in api_response['Message']:
                matched_items = self._search_symbol(query)
                params['fsym'] = matched_items[0]['symbol']
                api_response = requests.get(request_url, params=params)
                if api_response.status_code == requests.codes.ok:
                    api_response = json.loads(api_response.text)
                    query = matched_items[0]['symbol']
                    meta = 'Did you mean {}?'.format(matched_items[0]['name'])
                    return self._parse_api_response(
                           api_response, query, meta=meta)
                else:
                    return 'We had trouble getting that ticker price.'
            else:
                return self._parse_api_response(api_response, query)
        else:
            logger.error('Requests encountered an error.')
            logger.error('''HTTP GET response code:
                        {}'''.format(api_response.status_code))
            return api_response.raise_for_status()

    def _search_symbol(self, query):
        request_url = 'https://min-api.cryptocompare.com/data/all/coinlist'
        get_list = requests.get(request_url)
        if get_list.status_code == requests.codes.ok:
            api_list = json.loads(get_list.text)
            matched_items = []
            for coin in api_list['Data']:
                full_name = api_list['Data'][coin]['FullName']
                if query in full_name.lower():
                    matched_items.append({"symbol": coin, "name": full_name})

            return matched_items
        else:
            logger.error('Error attempting to get list: ' + api_list.text)
            return 'There was an error fetching the list'

    def _parse_api_response(self, api_response, query, **kwargs):
        if 'meta' in kwargs:
            return_val = kwargs['meta'] + '\n'
        return_val = return_val + query + ':  |  '
        for key, value in api_response.items():
            return_val += '{} {}  |  '.format(value, key)
        if query == 'DOGE':
            return_val = 'WOW! {}  TO THE MOON!!!'.format(return_val)
        return return_val

    def _build_index_url(self):
        baseurl = 'https://min-api.cryptocompare.com/data/pricemulti'
        fsyms = self.crypto_index['crypto_index']['fsyms']
        tsyms = self.crypto_index['crypto_index']['tsyms']
        return baseurl + '?fsyms=' + fsyms + '&tsyms=' + tsyms

    def get_name(self):
        return 'crypto'

    def get_help(self):
        return '''Lookup a crypto symbol's value. Usage: !crypto <symbol>.
                List of symbols here
                https://min-api.cryptocompare.com/data/all/coinlist.'''
