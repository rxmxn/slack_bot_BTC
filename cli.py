import click
import coin


@click.command()
@click.argument('currency')
@click.argument('icon')
@click.argument('name')
def run(currency, icon, name):
    c = coin.Coin(currency, icon, name)
    c.post_message_to_slack(str(c))

@click.command()
@click.argument('currency')
@click.argument('icon')
@click.argument('name')
def just_print(currency, icon, name):
    c = coin.Coin(currency, icon, name)
    print(c)

if __name__ == '__main__':
    run()
