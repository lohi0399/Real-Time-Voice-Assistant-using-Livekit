from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import JobContext
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero, elevenlabs
from assistant import AssistantFunction

load_dotenv() # Loading environement variables

class Initialization:

    def __init__(self, ctx: JobContext):
        self.ctx = ctx
    
    def setting_chat_context(self) -> ChatContext:

        chat_context = ChatContext(
        messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "Your name is Ally. You are an assistant for the blind and visually impaired. Your interface with users will be voice and vision."
                        "Respond with short and concise answers. Avoid using unpronouncable punctuation or emojis."
                    ),
                )
            ]
        )

        return chat_context

    def setting_gpt(self) -> openai.LLM:
        gpt = openai.LLM(model="gpt-4o")
        return gpt

    def setting_tts(self) -> elevenlabs.TTS:

            custom_voice = elevenlabs.Voice(
                id='21m00Tcm4TlvDq8ikWAM', 
                name='Bella',
                category='premade',
                settings=elevenlabs.VoiceSettings(
                    stability=0.71,
                    similarity_boost=0.5,
                    style=0.0,
                    use_speaker_boost=True
                )
                )
            elevenlabs_tts = elevenlabs.TTS(voice=custom_voice)

            return elevenlabs_tts

    def setting_chat_manager(self) -> rtc.ChatManager:
         chat = rtc.ChatManager(self.ctx.room)
         return chat

    def setting_voice_assistant(self) -> VoiceAssistant:
         
        assistant = VoiceAssistant(
            vad=silero.VAD.load(), 
            stt=deepgram.STT(), 
            llm=self.setting_gpt(),
            tts=self.setting_tts(), 
            fnc_ctx=AssistantFunction(),
            chat_ctx= self.setting_chat_context(),
        )
        return assistant
    
    