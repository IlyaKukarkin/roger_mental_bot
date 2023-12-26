import os

from amplitude import Amplitude
from amplitude import BaseEvent

amplitude_api_key = os.getenv("AMPLITUDE_API_KEY")
amplitude = Amplitude(amplitude_api_key)


async def amplitude_send_start_source_event(user_id: str, source: str, extra: str):
    amplitude.track(
            BaseEvent(
                event_type="Start Event",
                user_id=str(user_id),
                event_properties={
                    "user": {"_id": user_id},
                    "source": source,
                    "extra": extra
                }
            )
        )
    