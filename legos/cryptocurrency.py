from Legobot.Lego import Lego
import requests
import logging
import json

logger = logging.getLogger(__name__)


class Crypto(Lego):
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
        request_url = 'https://api.cryptonator.com/api/ticker/{}-USD'.format(
                      query)
        api_response = requests.get(request_url)
        if api_response.status_code == requests.codes.ok:
            return_val = self._parse_for_ticker(api_response, query)
        else:
            logger.error('Requests encountered an error.')
            logger.error('''HTTP GET response code:
                        {}'''.format(api_response.status_code))
            api_response.raise_for_status()
        return return_val

    def _parse_for_ticker(self, api_response, query):
        api_response = json.loads(api_response.text)
        return_val = '${}'.format(api_response['ticker']['price'])
        if query == 'DOGE':
            return_val = 'WOW! {}  TO THE MOON!!!'.format(return_val)
        return return_val

    def get_name(self):
        return 'crypto'

    def get_help(self):
        return '''Lookup a crypto symbol's value. Usage: !crypto <symbol>.
                List of symbols here
                https://api.cryptonator.com/api/currencies.'''
