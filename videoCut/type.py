from enum import Enum
from typing import TypedDict,Literal,Union,get_args
SPEECH_ARRAY_INDEX = TypedDict("SPEECH_ARRAY_INDEX", {"start": float, "end": float})
DEVICE = Union[Literal["cpu", "cuda:1"], None]
MODEL = Literal[
    "tiny", 
    "base", 
    "small", 
    "medium", 
    "large", 
    "large-v1",
    "large-v2",
    "large-v3"]
LANG = Literal[
    "zh",
    "en",
    "Afrikaans",
    "Arabic",
    "Armenian",
    "Azerbaijani",
    "Belarusian",
    "Bosnian",
    "Bulgarian",
    "Catalan",
    "Croatian",
    "Czech",
    "Danish",
    "Dutch",
    "Estonian",
    "Finnish",
    "French",
    "Galician",
    "German",
    "Greek",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Indonesian",
    "Italian",
    "Japanese",
    "Kannada",
    "Kazakh",
    "Korean",
    "Latvian",
    "Lithuanian",
    "Macedonian",
    "Malay",
    "Marathi",
    "Maori",
    "Nepali",
    "Norwegian",
    "Persian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Serbian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swahili",
    "Swedish",
    "Tagalog",
    "Tamil",
    "Thai",
    "Turkish",
    "Ukrainian",
    "Urdu",
    "Vietnamese",
    "Welsh",
]

