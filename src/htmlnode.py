
class HTMLNode():
    def __init__(self,tag=None,value=None,children=None,props=None):
        self.tag = tag
        self.value=value
        self.children=children
        self.props=props

    
    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self):
        prop_str=""

        # I want self.props to default to an empty list, but instructions didn't say so...
        if self.props == None:
            return prop_str

        for prop in self.props:
            prop_str += f" {prop}=\"" + self.props[prop] + "\""
        return prop_str
    
    def __repr__(self):
        return f"Tag={self.tag}, value={self.value}, props={self.props}, children={self.children}"
        


    