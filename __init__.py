import json
from pathlib import Path

from .tools import (
   handle_simple_travel,
   handle_blocks_world,
   handle_rescue,
   handle_robosub,
   handle_healthcare,
   handle_temporal_travel,
)

_SCHEMAS_DIR = Path(__file__).parent / "schemas"

_TOOLS = [
    ("plan_sample_simple_travel",  handle_simple_travel),
    ("plan_sample_blocks_world",   handle_blocks_world),
    ("plan_sample_rescue",         handle_rescue),
    ("plan_sample_robosub",        handle_robosub),
    ("plan_sample_healthcare",     handle_healthcare),
    ("plan_sample_temporal_travel", handle_temporal_travel),
]


def register(ctx):
    plugin_name = ctx.manifest.name
    for name, handler in _TOOLS:
        schema = json.loads((_SCHEMAS_DIR / f"{name}.json").read_text())
        ctx.register_tool(name, plugin_name, schema, handler)
