import pandoc

from ..models import Exercise, Answer

_pdf_base = r"""
\documentclass[a4paper]{scrartcl}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage[utf8]{inputenc}
\title{\textbf{TITLE}}
\subtitle{SUBTITLE}
\begin{document}
CONTENT
\end{document}
"""

_beamer_base = r"""
\documentclass{beamer}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage[utf8]{inputenc}
%\usetheme[fb2]{FrankfurtUniversity}
\title{TITLE}
\begin{document}
CONTENT
\end{document}
"""

_beamer_slide = r"""
\begin{frame}{TITLE}
CONTENT
\end{frame}
"""

_options_default = {
        "enumeration":True,
        "enumeration_lvl":[
            "number-brace",
            "alpha-brace",
            "roman-brace",
        ],
        "beamer":False,
        "title":True,
        }


def enumeration_sign(number,enumeration_type):
    def substitution(foo):
        if foo == "number":
            return str(number+1)
        if foo == "alpha":
            return chr(ord('a')+number)
        if foo == "brace":
            return ")"
        else:
            return str(number+1)
    return "".join(substitution(t) for t in enumeration_type.split("-"))

def flatten_exercise_tree(node,depth=0,number=0):
    if isinstance(node,list):
        return [x for n in node for x in flatten_exercise_tree(n,depth+1)]
    else:
        return [(depth,node)]

def enumerate_flatlist(flatlist):
    l = []
    d_old = -1
    numbers = []
    for d, e in flatlist:
        if d_old < d:   numbers.append(0)
        elif d_old > d: numbers.pop()
        else:           numbers[-1] += 1
        d_old = d
        l.append( (d,e,numbers[-1]) )
    return l

def internal_format_to_pandoc_format(f: str) -> str:
    f = f.lower()
    if f == "plain":
        return "rtf"
    return f

def exercise_fragment(depth, exercise, number, options=None):
    if options is None:
        options = _options_default
    doc_format = internal_format_to_pandoc_format(exercise.text_type)
    exercise_pandoc = pandoc.read(exercise.text, format=doc_format)
    exercise_latex = pandoc.write(exercise_pandoc,format="latex")

    section_header = r"\DEPTHsection*{TITLE}"
    section_header = section_header.replace("DEPTH","sub"*min((depth-1),2))
    #section_header = section_header.replace("NONUMBER","*" if options.get("nonumber",False) else "")
    title = exercise.title if options.get("title",True) else ""
    if options.get("enumeration",True) or True:
        etype = options.get("enumeration_lvl",_options_default["enumeration_lvl"])[depth-1]
        title = enumeration_sign(number, etype) + " " + title

    section_header = section_header.replace("TITLE",title)

    images = list(exercise.pictures.iterator())
    if images:
        for image in images:
            exercise_latex += f"\\\\\includegraphics[width=\\textwidth]{{{image.image.path}}}\n"

    content = section_header + "\n" + exercise_latex

    #print(content)
    return  content

def answers_fragment(depth, fragment, number, options = None):
    if options is None:
        options = _options_default
    doc_format = internal_format_to_pandoc_format(fragment.text_type)
    fragment_pandoc = pandoc.read(fragment.text, format=doc_format)
    fragment_latex = pandoc.write(fragment_pandoc,format="latex")

    section_header = r"\section*{Answer}"

    for image in fragment.pictures.iterator():
        fragment_latex += f"\\\\\includegraphics{{{image.image.path}}}\n"

    content = section_header + "\n" + fragment_latex

    #print(content)
    return  content

    pass


def fragment(depth, fragment, number, options = None):
    if isinstance(fragment, Exercise):
        return exercise_fragment(depth, fragment, number, options)
    if isinstance(fragment, Answer):
        return answers_fragment(depth, fragment, number, options)
    print("HELP\n"*10)
    breakpoint()



def latex_from_fragments(fragment_collection, options={}):
    print(f"{options=}")
    flatlist = flatten_exercise_tree(fragment_collection.tree)
    flatlist = enumerate_flatlist(flatlist)

    content = [fragment(*x, options) for x in flatlist]
    title = fragment_collection.title
    
    base = _pdf_base if not options.get("subtype","") == "beamer" else _beamer_base
    tex_document = base.replace("CONTENT","\n".join(content)).replace("TITLE",title,1)
    print("---LaTeX---")
    print(tex_document)
    print("---LaTeX---")
    return tex_document






