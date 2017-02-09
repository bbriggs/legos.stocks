import requests
import logging
import json
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)


class Stocks(Lego):
    def listening_for(self, message):
        if message['test'] is not None:
            try:
                return message['text'].split()[0] == '!stocks'
            except Exception as e:
                logger.error('Stocks lego failed to check message text: %s' % e)
                return False

    def handle(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            logger.error('Could not identify message source in message: %s'
                         % str(message))

        try:
            query = message['text'].split()[1]
        except:
            self.reply(message, "Invalid query", opts)

        self.reply(message, self.lookup_symbol(query), opts)

    def get_name(self):
        return 'stocks'

    def get_help(self):
        return "Lookup a stock symbol's value. Usage: !stocks <symbol>"

    def lookup_symbol(self, symbol):
        base_url = 'https://www.google.com/finance/info?q='
        url = base_url + symbol
        r = requests.get(url)
        logger.debug(r.status_code)
        if r.status_code == requests.codes.ok:
            r = r.text
            # take the leading // off the string
            r = r[4:]
            r = json.loads(r)
            r = r[0]
            ticker = r['t']
            exchange = r['e']
            value = r['l']
            return '%s trading on %s at %s' % (ticker, exchange, value)
        else:
            return "Could not find that ticker"
