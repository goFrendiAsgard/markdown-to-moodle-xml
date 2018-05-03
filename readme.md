# Markdown to Moodle XML 

## What is this?

Tool to convert this:

```markdown
# Test 1

* What is the color of the sky?
    - red
    - green
    - blue 
    - yellow

* Which ones are programmer's text editor?
    - sublime text 
    - vim 
    - atom 
    - microsoft word

# Test 2

* Who is the main protagonist in Dragon Ball?
    - Son Goku 
    - Picolo
    - Son Gohan
    - Vegeta

* Look at this code:
`` ```javascript
var a = 5
let b = 6
const c = 7
``  ```
Which one is immutable?
    - a
    - b
    - c 

* What is this?
    ![turtle](turtle.png)
    - A turtle 
    - A bird

* How do you spell $\alpha + \beta$?
    - a plus b
    - alpha plus beta
    - a fish and a funny flag
```

into this:
```xml
<?xml version="1.0" ?><quiz><question type="multichoice"><name><text>15f6bfae9c738eb5d5a625137c68f9d97217c9837bcef14f390b01f7</text></name><questiontext format="html"><text><![CDATA[What is the color of the sky?]]></text></questiontext><answer fraction="0"><text>red</text></answer><answer fraction="0"><text>green</text></answer><answer fraction="100.0"><text>blue</text></answer><answer fraction="0"><text>yellow</text></answer><shuffleanswers>1</shuffleanswers><single>true<answernumbering>abc</answernumbering></question><question type="multichoice"><name><text>1eb06c0febabb0ca206aa732e0bb607e50467a84209bf89b311afe3a</text></name><questiontext format="html"><text><![CDATA[Which ones are programmer's text editor?]]></text></questiontext><answer fraction="33.33"><text>sublime text</text></answer><answer fraction="33.33"><text>vim</text></answer><answer fraction="33.33"><text>atom</text></answer><answer fraction="0"><text>microsoft word</text></answer><shuffleanswers>1</shuffleanswers>false</single><answernumbering>abc</answernumbering></question></quiz>
```
and this:
```xml
<?xml version="1.0" ?><quiz><question type="multichoice"><name><text>85de507bd37c9dce0bac518e16fd8fa5b55cff8861fb49ec57f133cd</text></name><questiontext format="html"><text><![CDATA[Who is the main protagonist in Dragon Ball?]]></text></questiontext><answer fraction="100.0"><text>Son Goku</text></answer><answer fraction="0"><text>Picolo</text></answer><answer fraction="0"><text>Son Gohan</text></answer><answer fraction="0"><text>Vegeta</text></answer><shuffleanswers>1</shuffleanswers><single>true<answernumbering>abc</answernumbering></question><question type="multichoice"><name><text>6761a53fa753fbc447640804062afb329b98e9931e825ae0914255dd</text></name><questiontext format="html"><text><![CDATA[Look at this code:<pre>var a = 5
let b = 6
const c = 7
</pre>Which one is immutable?
]]></text></questiontext><answer fraction="0"><text>a</text></answer><answer fraction="0"><text>b</text></answer><answer fraction="100.0"><text>c</text></answer><shuffleanswers>1</shuffleanswers><single>true<answernumbering>abc</answernumbering></question></quiz>
```

## Why?

* Because writing quizes in `markdown` format is more pleasant than write it in `ms-office`, `libre-office` or `GIFT format`.
* You can transform `markdown` file into `pdf` by using `pandoc`: `pandoc -f markdown  -o example.pdf example.md`
* Because our live is too short to copy-pasting the quizes into moodle
* Because sometimes `macro` doesn't work

## How to use?

Simply cast: `python m2m.py <your-md-file>`

## Can I try it?

Sure, cast this: `python m2m.py example.md`

New files will be created: `example.md-Test 1.xml` and `example.md-Test 2.xml`

## Is there anything special with the markdown file?

Yes.

* First, I treat `# section` as beginning of new section, because sometimes I write a quizes for different subjects in a single file.
* Second, I treat `* question` as question. A question can contains multi-line string
* Third, I treat ` - answer` as wrong answer and ` - answer<space>` as correct answer. The correct answer has extra space behind. An answer only contains single line
* Any line preceeded by triple backtick will be converted to `<pre>` or `</pre>`
* Any `![]()` will be converted into `<img src="data:image/png,base64,..."/>`
* Any `$latex$` or `$$latex$$` will be converted into `\(\)`

## Is there anything wrong with the convertion?

Yes, any link, bold and italic format, and everything else aside from the ones I mention in the previous section.

## Prerequisites

* Python
* Human, non-muggle

# Bonus: Web App

I also make a web page so that you can write your markdown in the web and convert it into `pdf`, `doc`, and `moodle xml` at once.

## Prerequisites

* Flask `pip install Flask`
* pypandoc `pip install pypandoc`

## Run the server

`python web.py`

## Access the page

`http://localhost:5000`
