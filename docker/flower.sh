#!/bin/bash

celery --app=app.tasks.celery:celery flower