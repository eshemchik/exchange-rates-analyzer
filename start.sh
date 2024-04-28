#!/bin/sh
gunicorn --bind 0.0.0.0:5000 applications.frontend.app:app
gunicorn --bind 0.0.0.0:5001 applications.backend.app:app