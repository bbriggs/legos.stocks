from Legobot.Lego import Lego
import requests
import logging
import json

logger = logging.getLogger(__name__)


class Cryptocurrency(Lego):
    def listening_for(self, message):
        if message['text'] is not None:
            try:
                return message['text'].split()[0] == '!crypto'
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

        try:
            query = message['text'].split()[1]
        except:
            self.reply(message, "Invalid query", opts)

        self.reply(message, self.lookup_symbol(query), opts)

    def lookup_symbol(self, query):
        query = query.upper()
        request_url = 'https://min-api.cryptocompare.com/data/price'
        params = {}
        params['fsym'] = query  # fsym, the SYMbol to convert From
        if query == 'BTC':
            params['tsyms'] = 'USD'  # tsyms, the SYMbolS to convert To
        else:
            params['tsyms'] = 'USD,BTC'  # tsyms, the SYMbolS to convert To
        api_response = requests.get(request_url, params=params)
        if api_response.status_code == requests.codes.ok:
            return self._parse_api_response(api_response, query)
        else:
            logger.error('Requests encountered an error.')
            logger.error('''HTTP GET response code:
                        {}'''.format(api_response.status_code))
            return api_response.raise_for_status()

    def _parse_api_response(self, api_response, query):
        api_response = json.loads(api_response.text)
        return_val = query + ':  |  '
        for key, value in api_response.items():
            return_val += '{} {}  |  '.format(value, key)
        if query == 'DOGE':
            return_val = 'WOW! {}  TO THE MOON!!!'.format(return_val)
        return return_val

    def get_name(self):
        return 'crypto'

    def get_help(self):
        return '''Lookup a crypto symbol's value. Usage: !crypto <symbol>.
                List of symbols here
                https://min-api.cryptocompare.com/data/all/coinlist.'''
