import subprocess, sys, os, tempfile
import pandoc

########
# Pandoc External

def run(*command):
    return subprocess.run(command,capture_output=True,encoding='utf-8')

def run_and_get_lines(*command):
    completed_process = run(*command)
    return completed_process.stdout.split("\n")

def run_and_test_success(*command):
    completed_process = run(*command)
    return completed_process.returncode == 0


def assert_tool(command):
    """ function decorator
    fails if a function is called using an unavailable command"""

    def tool_not_found_function(*args,**kwargs):
        print(f'tool {name} not found using `which` - assuming no installation',
                file=sys.stderr)
        raise AssertionError(name)

    def function_identity_or_assertion_error(function):
        if not run_and_test_success('which',name):
            return tool_not_found_function
        return function
    
    return function_identity_or_assertion_error


def pandoc_default(doctype,tempdir):
    if not doctype in "docx pptx".split():
        return run_and_get_lines("pandoc","-D",doctype)
    else:
        # TODO capture output file
        return ...

# pandoc --reference-doc=REFERENCE_PATH -o OUTFILE INFILE


####
# Pandoc lib


#pd_formats = "latex pptx docx revealjs html pdf markdown".split()
pd_formats = "latex docx pptx markdown".split()

document_raw="""
# Hello World

## Subheading

$\sum\limits_{i=1}^{\infty} \\frac{1}{x^2}$

Text

- List
- More lists
"""

refdoc = lambda doc: [f"--reference-doc=templates/{doc}"]
tpldoc = lambda doc: [f"--template=templates/{doc}"]

template_option_dict = {
        "docx":refdoc("custom-reference.docx"),
        "pptx":refdoc("custom-reference.pptx"),
        "latex":tpldoc("latex_template_1.latex"),
        "markdown":[],
        }

def source(doc, doctype):
    assert(doctype in pd_formats)
    return pandoc.read(doc,format=doctype)

def target(doc, doctype):
    assert(doctype in pd_formats)
    #if doctype in template_option_dict:
    return pandoc.write(doc,format=doctype,options=template_option_dict[doctype])
    #return pandoc.write(doc, format=doctype)

def parse_exercise_tree(exercise_tree):
    markdown_doc = ""
    for node in exercise_tree:
        if isinstance(node,list):
            markdown_doc += parse_exercise_tree(node)
        else:
            markdown_doc += node.text
        markdown_doc += "\n\n"
    return markdown_doc


def exercise_as_file(exercise,tempdir,doctype):
    filename = tempdir+"tempfile.pdf"
    markdown_doc = parse_exercise_tree(exercise)
    try:
        pandoc_data = pandoc.read(markdown_doc,format="markdown")
    except Exception as e:
        err= "Error on document parsing:"+str(e)
        print(err)
        return err
    try:
        target_doc = pandoc.write(pandoc_data,format="pdf")
    except Exception as e:
        err = "Error on document writing:"+str(e)
        print(err)
        return err

    return target_doc



