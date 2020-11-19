import uvicorn
import click

from raid6.config import get_settings


@click.command()
@click.option('-h', '--host', default='127.0.0.1')
@click.option('-p', '--base-port', default=10000)
@click.option('-d', '--debug', is_flag=True)
@click.option('-s', '--server-id', type=int, required=True)
@click.option('-k', '--primary', default=6)
@click.option('-m', '--replica', default=2)
@click.option('--data-dir', default='/var/data/raid6')
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
