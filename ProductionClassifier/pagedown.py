import json
import PyV8

class PagedownToHtml():
    def __init__(self):
        js1 = open("Third/pagedown/Markdown.Converter.js").read()
        js2 = open("Third/pagedown/Markdown.Sanitizer.js").read()  

        self.ctxt = PyV8.JSContext()
        self.ctxt.enter()   
        self.ctxt.eval(js1)
        self.ctxt.eval(js2)
        self.ctxt.eval("converter = new Markdown.getSanitizingConverter();")

    def convert(self, markdown):
        return self.ctxt.eval("converter.makeHtml(" + json.dumps(markdown) + ")")