import requests
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMService:
    def __init__(self, model="gemini-1.5-flash-8b-latest", host="https://generativelanguage.googleapis.com/v1beta"):
        self.model = model
        self.host = host
        self.api_key = "AIzaSyDwS6IpFVixsKmLxAIZHf972ZvQsZHVnDQ"
        logging.debug(f"Initialized LLMService with model: {self.model}, host: {self.host}")

    def generate_response(self, prompt):
        """Generate a response using the Gemini API."""
        try:
            logging.debug(f"Generating response for prompt: {prompt[:50]}...")
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"You are a helpful teaching assistant. {prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }

            # Handle proxies
            proxies = {
                "http": os.getenv("HTTP_PROXY"),
                "https": os.getenv("HTTPS_PROXY")
            }
            logging.debug(f"Using proxies: {proxies}")

            # Log request details
            url = f"{self.host}/models/{self.model}:generateContent?key={self.api_key}"
            logging.debug(f"Sending POST request to: {url}")

            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                proxies=proxies if proxies["http"] or proxies["https"] else None,
                verify=True
            )

            logging.debug(f"Received response with status code: {response.status_code}")
            response.raise_for_status()

            result = response.json()
            logging.debug(f"Response JSON: {json.dumps(result, indent=2)[:200]}...")

            if "candidates" not in result or not result["candidates"]:
                raise ValueError("Unexpected response format from Gemini API")

            return result["candidates"][0]["content"]["parts"][0]["text"].strip()

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            raise Exception(f"Error communicating with Gemini API: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding Gemini API response: {str(e)}")
            raise Exception(f"Error decoding Gemini API response: {str(e)}")
        except ValueError as e:
            logging.error(f"Error in response format: {str(e)}")
            raise Exception(f"Error in response format: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")