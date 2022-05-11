from pylatex import Document, Itemize, Package, NoEscape, Command
from pylatex.base_classes import Environment, Arguments


class UASTemplate(Document):

    def __init__(self):
        super().__init__(documentclass='beamer', document_options=['english', 'hangout'], fontenc='T1', inputenc='utf8')

        self.packages.append(Package('rotating'))
        self.packages.append(Package('verbatim'))
        self.packages.append(Package('latexsym'))
        self.packages.append(Package('graphicx'))
        self.packages.append(Package('tabularx'))
        self.packages.append(Package('ragged2e'))
        self.packages.append(Package('eurosym'))
        self.packages.append(Package('listings'))
        self.packages.append(Package('multirow'))
        self.packages.append(Package('colortbl'))
        self.packages.append(Package('textcomp'))
        self.packages.append(Package('lmodern'))
        self.packages.append(Package('times'))
        self.packages.append(Package('babel', options=['english']))
        self.packages.append(Package('booktabs'))

        self.preamble.append(NoEscape(r'\usetheme[fb2]{FrankfurtUniversity}'))


class Slide(Environment):
    _latex_name = 'frame'

    def dumps(self):
        s = super().dumps()
        return s + '\n'


class TitledSlide(Slide):
    def __init__(self, title, subtitle=None, options=None, arguments=None, start_arguments=None, **kwargs):
        super().__init__(options=options, arguments=arguments, start_arguments=start_arguments, **kwargs)

        self._title = title
        self._subtitle = subtitle

    def dumps(self):
        """Represent the environment as a string in LaTeX syntax.
        Returns
        -------
        str
            A LaTeX string representing the environment.
        """

        content = self.dumps_content()
        if not content.strip() and self.omit_if_empty:
            return ''

        string = ''

        # Something other than None needs to be used as extra arguments, that
        # way the options end up behind the latex_name argument.
        if self.arguments is None:
            extra_arguments = Arguments()
        else:
            extra_arguments = self.arguments

        begin = Command('begin', self.start_arguments, self.options,
                        extra_arguments=extra_arguments)
        begin.arguments._positional_args.insert(0, self.latex_name)
        string += begin.dumps() + self.content_separator

        string += Command('frametitle', self._title).dumps()
        if self._subtitle is not None:
            string += Command('framesubtitle', self._subtitle).dumps()

        string += content + self.content_separator

        string += Command('end', self.latex_name).dumps()

        return string + '\n'


def create_example():
    doc = UASTemplate()

    doc.preamble.append(Command('title', 'Example Slide Set'))
    doc.preamble.append(Command('subtitle', NoEscape(r'\LaTeX\ beamer theme “FrankfurtUniversity”')))
    doc.preamble.append(Command('author', NoEscape('Prof.~Dr.~Eicke Godehardt')))
    doc.preamble.append(Command('institute', NoEscape(r'Frankfurt University of Applied Sciences\\Faculty of Computer Science and Engineering\\ \texttt{godehardt@fb2.fra-uas.de}')))
    doc.preamble.append(Command('date', NoEscape(r'\today')))

    with doc.create(Slide()):
        doc.append(NoEscape(r'\titlepage'))

    with doc.create(Slide()):
        doc.append(Command('vspace', '1.4cm'))
        doc.append(Command('center', NoEscape(r"""\huge\makebox[0pt]{\smash{\fontfamily{ptm}\fontsize{190}{0}\selectfont
        \color{lightgray}\raisebox{-.5em}[0pt][0pt]{\,'\!'}}}
        If you are not prepared to be wrong, you never come up with anything original.""")))
        doc.append(Command('raggedleft'))
        doc.append("Sir Ken Robinson")

    with doc.create(TitledSlide('Agenda')):
        doc.append(Command('tableofcontents'))

    with doc.create(TitledSlide('Example of Normal Slide', subtitle='Subtitle')):
        doc.append("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                   "Etiam sit amet vulputate ante, vel laoreet erat. C"
                   "ras pulvinar, sem nec lobortis vehicula,leo dolor commodo.")

        with doc.create(Itemize()) as itemize:
            itemize.add_item("Item 1")
            itemize.add_item("Item 2:")
            with doc.create(Itemize()) as itemize2:
                itemize2.add_item("Subitem 2.1")
                itemize2.add_item(Command('dots'))

    doc.generate_tex('example')
