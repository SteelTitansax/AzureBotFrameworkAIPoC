#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8', 
                                      env_prefix="ai_", 
                                      extra='ignore')

    endpoint: str
    deployment: str
    search_endpoint: str
    search_key: str
    subscription_key: str



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', 
                                      env_file_encoding='utf-8', 
                                      extra='ignore')

    ai_settings: AISettings = AISettings()
    
settings = Settings()

