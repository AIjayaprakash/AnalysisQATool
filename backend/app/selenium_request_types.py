# types.py

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field

class LocatorStrategy(str, Enum):
    ID = "id"
    CSS = "css"
    XPATH = "xpath"
    NAME = "name"
    TAG = "tag"
    CLASS = "class"
class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"

class BrowserOptions(BaseModel):
    headless: bool = True
    arguments: Optional[List[str]] = []

class StartBrowserRequest(BaseModel):
    browser: BrowserType
    options: Optional[BrowserOptions] = None

class NavigateRequest(BaseModel):
    url: str

class ElementLocator(BaseModel):
    by: str
    value: str
    timeout: int = 5000  # milliseconds

class SendKeysRequest(ElementLocator):
    text: str

class KeyPressRequest(BaseModel):
    key: str

class LocalStorageRequest(BaseModel):
    key: str = Field(..., description="Key in local storage")
    value: Optional[str] = Field(None, description="Value to set (if operation is 'set')")
    operation: str = Field("get", description="Operation to perform (get, set, remove)")

class ScreenshotRequest(BaseModel):
    output_path: Optional[str] = Field(None,
                                       description="Optional path where to save the screenshot. If not provided, returns base64 data.")


class IFrameRequest(BaseModel):
    type: str = Field(..., description="Type of iframe selector (index, id, name, or element)")
    value: Optional[Union[str, int]] = Field(None, description="Value for the iframe selector")
    element_by: Optional[LocatorStrategy] = Field(None,
                                                  description="If type is 'element', locator strategy to find iframe element")
    element_value: Optional[str] = Field(None, description="If type is 'element', value for the locator strategy")

class ScrollRequest(BaseModel):
    direction: str = Field("down", description="Direction to scroll (up or down)")
    pixels: Optional[int] = Field(None, description="Number of pixels to scroll")

class IFrameRequest(BaseModel):
    type: str = Field(..., description="Type of iframe selector (index, id, name, or element)")
    value: Optional[Union[str, int]] = Field(None, description="Value for the iframe selector")
    element_by: Optional[LocatorStrategy] = Field(None,
                                                  description="If type is 'element', locator strategy to find iframe element")
    element_value: Optional[str] = Field(None, description="If type is 'element', value for the locator strategy")


