import os
import logging

from git_criollo.ui import GitCriolloApp


def main() -> None:
    os.makedirs(os.path.expanduser("~/.gitcriollo"), exist_ok=True)
    logging.basicConfig(
        filename=os.path.expanduser("~/.gitcriollo/debug.log"),
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    GitCriolloApp().run()


if __name__ == "__main__":
    main()
