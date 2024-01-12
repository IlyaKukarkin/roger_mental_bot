"""Module providing functions for Amplitude"""

import os

from amplitude import Amplitude
from amplitude import BaseEvent

amplitude_api_key = os.getenv("AMPLITUDE_API_KEY")
amplitude = Amplitude(amplitude_api_key)


async def amplitude_send_default_source_event(event_type: str,
                                              user_id: str,
                                              message: str,
                                              extra: str):
    """Function to send events to Amplitude"""

    amplitude.track(
         BaseEvent(
             event_type=event_type,
             user_id=user_id,
             event_properties={
                 "message": message,
                 "extra": extra
             }
         )
     )



async def amplitude_send_start_source_event(user_id: str, source: str, extra: str):
    """Function to send start events to Amplitude"""

    amplitude.track(
        BaseEvent(
            event_type="Start Event",
            user_id=user_id,
            event_properties={
                "source": source,
                "extra": extra
            }
        )
    )
