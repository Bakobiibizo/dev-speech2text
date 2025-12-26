from pydantic import BaseModel, Extra, Field, root_validator
from pydantic.class_validators import validator
from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List
from loguru import logger
import enum
from typing import Optional, List, Union, Dict, Literal
from datetime import datetime
import uuid, json


class InputPromptModel(BaseModel):
    themeData: Optional[int] = 1
    board: Optional[int] = 1
    customBoard: Optional[str] = None
    avatar: Optional[str] = None
    imprintValue: Optional[float]
    creativity: Optional[float]
    steps: Optional[int]
    prompt: Optional[str]


class BoardgameArtRequest(BaseModel):
    themeData: int
    board: Optional[int] = None
    customBoard: Optional[str] = None
    avatar1: Optional[str] = None
    avatar2: Optional[str] = None
    avatar3: Optional[str] = None
    avatar4: Optional[str] = None
    imprintValue: Optional[float] = None
    creativity: Optional[float] = None
    steps: Optional[int] = None
    prompt: Optional[str] = None
    randomize: Optional[bool] = None


class ArtModelInput(BaseModel):
    ckpt_name: Optional[str] = None
    samples: Optional[List[Union[str, int]]] = None
    vae: Optional[List[Union[str, int]]] = None
    filename_prefix: Optional[str] = None
    images: Optional[List[Union[str, int]]] = None


class ArtModule(BaseModel):
    inputs: ArtModelInput
    class_type: str


class ArtRequest(BaseModel):
    themeData: int
    img2img: Optional[str] = None
    imprint_value: Optional[float] = None
    creativity: Optional[float] = None
    steps: Optional[int] = None
    user_prompt: Optional[str] = None
    randomize: Optional[bool] = None
    modules: Optional[List[ArtModule]] = None
    prompt: Optional[str] = None


class TTSGenerationResponse(BaseModel):
    prompt: str


class VideoGenerationRequest(BaseModel):
    prompt: str
    fps: Optional[int] = 16
    image: Optional[str] = None


class VideoGenerationResponse(BaseModel):
    video: str
    video_filename: Optional[str] = None
    gif_filename: Optional[str] = None
    image_filename: Optional[str] = None


class TranscriptionComplete(BaseModel):
    audio: str
    audio_filename: Optional[str] = None


class EndpointConfig(BaseModel):
    host: str
    port: str
    endpoint: str
    url: str


class EndpointLabels(BaseModel):
    hub: str = "hub"
    speech2text: str = "speech2text"


class EndpointMap(BaseModel):
    environment: Optional[str] = ""
    version: Optional[str] = ""
    baseurl: Optional[str] = ""
    hub: Optional[str] = ""
    endpoint_map: Optional[Dict[str, str]] = {}
    endpoint_labels: Optional[Dict[str, str]] = {}
    url_map: Optional[Dict[str, str]] = {}


class EndpointManager(BaseModel):
    environment: str
    version: str
    hub: EndpointConfig
    speech2text: EndpointConfig


class ConfigManager(ABC):
    @abstractmethod
    def get_config(self, value: str):
        pass

    @abstractmethod
    def get_url(self, host, port, version, endpoint) -> str:
        pass

    @abstractmethod
    def set_item(self, key, value) -> None:
        pass


class OAIMessage(BaseModel):
    role: str
    content: str


class TranscriptionRequest(BaseModel):
    data: Optional[str] = "multipart/form-data"
    temperature: Optional[str] = "0.0"
    temperature_inc: Optional[str] = "0.2"
    response_format: Optional[str] = "json"


class TokenUsage(BaseModel):
    total: int
    prompt: int
    request: int
    response: int


class ChoicesMessage(BaseModel):
    finish_reason: str
    index: int
    logprobs: str
    finish_reason: str
    Messages: List[OAIMessage]


class OAIResponse(BaseModel):
    id: Optional[Union[int, None]]
    object: Optional[Union[str, None]]
    created: Optional[Union[int, None]]
    model: Optional[Union[str, None]]
    system_fingerprint: Optional[Union[str, None]]
    choices: Optional[Union[ChoicesMessage, None]]
    usage: Optional[Union[TokenUsage, None]]


imageId = None
stylePositive = None
styleNegative = None
styleInput = None
inputSeed = None
boardControl = None
inputBoard = None
numberOfSteps = None
creativity = None


def getPrompt(
    imageId,
    positivePrompt,
    negativePrompt,
    stylePositive,
    styleNegative,
    inputSeed,
    boardControl,
    inputBoard,
    numberOfSteps,
    creativity,
):
    file_path = Path.cwd() / "src" / "static" / "prompt.json"

    prompt_text = file_path.read_text()

    prompt_map = {
        "{{board_strength}}": str(boardControl),
        "{{board_image}}": str(inputBoard),
        "{{seed}}": str(inputSeed),
        "{{steps}}": str(numberOfSteps),
        "{{creativity}}": str(creativity),
        "{{positive_prompt}}": str(positivePrompt),
        "{{negative_prompt}}": str(negativePrompt),
        "{{positive_style}}": str(styleNegative),
        "{{negative_style}}": str(stylePositive),
        "{{image_id}}": str(imageId),
    }

    for key, value in prompt_map.items():
        prompt_text = prompt_text.replace(key, str(value))
    return prompt_text


class OllamaRequest(BaseModel):
    images: Optional[List[str]] = None
    streaming: Optional[bool] = True
    prompt: Optional[str] = None
    model: Optional[str] = None


class FingoRequest(BaseModel):
    themeData: int
    board: int
    avatarData: Optional[str] = None
    avatarData2: Optional[str] = None
    imprintValue: Optional[str] = None
    creativity: Optional[str] = None
    steps: Optional[str] = None
    prompt: Optional[str] = None
