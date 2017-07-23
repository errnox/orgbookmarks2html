import re
from string import Template
import itertools


class Tag(object):
    # args[0]: name
    # args[1]: content
    def __init__(self, *args, **kwargs):
        if len(args) <= 1:
            content = ""
        else:
            content = args[1]
        self.name = args[0]
        self.content = []
        self.content.append(content)
        self.attrs = {}
        self._tag = ""
        self.start_tag_signature = []
        self.start_tag = ""
        self.end_tag = ""
        self.has_attrs = False
        if len(kwargs) > 0:
            self.has_attrs = True
        # Not necessary, but helpful for one tag elements later on...
        if len(content) >= 0:
            # self.start_tag = "<%s>" % (self.name)  # Consider this!
            self.start_tag_signature = ["<", self.name, ">"]
            self.end_tag = "</%s>" % (self.name)
        for kwword in kwargs:
            self.attrs[kwword] = str(kwargs[kwword])
        self._add_attr(**kwargs)
        self._build()

    def _add_attr(self, **kwargs):
        # DEBUG
        #
        # for key in self.attrs:
        #     print "%10s: %10s\t%10s: %10s" % (key, type(key), self.attrs[key], type(self.attrs[key]))
        # Add attribute-value pairs to the signature of the start tag
        for attr in self.attrs:
            self.start_tag_signature.insert(-1, " ")
            self.start_tag_signature.insert(-1, attr)
            self.start_tag_signature.insert(-1, "=")
            self.start_tag_signature.insert(-1, "\"" + self.attrs[attr] + "\"")

    def add(self, content):
        self.content.append(content)
        self._build()  # Rebuild the tag

    def _build(self):
        # Remove the last whitespace between last attribute value and '>'
        # Build the start tag
        self.start_tag = ""
        for element in self.start_tag_signature:
            self.start_tag += element

        # Add other tags to the body of the current tag
        self._tag = ""  # Clean the tag
        self._tag += self.start_tag
        for c in self.content:
            self._tag += c
        self._tag += self.end_tag

    def get(self):
        return self._tag


class Obj(object):
    def __init__(self):
        pass

    @staticmethod
    def Button(url, text):
        # button = '<button type="button" onClick="alert(\'%s\');">%s</button>' % (url, text)
        button = Tag("button",
                     type="button",
                     onClick="alert(\'%s\');" % url,
                     style="color:white;background-color:blue;")
        button.add(text)
        return button.get()

    @staticmethod
    def Link(url, text):
        # link = '<a href="%s">%s</a>' % (url, text)
        link = Tag("a", href=url, style="color:red;background-color:black;")
        link.add(str(text))
        return link.get()

    @staticmethod
    def Table(table, **kwargs):
        t = Tag("table", **kwargs)
        has_header = False  # Indicates if table has already a header
        for row in table:
            tr = Tag("tr")
            if has_header == False:
                for cell in row:
                    th = Tag("th", cell)
                    tr.add(th.get())
                t.add(tr.get())
                has_header = True
            else:
                for cell in row:
                    td = Tag("td", cell)
                    tr.add(td.get())
                t.add(tr.get())

            # for cell in row:
            #     td = Tag("td", cell)
            #     tr.add(td.get())
            # t.add(tr.get())
        # print t.get()
        return t.get()

    @staticmethod
    def Form(action, method, content):
        form = Tag("form", action=action, method=method)
        form.add(content)
        print "INPUT: ", form.get()
        return form.get()

    @staticmethod
    def Input(type, name, value):
        input = Tag("input", type=type, name=name, value=value)
        return input.get()


class Converter(object):
    def __init__ (self, inputFile):
        self.inFile = open(inputFile, 'r')
        self.input = []
        self.output = []

    def convert(self):
        current_text = ''
        current_url = ''
        text = re.compile('\A\s*\*\s+')
        url = re.compile('\w')

        # Beginning of document
        self.output.append("<html>")
        self.output.append("<head></head>")
        self.output.append("<body>")
        self.output.append("<span>")

        for line in self.inFile:
            if text.match(line) or url.match(line):
                self.input.append(line)

        for line in self.input:
            if text.match(line):
                line = re.sub('\A\s*\*\s', '', line)
                line = re.sub('\s*\Z', '', line)
                current_text = line
            elif url.match(line):
                line = re.sub('\A\s*', '', line)
                line = re.sub('\s*\Z', '', line)
                current_url = line
            else:
                pass

            self.output.append("<span>")
            self.output.append(Obj.Button(current_url, 'URL'))
            self.output.append(Obj.Link(current_url, current_text))
            self.output.append("<br/>")
            self.output.append("</span>")

        # self.output.append("<span>")
        test_table = Obj.Table([
                    ["Color", "Topic", "Notes"],
                    ["Red", "Love", "---"],
                    ["Green", "Hope", "Something..."],
                    ["Blue", "Strength", "---"]])
        self.output.append(test_table)
        # self.output.append("</span>")

        # ----------------------------------------------------------------
        # DEBUG
        self.output.append("<span>")
        def grouper(n, iterable, fillvalue=None):
            "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
            args = [iter(iterable)] * n
            return itertools.izip_longest(fillvalue=fillvalue, *args)

        num_table = []
        for i in grouper(3, range(10), '-'):
            temp_row = []
            for num in i:
                temp_row.append(str(num))
            num_table.append(list(temp_row))

        print num_table
        number_table = Obj.Table(num_table, border=1)
        print number_table
        self.output.append(number_table)
        self.output.append("</span>")
        # ----------------------------------------------------------------

        # self.output.append("<span>")
        form = Obj.Form("", "get", Obj.Input("text", "Name", "John Doe"))
        self.output.append(form)
        # self.output.append("</span>")


        # End of document
        self.output.append("</span>")
        self.output.append("</body>")
        self.output.append("</html>")


        self.inFile.close()

        with open('output.html', 'w+') as outFile:
            for idx, line in enumerate(self.output):
                if idx % 2 == 0:
                    outFile.write(line)


if __name__ == '__main__':
    converter = Converter('res/notes.org')
    converter.convert()

