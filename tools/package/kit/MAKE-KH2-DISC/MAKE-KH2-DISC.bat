@echo off
title Make the Kingdom Hearts II two-player TEST disc
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Make-KH2-Disc.ps1" -Original "%~1"
