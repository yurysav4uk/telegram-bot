import hashlib
import requests
import speech_recognition as sr
import logging
import soundfile as sf
import os
import asyncio

from convert_data import convert_to_pcm16, convert_to_ogg,convert_to_wav
from telebot import TeleBot, logger, types
from spellchecker import SpellChecker
from download_data import *