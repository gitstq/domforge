"""允许以 `python -m domforge` 方式运行。"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
