#!/bin/sh

echo "(…) Running ENTRY RUN"

if [ "$DATABASE" = "postgres" ]
then

  echo "(…) Waiting for PostgreSQL..."

  while ! nc -z $SQL_HOST $SQL_PORT; do
    sleep 0.1
  done

  echo "✔ PostgreSQL started!"
fi

echo "✔ Show migrations..."
python manage.py showmigrations

echo "✔ MIGRATE..."
python manage.py migrate --noinput

echo "✔ COLLECTSTATIC..."
python manage.py collectstatic --noinput


exec "$@"