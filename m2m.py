import os
import sys
import re
import hashlib
import random
import json
import base64
import urllib

NEW_LINE = '\n'
HEADER_PATTERN = re.compile(r'^# (.*)$')
QUESTION_PATTERN = re.compile(r'^(\s*)\*(\s)(.*)$')
CORRECT_ANSWER_PATTERN = re.compile(r'^(\s*)-(\s)(.*)\s$')
WRONG_ANSWER_PATTERN = re.compile(r'^(\s*)-(\s)(.*[^\s])$')
SWITCH_PRE_TAG_PATTERN = re.compile(r'^```.*$')
EMPTY_LINE_PATTERN = re.compile(r'^\s*$')
IMAGE_PATTERN = re.compile(r'!\[.*\]\((.+)\)')
MULTI_LINE_CODE_PATTERN = re.compile(r'```.*\n([\s\S]+)```', re.MULTILINE)
SINGLE_LINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
SINGLE_DOLLAR_LATEX_PATTERN = re.compile(r'\$(.+)\$')
DOUBLE_DOLLAR_LATEX_PATTERN = re.compile(r'\$\$(.+)\$\$')


def get_header(string):
    match = re.match(HEADER_PATTERN, string)
    if match:
        return match.group(1)
    return None


def get_question(string):
    match = re.match(QUESTION_PATTERN, string)
    if match:
        return match.group(3)
    return None


def get_correct_answer(string):
    match = re.match(CORRECT_ANSWER_PATTERN, string)
    if match:
        return match.group(3)
    return None


def get_wrong_answer(string):
    match = re.match(WRONG_ANSWER_PATTERN, string)
    if match:
        return match.group(3)
    return None


def is_header(string):
    return False if get_header(string) is None else True


def is_question(string):
    return False if get_question(string) is None else True


def is_correct_answer(string):
    return False if get_correct_answer(string) is None else True


def is_wrong_answer(string):
    return False if get_wrong_answer(string) is None else True


def md_script_to_dictionary(md_script):
    dictionary = {}
    section, current_question, current_answer = ([], {}, {})
    for md_row in md_script.split(NEW_LINE):
        if is_header(md_row):
            section = []
            dictionary[get_header(md_row)] = section
        elif is_question(md_row):
            current_question = {'text': get_question(md_row), 'answers': []}
            section.append(current_question)
        elif is_correct_answer(md_row):
            current_answer = {
                'text': get_correct_answer(md_row),
                'correct': True}
            current_question['answers'].append(current_answer)
        elif is_wrong_answer(md_row):
            current_answer = {
                'text': get_wrong_answer(md_row),
                'correct': False}
            current_question['answers'].append(current_answer)
        elif not re.match(EMPTY_LINE_PATTERN, md_row):
            current_question['text'] += md_row + '\n'
    dictionary = completing_dictionary(dictionary)
    return dictionary


def completing_dictionary(dictionary):
    for key in dictionary:
        section = dictionary[key]
        for question in section:
            correct_answers = [x for x in question['answers'] if x['correct']]
            correct_answer_count = len(correct_answers)
            if correct_answer_count < 1:
                correct_answer_count = 1
            question['single'] = correct_answer_count == 1
            weight = round(100.0 / correct_answer_count, 7)
            for answer in question['answers']:
                if answer['correct']:
                    answer['weight'] = weight
                else:
                    answer['weight'] = 0
    return dictionary


def section_to_xml(section, md_dir_path):
    xml = '<?xml version="1.0" ?><quiz>'
    for index, question in enumerate(section):
        xml += question_to_xml(question, index, md_dir_path)
    xml += '</quiz>'
    return xml


def question_to_xml(question, index, md_dir_path):
    rendered_question_text = render_text(question['text'], md_dir_path)
    index_part = str(index + 1).rjust(4, '0')
    q_part = (question['text'] + str(random.random())).encode('utf-8')
    question_single_status = ('true' if question['single'] else 'false')
    xml = '<question type="multichoice">'
    # question name
    xml += '<name><text>'
    xml += index_part + hashlib.sha224(q_part.encode('utf-8')).hexdigest()
    xml += '</text></name>'
    # question text
    xml += '<questiontext format="html"><text><![CDATA['
    xml += rendered_question_text
    xml += ']]></text></questiontext>'
    # answer
    for answer in question['answers']:
        xml += answer_to_xml(answer)
    # other properties
    xml += '<shuffleanswers>1</shuffleanswers>'
    xml += '<single>' + question_single_status + '</single>'
    xml += '<answernumbering>abc</answernumbering>'
    xml += '</question>'
    return xml


def answer_to_xml(answer):
    xml = '<answer fraction="'+str(answer['weight'])+'">'
    xml += '<text>'+answer['text']+'</text>'
    xml += '</answer>'
    return xml


def render_text(text, md_dir_path):
    text = re.sub(MULTI_LINE_CODE_PATTERN, replace_multi_line_code, text)
    text = re.sub(SINGLE_LINE_CODE_PATTERN, replace_single_line_code, text)
    text = re.sub(IMAGE_PATTERN, replace_image_wrapper(md_dir_path), text)
    text = re.sub(DOUBLE_DOLLAR_LATEX_PATTERN, replace_latex, text)
    text = re.sub(SINGLE_DOLLAR_LATEX_PATTERN, replace_latex, text)
    return text


def replace_latex(match):
    code = match.group(1)
    return '\\(' + code + '\\)'


def replace_single_line_code(match):
    code = match.group(1)
    return '<pre style="display:inline-block;"><code>' + code + '</code></pre>'


def replace_multi_line_code(match):
    code = match.group(1)
    return '<pre><code>' + code + '</code></pre>'


def replace_image_wrapper(md_dir_path):
    def replace_image(match):
        file_name = match.group(1)
        if (not os.path.isabs(file_name)) and ('://' not in file_name):
            file_name = os.path.join(md_dir_path, file_name)
        return build_image_tag(file_name)
    return replace_image


def build_image_tag(file_name):
    extension = file_name.split('.')[-1]
    data = urllib.urlopen(file_name).read()
    base64_image = str(base64.b64encode(data))
    src_part = 'data:image/' + extension + ';base64,' + base64_image
    return '<img style="display:block;" src="' + src_part + '" />'


def md_to_xml_file(md_file_name):
    md_dir_path = os.path.dirname(os.path.abspath(md_file_name))
    md_file = open(md_file_name, 'r')
    md_script = md_file.read()
    dictionary = md_script_to_dictionary(md_script)
    for section_caption in dictionary:
        section = dictionary[section_caption]
        xml_file = open(md_file_name+'-'+section_caption+'.xml', 'w')
        xml_file.write(section_to_xml(section, md_dir_path))
    return dictionary


def md_to_xml_string(md_script):
    md_dir_path = os.getcwd()
    result = {}
    dictionary = md_script_to_dictionary(md_script)
    for section_caption in dictionary:
        section = dictionary[section_caption]
        result[section_caption] = section_to_xml(section, md_dir_path)
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    try:
        md_file_name = sys.argv[1]
        md_file = open(md_file_name, 'r')
        md_to_xml_file(md_file_name)
    except Exception:
        md_script = sys.argv[1]
        print(md_to_xml_string(md_script))
