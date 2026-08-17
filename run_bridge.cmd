@echo off
rem Leiko render bridge - hourly scheduled task wrapper. No secret in this file:
rem CONTENT_INGEST_SECRET is a persistent USER environment variable.
cd /d "%~dp0"
echo ---- %date% %time% ---- >> bridge_log.txt
python render_bridge.py >> bridge_log.txt 2>&1
