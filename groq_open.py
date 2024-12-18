from dotenv import load_dotenv
from groq import Groq
import base64
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from typing import Any
from openai.types.chat import ChatCompletionMessageParam
from livekit import rtc
from livekit.agents import llm, utils

load_dotenv()

def _build_oai_image_content(image: ChatImage, cache_key: Any):

    if isinstance(image.image, str):  # image url
        return {
            "type": "image_url",
            "image_url": {"url": image.image, "detail": "auto"},
        }
    elif isinstance(image.image, rtc.VideoFrame):  # VideoFrame

        if cache_key not in image._cache:
            # inside our internal implementation, we allow to put extra metadata to
            # each ChatImage (avoid to reencode each time we do a chatcompletion request)
            opts = utils.images.EncodeOptions()
            if image.inference_width and image.inference_height:
                opts.resize_options = utils.images.ResizeOptions(
                    width=image.inference_width,
                    height=image.inference_height,
                    strategy="center_aspect_fit",
                )

            encoded_data = utils.images.encode(image.image, opts)
            base64_image = base64.b64encode(encoded_data).decode("utf-8")

        return base64_image
  
    raise ValueError(f"unknown image type {type(image.image)}")

class Groq_Open_LLM:
    def __init__(self,client: Groq, model:str="llama-3.2-11b-vision-preview"):
        self.client = client
        self.model = model

    def chat(self,image: ChatImage,prompt: str) -> str:

        base64_image = _build_oai_image_content(image, id(self))
        # Call the Groq API
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            
            model=self.model,
        )
        # print(chat_completion.choices[0].message.content)
        # Extract and return the response
        return chat_completion.choices[0].message.content