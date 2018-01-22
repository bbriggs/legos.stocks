from Legobot.Lego import Lego
import requests
import logging
import json
import configparser

logger = logging.getLogger(__name__)


class Hodl(Lego):
    def __init__(self, baseplate, lock):
        super().__init__(baseplate, lock)
        self.hodl = configparser.ConfigParser()
        self.hodl.read('hodl.ini')
        if 'hodl' not in self.hodl.sections():
            self.hodl['hodl'] = {}
            self.hodl['hodl']['convert_from'] = 'BTC'
            self.hodl['hodl']['convert_to'] = 'USD,BTC'
            with open('hodl.ini', 'w') as configfile:
                self.hodl.write(configfile)

    def listening_for(self, message):
        if message['text'] is not None:
            try:
                command = message['text'].split()[0]
                return command == '!hodl'
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

        message_list = message['text'].split()
        try:
            self.reply(message, self._parse_multi_commands(message_list), opts)
        except Exception as e:
            self.reply(message, 'An Error Ocurred: ' + e, opts)

    def _parse_multi_commands(self, message_list):
        if len(message_list) == 1:
            return self._lookup_multi()
        elif len(message_list) > 1:
            case_dict = {}
            case_dict['list'] = self._list_hodl_symbols
            case_dict['add'] = self._add_symbols
            case_dict['drop'] = self._drop_symbols
            try:
                return case_dict[message_list[1]](message_list)
            except Exception as e:
                return 'Argument error: ' + e

    def _list_hodl_symbols(self, message_list):
        convert_from = self.hodl['hodl']['convert_from']
        convert_to = self.hodl['hodl']['convert_to']
        return_val = ''
        return_val += 'Convert From:  ' + convert_from + '\n'
        return_val += 'Convert To:  ' + convert_to + '\n'
        return return_val

    def _add_symbols(self, message_list):
        if len(message_list) < 3:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl add from BTC,LTC')
        elif message_list[2] == 'from':
            return self._add_from_symbols(message_list)
        elif message_list[2] == 'to':
            return self._add_to_symbols(message_list)
        else:
            return 'There was an issue processing your request.'

    def _add_from_symbols(self, message_list):
        try:
            add_convert_from = message_list[3].split(',')
            old_convert_from = self.hodl['hodl']['convert_from'].split(',')
            new_convert_from = list(set(old_convert_from + add_convert_from))
            self.hodl['hodl']['convert_from'] = ','.join(new_convert_from)
            with open('hodl.ini', 'w') as configfile:
                self.hodl.write(configfile)
            return self._list_hodl_symbols(message_list)
        except:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl add from BTC,LTC')

    def _add_to_symbols(self, message_list):
        try:
            add_convert_to = message_list[3].split(',')
            old_convert_to = self.hodl['hodl']['convert_to'].split(',')
            new_convert_to = list(set(old_convert_to + add_convert_to))
            self.hodl['hodl']['convert_to'] = ','.join(new_convert_to)
            with open('hodl.ini', 'w') as configfile:
                self.hodl.write(configfile)
            return self._list_hodl_symbols(message_list)
        except:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl add to BTC,LTC')

    def _drop_symbols(self, message_list):
        if len(message_list) < 3:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl drop from BTC')
        elif message_list[2] == 'from':
            return self._drop_from_symbols(message_list)
        elif message_list[2] == 'to':
            return self._drop_to_symbols(message_list)
        else:
            return 'There was an issue processing your request.'

    def _drop_from_symbols(self, message_list):
        try:
            drop_convert_from = message_list[3].split(',')
            old_convert_from = self.hodl['hodl']['convert_from'].split(',')
            new_convert_from = set(old_convert_from).symmetric_difference(
                               set(drop_convert_from))
            self.hodl['hodl']['convert_from'] = ','.join(new_convert_from)
            with open('hodl.ini', 'w') as configfile:
                self.hodl.write(configfile)
            return self._list_hodl_symbols(message_list)
        except:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl drop from BTC,LTC')

    def _drop_to_symbols(self, message_list):
        try:
            drop_convert_to = message_list[3].split(',')
            old_convert_to = self.hodl['hodl']['convert_to'].split(',')
            new_convert_to = set(old_convert_to).symmetric_difference(
                             set(drop_convert_to))
            self.hodl['hodl']['convert_to'] = ','.join(new_convert_to)
            with open('hodl.ini', 'w') as configfile:
                self.hodl.write(configfile)
            return self._list_hodl_symbols(message_list)
        except:
            return ('Please supply additional arguments, e.g.:\n'
                    '!hodl drop to BTC,LTC')

    def _lookup_multi(self):
        multi_url = self._build_index_url()
        get_multi = requests.get(multi_url)
        if get_multi.status_code == requests.codes.ok:
            api_response = json.loads(get_multi.text)
            return self._parse_multi_price_response(api_response)
        else:
            return 'There was an error getting the data: ' + get_multi.text

    def _parse_multi_price_response(self, api_response):
        return_val = ''
        for key, value in api_response.items():
            return_val += key + ':  |  '
            for key, value in value.items():
                return_val += '{} {}  |  '.format(value, key)
            return_val += '\n'
        return return_val

    def _build_index_url(self):
        baseurl = 'https://min-api.cryptocompare.com/data/pricemulti'
        convert_from = self.hodl['hodl']['convert_from']
        convert_to = self.hodl['hodl']['convert_to']
        return baseurl + '?fsyms=' + convert_from + '&tsyms=' + convert_to

    def get_name(self):
        return 'hodl'

    def get_help(self):
        return ('Lookup multiple crypto symbol\'s values from saved list.\n'
                'List of symbols here: '
                'https://min-api.cryptocompare.com/data/all/coinlist.\n'
                'Usage:\n'
                '!hodl -- returns prices for multiple coins at once.\n'
                '!hodl list -- returns the list of coins to convert from/to.\n'
                '!hodl <add/drop> <to/from> <comma separated symbols list>'
                ' -- adds or drop list of symbols to the convert to or convert'
                ' from list.')
