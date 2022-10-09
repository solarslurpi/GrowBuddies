
# sphinxLearning

The documentation uses Sphinx.  I'm putting learnings on how to do non intuitive Sphinx things here.

## Autobuild
I tried using the [RST page preview](https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext) which was great until I switched to markdown.  With [Autobuild](https://github.com/executablebooks/sphinx-autobuild) I have a WYSIWYG environment which makes editing much more of a delight.  The Autobuild documentation is good enough to get going.  Here is the command to start autobuild going:
```console
 sphinx-autobuild docs docs/_build/html
```

The command assumes the md or rst files are in the docs file and the output is in docs/_build/html.


## Myst-parser

[Myst-parser](https://myst-parser.readthedocs.io/en/latest/) define a version of markdown that understands Sphinx's roles and directives.  I find markdown much simpler than restructured text.  I just thought restructured text was more powerful.

See [Geting Started with Myst](https://myst-parser.readthedocs.io/en/latest/intro.html)

### Extensions
Directives such as:
```
:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::
```
require extensions to markdown that the Myst parser will optionally handle if the extension is listed in `myst_enable_extensions` in `conf.py`.  To handle images and figures, add the following to conf.py:
```
myst_enable_extensions = ["colon_fence"]
```
Now we can include restructured text images/figures directives.

:::{figure} images/SnifferBuddy_wiring.jpg
:align: center
:scale: 100

SnifferBuddy Wiring
:::

### Example
In this example, we start with a file in rst format and convert to markdown.  To do this, we use the rst-to-myst[sphinx]
1. Install the library into your virtual environment `pip install rst-to-myst[sphinx]`
2. Convert the files.  I put snifferbuddy.rst into the rst-test-files folder to give us an example to work with. 
```
rst2myst convert ../rst-test-files/* .
```

## Link To Another Doc Page
To link to another doc page, use `{doc}`<pagename>` ` for example, {doc}`snifferbuddy`.
