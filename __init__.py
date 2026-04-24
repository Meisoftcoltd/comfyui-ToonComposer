from .tooncomposer_nodes import ToonComposerSequentialWrapper

NODE_CLASS_MAPPINGS = {
    "ToonComposerSequentialWrapper": ToonComposerSequentialWrapper
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ToonComposerSequentialWrapper": "ToonComposer SLRA Sequential Wrapper"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
