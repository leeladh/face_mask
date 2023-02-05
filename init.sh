#!/bin/bash
uvicorn main_launch:app --reload --port $1 --host 0.0.0.0