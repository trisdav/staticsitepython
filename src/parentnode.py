from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self,tag,children,value=None,props=None):
        self.tag=tag
        self.children=children
        self.value=value
        self.props=props

    def get_children(self, node):
        html=""

        if not isinstance(node,ParentNode):
            return node.to_html()
        else:
            html+=f"<{node.tag}{node.props_to_html()}>"
            for child in node.children:
                if not isinstance(child,ParentNode):
                    html+=child.to_html()
                else:
                    html+=child.get_children(child)
            html+=f"</{node.tag}>"
        return html

    def to_html(self):
        if self.tag == None:
            raise ValueError("No tag.")
        if not self.children:
            raise ValueError("No children.")
        return self.get_children(self)