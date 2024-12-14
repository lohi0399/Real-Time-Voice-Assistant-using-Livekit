import asyncio
from livekit import rtc
import sentry_sdk


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
