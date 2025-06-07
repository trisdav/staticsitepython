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
    exp=r"[\[\(](.*?)[\]\)]"
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
    exp=r"!*\[.*?\]\((.*?)\)"
    matches = list(re.finditer(exp,text))
    imageRanges=[]
    for i in range(0,len(matches)):
        imageRanges.append((matches[i].start(),matches[i].end()))
    lastEnd = 0
    start = 0
    end = 0
    for imageRange in imageRanges:
        if lastEnd == imageRange[0]: # No string before the match
            start = imageRange[0]
            end = imageRange[1]
        else: # String before the match
            start = lastEnd
            end = imageRange[0]
            split.append((text[start:end], textnode.TextType.TEXT))
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
            #print(splitStrings)
            for splitString in splitStrings:
                if splitString[1] == textnode.TextType.TEXT:
                    new_nodes.append(textnode.TextNode(splitString[0], textnode.TextType.TEXT))
                if splitString[1] == textnode.TextType.IMAGE:
                    img = extract_markdown_images(splitString[0])[0]
                    new_nodes.append(textnode.TextNode(img[0], textnode.TextType.IMAGE, url=img[1]))
                if splitString[1] == textnode.TextType.LINK:
                    img = extract_markdown_images(splitString[0])[0]
                    new_node = textnode.TextNode(img[0], textnode.TextType.LINK, url=img[1])
                    new_nodes.append(new_node)
                    
                
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
            return LeafNode(f"h{level}", block.lstrip("# ").strip())
        case BlockType.CODE:
            node = LeafNode("code",block.strip("`").strip())
            return ParentNode("pre", [node])
        case BlockType.QUOTE:
            blockLines = block.split("\n")
            lines=[]
            for blockLine in blockLines:
                lines.append(blockLine.strip(">").strip())
            return LeafNode("blockquote", "<br>".join(lines))
        case BlockType.UNORDERED_LIST:
            blockLines = block.split("\n")
            children=[]
            for blockLine in blockLines:
                cleanLine = blockLine.strip("- ").strip()
                childNodes = text_to_textnodes(cleanLine)
                content = ""
                for node in childNodes:
                 #   print(node)
                    content += node.to_html()
                #print(content)
                children.append(LeafNode("li",content))
            return ParentNode("ul",children)
        case BlockType.ORDERED_LIST:
            blockLines = block.split("\n")
            children=[]
            subexpr=r"^[0-9]+\. "
            for blockLine in blockLines:
                cleanLine = re.sub(subexpr,"",blockLine).strip()
                childNodes = text_to_textnodes(cleanLine)
                content = ""
                for node in childNodes:
                    content += node.to_html()
                children.append(LeafNode("li",content))
            return ParentNode("ol",children)

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
            newDest = os.path.join(dest,file)
            os.makedirs(os.path.join(dest,file), exist_ok=True)
            copyFiles(filePath,newDest)

def extract_title(md):
    startTitle = md.find("# ")
    if startTitle == -1:
        raise Exception("No title find in markdown file.")

    endTitle = md[startTitle:].find("\n")
    title=""
    if endTitle > -1: # If the string is longer than one line.
        title = md[startTitle:endTitle+1]
    else:
        title= md[startTitle:]
    title = title.lstrip("#").strip()
    return title

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    fmd=""
    with open(from_path,"r") as fp:
        fmd=fp.read()
    tmd=""
    with open(template_path,"r") as tp:
        tmd=tp.read()
    fhtml=markdown_to_html_node(fmd).to_html()
    title = extract_title(fmd)
    tmd = tmd.replace("{{ Title }}", title)
    tmd = tmd.replace("{{ Content }}", fhtml)
    tmd = tmd.replace("href=\"/", f"href=\"{basepath}")
    tmd = tmd.replace("src=\"/", f"src=\"{basepath}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as dp:
        dp.write(tmd)
    
def generate_pages_recursive(dir_content, temp_path, dest_path, basepath):
    files = os.listdir(dir_content)
    for file in files:
        
        if os.path.isfile(os.path.join(dir_content,file)):
            if file.endswith(".md"):
                contSrc = os.path.join(dir_content,file)
                contDest = os.path.join(dest_path,file)
                generate_page(contSrc, temp_path, contDest.replace(".md",".html"), basepath)
        else:
            nextContent = os.path.join(dir_content,file)
            nextDest = os.path.join(dest_path,file)
            generate_pages_recursive(nextContent,temp_path, nextDest.replace(".md",".html"), basepath)

def main(basepath):
    rmdir = os.path.abspath("docs/")
    if os.path.exists(rmdir):
        cont=input(f"Remove directory {rmdir} (y/n)? ")
        if cont.upper() == "Y":
            shutil.rmtree("docs/")
        else:
            print("Must remove docs directory to continue.")
            return 0
    print("Copying files...")
    copyFiles("static","docs")
    generate_pages_recursive("content","template.html","docs",basepath)
    #tn = textnode.TextNode("aaa",textnode.TextType.TEXT,"")
    #text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")

if __name__=="__main__":
    import sys
    basepath="/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    main(basepath)