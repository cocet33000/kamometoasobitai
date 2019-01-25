#!/bin/sh

git add .
git commit -m 'none'
git push heroku master --force
