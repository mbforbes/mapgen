"""
Generate the report
"""

# imports
# ---

# 3rd party
import markdown
from markdown.extensions.toc import TocExtension


# settings
# ---


class Settings:
    HEADER_PATH = 'html/header.html'
    FOOTER_PATH = 'html/footer.html'
    MD_PATH = 'report.md'
    OUT_PATH = 'report.html'

    MD_EXTENSIONS = [
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        TocExtension(baselevel=1, title='Table of Contents'),
    ]


# functions
# ---

def read(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


def write(path: str, contents: str) -> None:
    with open(path, 'w') as f:
        f.write(contents)


# main
# ---

def main():
    header = read(Settings.HEADER_PATH)
    footer = read(Settings.FOOTER_PATH)
    md = markdown.markdown(
        read(Settings.MD_PATH), extensions=Settings.MD_EXTENSIONS)

    write(Settings.OUT_PATH, '\n'.join([
        header,
        md,
        footer,
    ]))


if __name__ == '__main__':
    main()
