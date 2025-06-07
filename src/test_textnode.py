import unittest

from textnode import TextNode, TextType
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
from main import split_nodes_delimiter
from main import extract_markdown_images
from main import split_nodes_image
from main import split_images_string
from main import text_to_textnodes
from main import markdown_to_blocks
from main import BlockType
from main import block_to_block_type
from main import markdown_to_html_node
from main import extract_title

class TestMarkdownFunctions(unittest.TestCase):
    def test_extract_title(self):
        md="# start"
        self.assertEqual(extract_title(md), "start")
        md="""
# start
# end
"""
        self.assertEqual(extract_title(md), "start")
        md="##fakeStart\n# start"
        self.assertEqual(extract_title(md), "start")
        md="#nostart"
        with self.assertRaises(Exception):
            self.assertEqual(extract_title(md), "nostart")

    def test_find_img(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(str(extract_markdown_images(text)), "[('rick roll', 'https://i.imgur.com/aKaOqIh.gif'), ('obi wan', 'https://i.imgur.com/fJRm4Vk.jpeg')]")
    
    def test_split(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(str(split_images_string(text)), "[('This is text with a ', <TextType.TEXT: 0>), ('![rick roll](https://i.imgur.com/aKaOqIh.gif)', <TextType.IMAGE: 5>), (' and ', <TextType.TEXT: 0>), ('![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)', <TextType.IMAGE: 5>)]")
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line


- This is a list




- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list",
                "- with items",
            ],
        )

    def test_blocks_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

> quote l1
> quote l2
> quote l3

# heading1

## heading2

### heading3

#### heading4

##### heading5

###### heading6

####### fake heading

- This is a list
- with items

1. li 1
2. li2
10. li3

```code123```

```bash
real code
```
"""
        expected=[BlockType.PARAGRAPH, BlockType.PARAGRAPH,
                BlockType.QUOTE,
                BlockType.HEADING, BlockType.HEADING, BlockType.HEADING, BlockType.HEADING, BlockType.HEADING, BlockType.HEADING,
                BlockType.PARAGRAPH,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.CODE,
                BlockType.CODE,
                ]
        blocks = markdown_to_blocks(md)
        types=[]
        for block in blocks:
            types.append(block_to_block_type(block))
        self.assertEqual(types,expected)

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.maxDiff=None
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff</code></pre></div>",
        )


    def test_heading(self):
        md = """
# HEADING

## HEADING 2

### HEADING 3

#### HEADING 4

##### HEADING 5

###### HEADING 6
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>HEADING</h1><h2>HEADING 2</h2><h3>HEADING 3</h3><h4>HEADING 4</h4><h5>HEADING 5</h5><h6>HEADING 6</h6></div>",
        )


    def test_blockquote(self):
        md = """
> multi line
> blockquotes
> are different
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>multi line<br>blockquotes<br>are different</blockquote></div>",
        )

    def test_ul(self):
        md = """
- multi line
- unordered list
- are different
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>multi line</li><li>unordered list</li><li>are different</li></ul></div>",
        )

    def test_ol(self):
        md = """
1. multi line
2. ordered list
10. are different
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>multi line</li><li>ordered list</li><li>are different</li></ol></div>",
        )

    def test_formatted_ul(self):
        md = """
- ![rick roll](https://i.imgur.com/aKaOqIh.gif)
- [link](https://boot.dev)
- **are different**
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><ul><li><img src="https://i.imgur.com/aKaOqIh.gif" alt="rick roll"></img></li><li><a href="https://boot.dev">link</a></li><li><b>are different</b></li></ul></div>',
        )

# How can I move thse into the class TestSplitDelimiter?
node0 = TextNode("one two **three** four five", TextType.TEXT)
node1 = TextNode("one **two** three **four** five", TextType.TEXT)
node2 = TextNode("**one** two three four **five**", TextType.TEXT)
node3 = TextNode("**one****two** three four five", TextType.TEXT)
node4 = TextNode("one **** two three four five", TextType.TEXT)
node5 = TextNode("one **two** **three four five", TextType.TEXT)

class TestSplitDelimiter(unittest.TestCase):
        def test_bold(self):
            self.assertEqual(str(split_nodes_delimiter([node0],"**", TextType.BOLD)),"[TextNode(one two , TextType.TEXT, None), TextNode(three, TextType.BOLD, None), TextNode( four five, TextType.TEXT, None)]")
            self.assertEqual(str(split_nodes_delimiter([node1],"**", TextType.BOLD)),"[TextNode(one , TextType.TEXT, None), TextNode(two, TextType.BOLD, None), TextNode( three , TextType.TEXT, None), TextNode(four, TextType.BOLD, None), TextNode( five, TextType.TEXT, None)]")
            self.assertEqual(str(split_nodes_delimiter([node2],"**", TextType.BOLD)),"[TextNode(one, TextType.BOLD, None), TextNode( two three four , TextType.TEXT, None), TextNode(five, TextType.BOLD, None)]")
            self.assertEqual(str(split_nodes_delimiter([node3],"**", TextType.BOLD)),"[TextNode(one, TextType.BOLD, None), TextNode(two, TextType.BOLD, None), TextNode( three four five, TextType.TEXT, None)]")
            self.assertEqual(str(split_nodes_delimiter([node4],"**", TextType.BOLD)),"[TextNode(one , TextType.TEXT, None), TextNode(, TextType.BOLD, None), TextNode( two three four five, TextType.TEXT, None)]")
            with self.assertRaises(Exception):
                split_nodes_delimiter([node5],"**", TextType.BOLD)
        
        def test_code(self):
            node0.text=node0.text.replace("**","`")
            node1.text=node1.text.replace("**","`")
            node2.text=node2.text.replace("**","`")
            node3.text=node3.text.replace("**","`")
            node4.text=node4.text.replace("**","`")
            node5.text=node5.text.replace("**","`")
            self.assertEqual(str(split_nodes_delimiter([node0],"`", TextType.CODE)),"[TextNode(one two , TextType.TEXT, None), TextNode(three, TextType.BOLD, None), TextNode( four five, TextType.TEXT, None)]".replace("BOLD","CODE"))
            self.assertEqual(str(split_nodes_delimiter([node1],"`", TextType.CODE)),"[TextNode(one , TextType.TEXT, None), TextNode(two, TextType.BOLD, None), TextNode( three , TextType.TEXT, None), TextNode(four, TextType.BOLD, None), TextNode( five, TextType.TEXT, None)]".replace("BOLD","CODE"))
            self.assertEqual(str(split_nodes_delimiter([node2],"`", TextType.CODE)),"[TextNode(one, TextType.BOLD, None), TextNode( two three four , TextType.TEXT, None), TextNode(five, TextType.BOLD, None)]".replace("BOLD","CODE"))
            self.assertEqual(str(split_nodes_delimiter([node3],"`", TextType.CODE)),"[TextNode(one, TextType.BOLD, None), TextNode(two, TextType.BOLD, None), TextNode( three four five, TextType.TEXT, None)]".replace("BOLD","CODE"))
            self.assertEqual(str(split_nodes_delimiter([node4],"`", TextType.CODE)),"[TextNode(one , TextType.TEXT, None), TextNode(, TextType.BOLD, None), TextNode( two three four five, TextType.TEXT, None)]".replace("BOLD","CODE"))
            with self.assertRaises(Exception):
                split_nodes_delimiter([node5],"`", TextType.CODE)

        def test_split_images(self):
            node = TextNode(
                "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
                TextType.TEXT,
            )
            new_nodes = split_nodes_image([node])
            self.assertListEqual(
                [
                    TextNode("This is text with an ", TextType.TEXT),
                    TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                    TextNode(" and another ", TextType.TEXT),
                    TextNode(
                        "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                    ),
                ],
                new_nodes,
            )

        def test_text_to_nodes_basic(self):
            nodes=text_to_textnodes("This is **text** with an _italic_ word and a `code block`")
            self.maxDiff=None
            self.assertEqual(str(nodes),'[TextNode(This is , TextType.TEXT, None), TextNode(text, TextType.BOLD, None), TextNode( with an , TextType.TEXT, None), TextNode(italic, TextType.ITALIC, None), TextNode( word and a , TextType.TEXT, None), TextNode(code block, TextType.CODE, None)]')

        def test_text_to_nodes_image(self):
            nodes=text_to_textnodes("This is an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
            self.maxDiff=None
            self.assertEqual(str(nodes),'[TextNode(This is an , TextType.TEXT, None), TextNode(obi wan image, TextType.IMAGE, https://i.imgur.com/fJRm4Vk.jpeg), TextNode( and a , TextType.TEXT, None), TextNode(link, TextType.LINK, https://boot.dev)]')
        
        #def test_text_to_nodes(self):
        #    nodes=text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        #    self.maxDiff=None
        #    self.assertEqual(str(nodes),'[TextNode(this is , TextType.TEXT, None), TextNode(text, TextType.BOLD, None), TextNode( with an , TextType.TEXT, None), TextNode(italic, TextType.ITALIC, None), TextNode( word and a , TextType.TEXT, None), TextNode(code block, TextType.CODE, None), TextNode( and an , TextType.TEXT, None), TextNode(obi wan image, TextType.IMAGE, https://i.imgur.com/fJRm4Vk.jpeg), TextNode( and a , TextType.TEXT, None), TextNode(link, TextType.LINK, https://boot.dev)]')


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is  text node", TextType.BOLD)
        self.assertNotEqual(node, node2)
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is 1 text node", TextType.TEXT)
        self.assertNotEqual(node, node2)
        node = TextNode("This is a text node", TextType.BOLD, "ABCD.COM")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_link_none(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertIsNone(node.url)
    
    def test_link_not_none(self):
        node = TextNode("This is a text node", TextType.LINK,"ABCD.COM")
        self.assertIsNotNone(node.url)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = node.to_html_node()
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_text_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = node.to_html_node()
        self.assertEqual(html_node.to_html(), "<b>This is a text node</b>")
    def test_text_italic(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        html_node = node.to_html_node()
        self.assertEqual(html_node.to_html(), "<i>This is a text node</i>")
    def test_text_CODE(self):
        node = TextNode("This is a text node", TextType.CODE)
        html_node = node.to_html_node()
        self.assertEqual(html_node.to_html(), "<code>This is a text node</code>")
    def test_text_link(self):
        node = TextNode("This is a text node", TextType.LINK,"www.google.com")
        html_node = node.to_html_node()
        self.assertEqual(html_node.to_html(), "<a href=\"www.google.com\">This is a text node</a>")
    def test_text_image(self):
        node = TextNode("This is a text node", TextType.IMAGE, "www.google.com/logo.png")
        html_node = node.to_html_node()
        self.assertEqual(html_node.to_html(), "<img src=\"www.google.com/logo.png\" alt=\"This is a text node\"></img>")



class TestHtmlNode(unittest.TestCase):
    def test_init(self):
        node = HTMLNode()
        self.assertIsNotNone(node)

    def test_print(self):
        cNode = HTMLNode()
        props={"test":"words"}
        node = HTMLNode("aaa","bbb",[cNode],props)
        self.assertEqual(str(node),"Tag=aaa, value=bbb, props={'test': 'words'}, children=[Tag=None, value=None, props=None, children=None]")


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    def test_leaf_props(self):
        node = LeafNode("p", "Hello, world!",{"href":"www.google.com"})
        self.assertEqual(node.to_html(), "<p href=\"www.google.com\">Hello, world!</p>")
    def test_print(self):
        node = LeafNode("p", "Hello, world!",{"href":"www.google.com"})
        self.assertEqual(str(node), "Tag=p, value=Hello, world!, props={'href': 'www.google.com'}")

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild",{"hidden":"true"})
        child_node = ParentNode("span", [grandchild_node],props={"style":"{font-color=green;}"})
        parent_node = ParentNode("div", [child_node],props={"style":"{font-color=red;}"})
        self.assertEqual(
            parent_node.to_html(),
            '<div style="{font-color=red;}"><span style="{font-color=green;}"><b hidden="true">grandchild</b></span></div>',
        )

if __name__ == "__main__":
    unittest.main()