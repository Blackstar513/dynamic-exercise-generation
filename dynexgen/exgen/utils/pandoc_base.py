import subprocess, sys, os, tempfile
from traceback import print_exception
from contextlib import contextmanager

import pandoc
#from .pandoc_exercise_composer import parse_exercise_tree

from tempfile import TemporaryDirectory

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
        raise AssertionError(command)

    def function_identity_or_assertion_error(function):
        if not run_and_test_success('which',command):
            return tool_not_found_function
        return function
    
    return function_identity_or_assertion_error


@assert_tool("pandoc")
def pandoc_default(doctype,tempdir):
    if not doctype in "docx pptx".split():
        return run_and_get_lines("pandoc","-D",doctype)
    else:
        # TODO capture output file
        return ...

@contextmanager
def cd_tmpdir():
    owd = os.getcwd()
    try:
        with TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            yield tmpdir
    finally:
        os.chdir(owd)

@assert_tool("pdflatex")
def pdflatex_convert(infile_data):
    with cd_tmpdir() as tmpdir:
        with open("tmp.tex",'w+') as f:
            f.write(infile_data)
        command_output = run_and_get_lines(
            "pdflatex","-interaction=nonstopmode","","tmp.tex"
            )
        #print("vvvv infile vvvv")
        #print(infile_data)
        #print("=== vv pdflatex vv ===")
        #print("\n".join(commandoutput))
        #print("=== ^^ pdflatex ^^ ===")
        #print(os.listdir())
        try:
            with open("texput.log") as f:
                print(f.read())
        except Exception as e:
            pass # I don't care. It's only relevant if it failed
        with open("tmp.pdf","rb") as f:
            return f.read()


# pandoc --reference-doc=REFERENCE_PATH -o OUTFILE INFILE


####
# Pandoc lib


#pd_formats = "latex pptx docx revealjs html pdf markdown".split()
pd_formats = "latex docx pptx markdown".split()

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
    #return pandoc.write(doc,format=doctype,options=template_option_dict[doctype])
    return pandoc.write(doc, format=doctype)

def document_from_latex(latex_infile, doctype):
    if doctype == "pdf":
        target_doc = pdflatex_convert(latex_infile)
    else:
        pandoc_document = pandoc.read(tex_document,format="latex")
        target_doc = pandoc.write(pandoc_data,format=doctype)
    return target_doc

