import textnode
from leafnode import LeafNode
from parentnode import ParentNode
import re
from enum import Enum

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes=[]
    for node in old_nodes:
        if node.text_type == textnode.TextType.TEXT:
            splitString = node.text.split(delimiter)
            # Fascination, for each delimiter n in the string, there will be n+1 strings created.
            #  Also, assuming  there is an even number of delimiters, every other element in the split
            #  will be enclosed by the delimiters.
            if len(splitString)%2 == 0:
                raise Exception("Invalid syntax, missing delimiter: " + delimiter + " in: " + node.text)
            for i in range(0,len(splitString),2):
                if len(splitString[i]) > 0:
                    new_nodes.append(textnode.TextNode(splitString[i], textnode.TextType.TEXT))
                if i+1 < len(splitString):
                    new_nodes.append(textnode.TextNode(splitString[i+1], text_type))
        else:
            new_nodes.append(node)
    return new_nodes

def extract_markdown_images(text):
    exp=r"!*[\[\(](.*?)[\]\)]"
    matches = re.findall(exp,text)
    if len(matches)%2!=0:
        raise Exception("Syntax error: Incomplete image tag: " + text)
    images=[]
    for i in range(0,len(matches),2):
        images.append((matches[i],matches[i+1]))
    return images

def split_images_string(text):
    """
    Return a list of tuples where the first is the string split, the second the TextType.
    """
    split=[]
    exp=r"!*[\[\(](.*?)[\]\)]"
    matches = list(re.finditer(exp,text))
    if len(matches)%2!=0:
        raise Exception("Syntax error: Incomplete image tag: " + text)
    imageRanges=[]
    for i in range(0,len(matches),2):
        imageRanges.append((matches[i].start(),matches[i+1].end()))
    lastEnd = 0
    for imageRange in imageRanges:
        if lastEnd == imageRange[0]: # No string before the match
            split.append((text[imageRange[0]:imageRange[1]], textnode.TextType.IMAGE))
        else: # String before the match
            #print(textnode.TextType.TEXT)
            split.append((text[lastEnd:imageRange[0]], textnode.TextType.TEXT))
            imageText = text[imageRange[0]:imageRange[1]]
            if imageText.startswith("!"):
                split.append((imageText, textnode.TextType.IMAGE))
            else:
                split.append((imageText, textnode.TextType.LINK))
        lastEnd = imageRange[1]
    if lastEnd != len(text): # string after match
        split.append((text[lastEnd:], textnode.TextType.TEXT))
    return split

def split_nodes_image(old_nodes):
    new_nodes=[]
    for node in old_nodes:
        if node.text_type == textnode.TextType.TEXT:
            splitStrings = split_images_string(node.text)
            for splitString in splitStrings:
                if splitString[1] == textnode.TextType.TEXT:
                    new_nodes.append(textnode.TextNode(splitString[0], textnode.TextType.TEXT))
                if splitString[1] == textnode.TextType.IMAGE:
                    img = extract_markdown_images(splitString[0])[0]
                    new_nodes.append(textnode.TextNode(img[0], textnode.TextType.IMAGE, url=img[1]))
                if splitString[1] == textnode.TextType.LINK:
                    img = extract_markdown_images(splitString[0])[0]
                    new_nodes.append(textnode.TextNode(img[0], textnode.TextType.LINK, url=img[1]))
        else:
            new_nodes.append(node)
    return new_nodes

def text_to_textnodes(text):
    node = textnode.TextNode(text,textnode.TextType.TEXT)
    nodes = [node]
    nodes = split_nodes_delimiter(nodes,"**",textnode.TextType.BOLD)
    nodes = split_nodes_delimiter(nodes,"_",textnode.TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes,"`",textnode.TextType.CODE)
    nodes = split_nodes_image(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    for i in range(0,len(blocks)):
        clean=[]
        for line in blocks[i].split("\n"):
            if line !="":
                clean.append(line.strip())
        blocks[i]="\n".join(clean)
    blocks = list(filter(lambda text: text!="", blocks))
    return blocks

class BlockType(Enum):
    PARAGRAPH=""
    HEADING=r"^#{1,6} "
    CODE=r"^```[\s\S]*```$"
    QUOTE=r"^>"
    UNORDERED_LIST=r"^- "
    ORDERED_LIST=r"^[0-9]+\."

def block_to_block_type(textBlock):
    headingList = re.findall(BlockType.HEADING.value,textBlock)
    codeList = re.findall(BlockType.CODE.value,textBlock)
    quoteList = re.findall(BlockType.QUOTE.value,textBlock)
    unList = re.findall(BlockType.UNORDERED_LIST.value,textBlock)
    ordList = re.findall(BlockType.ORDERED_LIST.value,textBlock)

    if headingList:
        return BlockType.HEADING
    elif codeList:
        return BlockType.CODE
    elif quoteList:
        return BlockType.QUOTE
    elif unList:
        return BlockType.UNORDERED_LIST
    elif ordList:
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def get_node(block, blockType):
    match blockType:
        case BlockType.PARAGRAPH:
            texts = text_to_textnodes(block)
            #print(texts)
            content=""
            for text in texts:
                content+=text.to_html()
            node = LeafNode("p",content)
            return node
        case BlockType.HEADING:
            level=0
            for i in range(0,len(block)):
                if block[i]=="#":
                    level+=1
                if level == 6:
                    break
            # Heading in mark down can't have children...
            return LeafNode(f"h{level}", block)
        case BlockType.CODE:
            node = LeafNode("code",block)
            return ParentNode("pre", [node])
        case BlockType.QUOTE:
            return LeafNode("blockquote", block)
        case BlockType.UNORDERED_LIST:
            return LeafNode("ul",block)
        case BlockType.ORDERED_LIST:
            return LeafNode("li",block)

def markdown_to_html_node(md):
    blocks = markdown_to_blocks(md)
    nodes = [(get_node(block,block_to_block_type(block))) for block in blocks]
    div = ParentNode("div",nodes)
    #root = ParentNode("html",[body])
    with open("test.html", 'w') as testfile:
        for node in nodes:
            testfile.write(node.to_html())
    return div

import os
import shutil
def copyFiles(src,dest):
    files=os.listdir(src)
    for file in files:
        filePath=os.path.join(src,file)
        print(filePath)
        if os.path.isfile(filePath):
            destPath = os.path.join(dest,file)
            shutil.copy(filePath, destPath)
        else:
            os.makedirs(os.path.join(dest,file), exist_ok=True)
            copyFiles(filePath,dest)
    
def main():
    copyFiles("static","public")
    #tn = textnode.TextNode("aaa",textnode.TextType.TEXT,"")
    #text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")

main()