import asyncio
from typing import Annotated
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero, elevenlabs


load_dotenv()
class AssistantFunction(agents.llm.FunctionContext):
    """This class is used to define functions that will be called by the assistant."""

    @agents.llm.ai_callable(
        description=(
            "Called when asked to evaluate something that would require vision capabilities"
        )
    )

    async def image(
        self,
        user_msg: Annotated[
            str,
            agents.llm.TypeInfo(
                description="The user message that triggered this function"
            ),
        ],
    ):
        print(f"[LOG] Message triggering vision capabilities: {user_msg}")

        return None


async def get_video_track(room: rtc.Room):
    """
    Sets up video track handling using LiveKit's subscription model.
    Returns a Future that will be resolved with the first available video track.
    """
    video_track = asyncio.Future[rtc.RemoteVideoTrack]()
    
    # First check existing tracks in case we missed the subscription event
    for participant in room.remote_participants.values():
        print(f"[LOG] Checking participant: {participant.identity}")
        for pub in participant.track_publications.values():
            if (pub.track and 
                pub.track.kind == rtc.TrackKind.KIND_VIDEO and 
                isinstance(pub.track, rtc.RemoteVideoTrack)):
                
                # Log track details
                print(f"[LOG] Found existing video track: {pub.track.sid}")

                
                video_track.set_result(pub.track)
                return await video_track

    # Set up listener for future video tracks
    @room.on("track_subscribed") 
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if (not video_track.done() and 
            track.kind == rtc.TrackKind.KIND_VIDEO and 
            isinstance(track, rtc.RemoteVideoTrack)):
            
            
            video_track.set_result(track)

    # Add timeout in case no video track arrives
    try:
        return await asyncio.wait_for(video_track, timeout=10.0)
    except asyncio.TimeoutError as e:
        sentry_sdk.capture_exception(e)
        print("[ERROR] Timeout waiting for video track")
        raise Exception("No video track received within timeout period")
        
async def _enableCamera(ctx):
    await ctx.room.local_participant.publish_data(
        "camera_enable", reliable=True, topic="camera"
    )

async def _getVideoFrame(ctx, assistant):
    await _enableCamera(ctx)
    latest_images_deque = []
    try:
        print("[LOG] Waiting for video track...")
        video_track = await get_video_track(ctx.room)
        print(f"[LOG] Got video track: {video_track.sid}")
        async for event in rtc.VideoStream(video_track):
            latest_image = event.frame
            latest_images_deque.append(latest_image)
            assistant.fnc_ctx.latest_image = latest_image

            if len(latest_images_deque) == 5:
                best_frame = await select_best_frame(latest_images_deque)
                return best_frame
    except Exception as e:  # Add Exception type
        print(f"[ERROR] Error in getVideoframe function: {e}")
        return None

        
async def select_best_frame(latest_images_deque):
    '''Please come up with a function that selects the best frame out of 5'''
    return latest_images_deque[-1]
    
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    print(f"Room name: {ctx.room.name}")

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

    gpt = openai.LLM(model="gpt-4o")

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




    assistant = VoiceAssistant(
        vad=silero.VAD.load(), 
        stt=deepgram.STT(), 
        llm=gpt,
        tts=elevenlabs_tts, 
        fnc_ctx=AssistantFunction(),
        chat_ctx=chat_context,
    )

    chat = rtc.ChatManager(ctx.room)

    async def _answer(text: str, use_image: bool = False):
        """
        Answer the user's message with the given text and optionally the latest
        image captured from the video track.
        """
        print(f"[LOG] _answer called with text: {text}, use_image: {use_image}")
        try:
            content: list[str | ChatImage] = [text]
            if use_image:
                print("[LOG] Getting video frame")
                latest_image = await _getVideoFrame(ctx, assistant)
                if latest_image is not None:
                    print("[LOG] Adding image to content")
                    content.append(ChatImage(image=latest_image))
                else:
                    print("[LOG] No image available")
    
            print("[LOG] Adding message to chat context")
            chat_context.messages.append(ChatMessage(role="user", content=content))
    
            print("[LOG] Getting GPT response")
            stream = gpt.chat(chat_ctx=chat_context)
            print("[LOG] Sending response to assistant")
            await assistant.say(stream, allow_interruptions=True)
        except Exception as e:
            print(f"[ERROR] Error in _answer: {e}")

    @chat.on("message_received")
    def on_message_received(msg: rtc.ChatMessage):
        """This event triggers whenever we get a new message from the user."""

        if msg.message:
            asyncio.create_task(_answer(msg.message, use_image=False))


    @assistant.on("function_calls_finished")
    def on_function_calls_finished(called_functions: list[agents.llm.CalledFunction]):
        """This event triggers when an assistant's function call completes."""
        print(f"[LOG] Function calls finished. Number of calls: {len(called_functions)}")
    
        if len(called_functions) == 0:
            print("[LOG] No functions were called")
            return
    
        try:
            user_msg = called_functions[0].call_info.arguments.get("user_msg")
            print(f"[LOG] Function call user message: {user_msg}")
            
            if user_msg:
                print("[LOG] Creating task for _answer with image")
                asyncio.create_task(_answer(user_msg, use_image=True))
            else:
                print("[LOG] No user message to process")
        except Exception as e:
            print(f"[ERROR] Error in function calls handler: {e}")
            
    assistant.start(ctx.room)

    await asyncio.sleep(1)
    #Start with a greeting
    await assistant.say("Hi there! How can I help?", allow_interruptions=True)



if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))