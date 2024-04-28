#!/bin/sh
gunicorn applications.frontend.app:app
gunicorn applications.backend.app:app