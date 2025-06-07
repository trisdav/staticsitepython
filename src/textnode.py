from leafnode import LeafNode
from enum import Enum

class TextType(Enum):
    TEXT = 0
    BOLD = 1
    ITALIC = 2
    CODE = 3
    LINK = 4
    IMAGE = 5


class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(a,b): # a is self here.
        return a.text == b.text and a.text_type == b.text_type and a.url == b.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

    # Where should this go? instructions didn't say.
    def to_html(self):
        if not isinstance(self, TextNode):
            raise Exception("Invalid text node")
        match(self.text_type):
            case TextType.TEXT:
                return self.text.replace("\n"," ") # This makes no sense, but the provided unit test requires it.
            case TextType.BOLD:
                return LeafNode("b",self.text).to_html() #f"<b>{self.text}</b>"
            case TextType.ITALIC:
                return LeafNode("i",self.text).to_html() #f"<i>{self.text}</i>"
            case TextType.CODE:
                return LeafNode("code",self.text).to_html() #f"<code>{self.text}</code>"
            case TextType.LINK:
                return LeafNode("a",self.text,{"href":self.url}).to_html() #f"<a href=\"{self.url}\">{self.text}</a>"
            case TextType.IMAGE:
                return LeafNode("img",None,{"src":self.url,"alt":self.text}).to_html() #f"<img src=\"{self.url}\" alt=\"{self.text}\"</img>"
            case _:
                raise Exception("Invalid text type")
    
    # Function useful in testing.
    def to_html_node(self):
        if not isinstance(self, TextNode):
            raise Exception("Invalid text node")
        match(self.text_type):
            case TextType.TEXT:
                return LeafNode(None,self.text)
            case TextType.BOLD:
                return LeafNode("b",self.text) #f"<b>{self.text}</b>"
            case TextType.ITALIC:
                return LeafNode("i",self.text) #f"<i>{self.text}</i>"
            case TextType.CODE:
                return LeafNode("code",self.text) #f"<code>{self.text}</code>"
            case TextType.LINK:
                return LeafNode("a",self.text,{"href":self.url}) #f"<a href=\"{self.url}\">{self.text}</a>"
            case TextType.IMAGE:
                return LeafNode("img",None,{"src":self.url,"alt":self.text}) #f"<img src=\"{self.url}\" alt=\"{self.text}\"</img>"
            case _:
                raise Exception("Invalid text type")