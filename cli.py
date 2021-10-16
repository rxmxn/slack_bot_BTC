import click
import coin

@click.group()
def cli():
    pass

@cli.command()
@click.argument('currency')
@click.argument('icon')
@click.argument('name')
def run(currency, icon, name):
    c = coin.Coin(currency, icon, name)
    c.post_message_to_slack(str(c))

@cli.command('print')
@click.argument('currency')
@click.argument('icon')
@click.argument('name')
def just_print(currency, icon, name):
    c = coin.Coin(currency, icon, name)
    print(c)

if __name__ == '__main__':
    cli()
