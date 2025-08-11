#!/bin/sh
set -e
PORT="${PORT:-8000}"
exec gunicorn 'src.web.app:create_app()' --bind 0.0.0.0:$PORT --workers 2
