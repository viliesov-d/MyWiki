'''Convers GitHub-styled markdown to HTML

Functions:
    md2html(string)
'''
import re

# Declare a dictionary to contain html tag to re mappings
tag_map = {}

# Headers: 1 to 6 #'s
for i in range(1, 7):
	tag_map[f"<h{i}>"] = [re.compile("^(" + ("#" * i) + r"\s+(.*))$")]

# All bold and italic: ***
tag_map["<strong><em>"] = [re.compile(r"(\*{3}(.*?)\*{3})")]

# Bold: ** and __
tag_map["<strong>"] = [
    re.compile(r"((?<!\*)\*{2}(?!\*)(.*?)(?<!\*)\*{2}(?!\*))"),
    re.compile(r"(_{2}(?P<text2>.*?)_{2})")
]

# Italic: * and _
tag_map["<em>"] = [
    re.compile(r"((?<!\*)\*{1}?(?!\*)(.*?)(?<!\*)\*{1}(?!\*))"),
    re.compile(r"((?<!_)_{1}(?!_)(?P<text2>.*?)(?<!_)_{1}(?!_))")
]

# Strikethrough: ~~
tag_map["<strike>"] = [re.compile(r"((?<!~)~{2}(?!~)(.*?)(?<!~)~{2}(?!~))")]

# Links
tag_map["<a>"] = [re.compile(r"(\[(.*?)\]\((.*?)\))")]

# Marked lists: * and -
tag_map["<li>"] = [re.compile(r"^(-\s(.*))"),
    re.compile(r"^(\*\s(.*))")
]

# Utility regular expressions
rx_h_or_li = re.compile(r"^(#{1,6}|\*|-)\s+")
rx_li = re.compile(r"^(\*|-)\s+")

def md2html(md_str):
    '''Converts GitHub-style markdown into HTML code

    Supported markdown:
    * headers
    * links
    * lists
    * bold and italic (incl. inline)

        Parameters:
            md_str (str): A string containing markdown

        Returns:
            md2html (str): A string containing HTML code
'''
    # If the string is empty, return an empty string
    if md_str is None or md_str == "":
        return ""

    # Result variable
    out_html = ""

    # Helper variables
    paragraph_opened = False
    list_opened = False
    prev_line = None

    # Check code line by line
    lines = md_str.split("\n")

    for line in lines:

        # Save initial line for lookback purposes
        initial_line = line

        # If this line is a header or a list item
        # and a paragraph is open, then close the paragraph
        if line != "" and rx_h_or_li.search(line) is not None:
            if paragraph_opened:
                out_html += "</p>\n"
                paragraph_opened = False

        else:
            # If this line is empty
            # and a paragraph is open, then close the paragraph,
            # save the initial line as previous,
            # and skip processing
            if line == "" and paragraph_opened:
                out_html += "</p>\n"
                paragraph_opened = False
                prev_line = initial_line
                continue
            
            # If it is not a list item, but previous line is,
            # then close the marked list
            elif prev_line is not None \
                and len(prev_line) > 0 \
                and rx_li.search(prev_line) is not None \
                and list_opened:

                line += "</ul>"
                list_opened = False

            # If this line is neither a header, nor a list,
            # and it is the first line or follows an empty line,
            # then start a paragraph 
            if line != "" and (prev_line is None or prev_line == ""):
                out_html += '<p dir="auto">\n'
                paragraph_opened = True

        # Check the line for markdown
        for tag in tag_map:
            rxs = tag_map[tag]

            # Loop through all markdown variants for a tag
            for rx in rxs:
                found = False
                matches = rx.findall(line)

                for match in matches:
                    # Inner text
                    text = ""
                    # Text with markdown
                    text_to_replace = ""

                    if len(match) > 0:
                        found = True

                        # Type check is left for compatibility reasons.
                        # Patterns implemented by 2022-03-12 return tuples
                        if type(match) is str:
                            text = match

                        else:
                            # Save text with markdown
                            text_to_replace = match[0]
                            for result in match:
                                if result != "" and result != text_to_replace:
                                    # Save inner text
                                    text = result

                        # Decide on closing tag
                        closing_tag = ""
                        # *** must be checked individually
                        if tag == "<strong><em>":
                            closing_tag = "</em></strong>"
                        else:
                            closing_tag = tag.replace("<", "</")

                        # Process individual tags that need attention

                        # Link has 3 groups: markdown, link text and link URL
                        if tag == "<a>":
                            line = line.replace(text_to_replace, f'<a href="{match[2]}">{match[1]}{closing_tag}')
                        else:
                            # Use the same template for all other tags
                            line = line.replace(text_to_replace, f"{tag}{text}{closing_tag}")
                            
                            # Open a marked list, if this line is a first list item
                            if tag == "<li>":
                                if not list_opened:
                                    list_opened = True
                                    line = f'<ul dir="auto">\n{line}'
                        #end for

        # Save the initial line state as previous
        prev_line = initial_line
        # Append the processed line
        out_html += line + "\n"

    # Close a paragraph or a list if opened (e.g. at EOF)
    if paragraph_opened:
        out_html += "</p>"
    elif list_opened:
        out_html += "</ul>"

    return out_html

# ============================================================================
# Test code

if __name__ == '__main__':

    s = """# Block **with _inline_ spans**

#Not a header
-Not a list item

Paragraph with [GitHub Pages link](https://pages.github.com/).
The same paragraph with ***bold and italic***, **bold with inline _italic_** and *italic with inline __bold__*.

* item 1
* item 2

Last paragraph"""

    # s = "Single line *with markdown*"

    # s = ""

    print(md2html(s))
    # print(md2html.__doc__)
