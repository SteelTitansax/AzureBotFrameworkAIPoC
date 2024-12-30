# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from django.http import JsonResponse
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

from openai import AzureOpenAI
from django.utils.html import escape
import os
from config import settings
import time

# Azure AI Foundry Configuration

endpoint = os.getenv("ENDPOINT_URL", settings.ai_settings.endpoint)
deployment = os.getenv("DEPLOYMENT_NAME", settings.ai_settings.deployment)
search_endpoint = os.getenv("SEARCH_ENDPOINT", settings.ai_settings.search_endpoint)
search_key = os.getenv("SEARCH_KEY", settings.ai_settings.search_key)
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", settings.ai_settings.subscription_key)

print(deployment)
# Azure OpenAI Client initialization

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# Initialize conversation history
conversation_history = []


def ask_openai(conversation_history):
        # Prepare chat prompt with conversation history
        chat_prompt = conversation_history

        # Answer generation
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            extra_body={
                "data_sources": [{
                    "type": "azure_search",
                    "parameters": {
                        "filter": None,
                        "endpoint": f"{search_endpoint}",
                        "index_name": "mgf-index-poc-2",
                        "semantic_configuration": "azureml-default",
                        "authentication": {
                            "type": "system_assigned_managed_identity"
                        },
                        "query_type": "simple",
                        "in_scope": True,
                        "role_information": "",
                        "strictness": 1,
                        "top_n_documents": 20
                    }
                }]
            }
        )

        answer = completion.choices[0].message.content.strip()
        return answer

class MyBot(ActivityHandler):

    

    async def on_message_activity(self, turn_context: TurnContext):
        global conversation_history
        message = turn_context.activity.text
        returnedResponse= ""
        language = False
        counter = 0
        retry_answer = 'The requested information is not available in the retrieved data'
        if language == False : 
                context_prompt = """
                                    Put Your Propmt Here                                    
					   """
                                 
                escaped_message = escape("Response language : " + message + context_prompt)
                conversation_history.append({"role": "user", "content": escaped_message})
                
                response = ask_openai(conversation_history)
                # Append AI response to conversation history
                conversation_history.append({"role": "assistant", "content": response})
                language = True
                returnedResponse = response


        else:
            while counter < 3:
                escaped_message = escape(message)

                # Append user message to conversation history
                conversation_history.append({"role": "user", "content": escaped_message})
                
                response = ask_openai(conversation_history)

                # Append AI response to conversation history
                conversation_history.append({"role": "assistant", "content": response})
                
                if retry_answer in response: 
                    if counter == 2: 
                        returnedResponse = response
                    counter = counter + 1
                else:
                    returnedResponse = response

        await turn_context.send_activity(returnedResponse)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hi, I am the PoC Chatbot, In which language you require support?.")
