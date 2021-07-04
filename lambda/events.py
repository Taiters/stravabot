import functools
from typing import Callable

from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core.models.trace_header import TraceHeader

patch_all()


def traced(func: Callable) -> Callable:
    @functools.wraps
    def decorator(event, context):
        message = event["Records"][0]
        attributes = message["attributes"]
        if "AWSTraceHeader" in attributes:
            trace_header = TraceHeader.from_header_str(attributes["AWSTraceHeader"])
            segment = xray_recorder.current_segment
            segment.trace_id = trace_header.root
            segment.parent_id = trace_header.parent
            segment.sampled = trace_header.sampled
        return func(event, context)

    return decorator


@traced
def handler(event, context):
    print(event)
