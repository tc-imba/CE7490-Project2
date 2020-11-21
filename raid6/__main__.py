import uvicorn
import click

from raid6.config import get_settings


@click.command()
@click.option('-h', '--host', default='127.0.0.1', help='Host address')
@click.option('-p', '--base-port', default=10000, help='Port of the first server')
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode')
@click.option('-s', '--server-id', type=int, required=True, help='ID of the current server')
@click.option('-k', '--primary', default=6, help='Number of primary data strips')
@click.option('-m', '--parity', default=2, help='Number of parity data strips')
@click.option('-r', '--random', is_flag=True, help='Enable random distribution of data strips')
@click.option('--data-dir', default='/var/data/raid6', help='Location of data strips')
def main(**kwargs):
    settings = get_settings()
    for key, value in kwargs.items():
        if key in settings.__fields__:
            if value is not None:
                settings.__setattr__(key, value)
    settings.port = settings.server_id + settings.base_port
    with open('.settings.json', 'w') as f:
        f.write(settings.json())
    uvicorn.run(
        "raid6:app",
        host=settings.host, port=settings.port,
        debug=settings.debug, reload=settings.debug
    )


if __name__ == "__main__":
    main()
