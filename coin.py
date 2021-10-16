from alpha_vantage.cryptocurrencies import CryptoCurrencies
import requests
import json
import datetime


def percentage_difference(price, value):
    """Calculate % between current price and prior prices"""
    return (price - value) * 100 / value if value != 0 else 0

def iso(_date):
    return _date.strftime("%Y-%m-%d")

class Coin:
    def __init__(self, currency, icon, name):
        self.currency = currency
        # Get key from https://www.alphavantage.co/documentation/
        self.cc = CryptoCurrencies(key='69420', output_format='json')

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        last_week = today - datetime.timedelta(days=7)
        last_month = today - datetime.timedelta(days=30)

        self.currentValue, self.crypto, self.data_array = self.get_data('USD')
        self.yesterday_value, self.last_week_value, self.last_month_value = self.get_percentage_change(self.currentValue, yesterday, last_week, last_month, 'USD')

        # WARNING: IF PUSHING THIS TO A REPO I NEED TO REDACT THIS TOKEN
        self.slack_token = 'aserequebola'
        self.slack_channel = '#crypto'
        self.slack_icon_emoji = icon
        self.slack_user_name = name

        if self.currency != 'BTC':
            self.currentValueBTC, self.crypto_btc, _ = self.get_data('BTC')
            self.yesterday_value_btc, self.last_week_value_btc, self.last_month_value_btc = self.get_percentage_change(self.currentValueBTC, yesterday, last_week, last_month, 'BTC')

    def get_data(self, uoa):
        data, _ = self.cc.get_digital_currency_exchange_rate(self.currency, uoa)
        current = float(data['5. Exchange Rate'])

        if uoa == 'USD':
            crypto = '{0:,.2f}'.format(current)
        else:
            crypto = '{0:.8f}'.format(current)

        data_array, _ = self.cc.get_digital_currency_daily(symbol=self.currency, market='USD')
        return current, crypto, data_array

    def get_percentage_change(self, current, yesterday, last_week, last_month, uoa):
        yesterdayValue = float(self.get_value_from_date(self.data_array, iso(yesterday)))
        lastweekValue = float(self.get_value_from_date(self.data_array, iso(last_week)))
        lastmonthValue = float(self.get_value_from_date(self.data_array, iso(last_month)))

        if uoa == 'BTC':
            # the api doesn't allow to get directly the array with the values using UoA = BTC
            # need to convert the values to be accounted in BTC 
            # in order to do this, I need to use the BTC values from those same dates

            btc_data_array, _ = self.cc.get_digital_currency_daily(symbol='BTC', market='USD')
            btcyesterdayValue = float(self.get_value_from_date(btc_data_array, iso(yesterday)))
            btclastweekValue = float(self.get_value_from_date(btc_data_array, iso(last_week)))
            btclastmonthValue = float(self.get_value_from_date(btc_data_array, iso(last_month)))

            yesterdayValue = yesterdayValue/btcyesterdayValue
            lastweekValue = lastweekValue/btclastweekValue
            lastmonthValue = lastmonthValue/btclastmonthValue

        yesterday_value = '{0:.2f}'.format(percentage_difference(current, yesterdayValue))
        last_week_value = '{0:.2f}'.format(percentage_difference(current, lastweekValue))
        last_month_value = '{0:.2f}'.format(percentage_difference(current, lastmonthValue))

        return yesterday_value, last_week_value, last_month_value

    def post_message_to_slack(self, text, blocks = None):
        """Post to a slack channel"""
        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.slack_token,
            'channel': self.slack_channel,
            'text': text,
            'icon_emoji': self.slack_icon_emoji,
            'username': self.slack_user_name,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()

    def get_value_from_date(self, data_array, _date):
        """Get data from a specific date in isoformat: YYYY-MM-DD"""
        return data_array[_date]['4a. close (USD)']

    def __str__(self):
        coin_string = list()

        if self.currency == 'BTC':
            uoa_usd = '$' + self.crypto + ' ~ 1฿ | 1D (' + self.yesterday_value + '%) | 7D (' + self.last_week_value + '%) | 30D (' + self.last_month_value + '%)'
            return uoa_usd

        uoa_usd = '$' + self.crypto + ' | 1D (' + self.yesterday_value + '%) | 7D (' + self.last_week_value + '%) | 30D (' + self.last_month_value + '%)'
        coin_string.append(uoa_usd)
        uoa_btc = self.crypto_btc + '฿ | 1D (' + self.yesterday_value_btc + '%) | 7D (' + self.last_week_value_btc + '%) | 30D (' + self.last_month_value_btc + '%)'
        coin_string.append(uoa_btc)
        return "\n".join(coin_string)

