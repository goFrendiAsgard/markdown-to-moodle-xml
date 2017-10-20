import sys, re, math, hashlib, random, json

NEW_LINE = '\n'
HEADER_PATTERN = re.compile('^# (.*)$')
QUESTION_PATTERN = re.compile('^(\s*)\*(\s)(.*)$')
CORRECT_ANSWER_PATTERN = re.compile('^(\s*)-(\s)(.*)\s$')
WRONG_ANSWER_PATTERN = re.compile('^(\s*)-(\s)(.*[^\s])$')
SWITCH_PRE_TAG_PATTERN = re.compile('^```.*$')
EMPTY_LINE_PATTERN = re.compile('^\s*$')
IMAGE_PATTERN = re.compile('!\[.*\]\((.+)\)')

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
    is_inside_pre = False
    for md_row in md_script.split(NEW_LINE):
        if is_header(md_row):
            section = []
            dictionary[get_header(md_row)] = section
        elif is_question(md_row):
            current_question = {'text': get_question(md_row), 'answers': []}
            section.append(current_question)
        elif is_correct_answer(md_row):
            current_answer = {'text': get_correct_answer(md_row), 'correct': True}
            current_question['answers'].append(current_answer)
        elif is_wrong_answer(md_row):
            current_answer = {'text': get_wrong_answer(md_row), 'correct': False}
            current_question['answers'].append(current_answer)
        elif not re.match(EMPTY_LINE_PATTERN, md_row):
            # question can contains multi line and can contains code
            if re.match(SWITCH_PRE_TAG_PATTERN, md_row):
                is_inside_pre = not is_inside_pre
                current_question['text'] += '<pre>' if is_inside_pre else '</pre>'
            else:
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

def section_to_xml(section):
    xml = '<?xml version="1.0" ?><quiz>'
    for question in section:
        xml += question_to_xml(question)
    xml += '</quiz>'
    return xml

def question_to_xml(question):
    rendered_question_text = re.sub(IMAGE_PATTERN, md_match_to_image_tag, question['text'])
    xml = '<question type="multichoice">'
    # question name
    xml += '<name><text>'
    xml += hashlib.sha224(question['text'] + str(random.random())).hexdigest()
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
    xml += '<single>'+ ('true' if question['single'] else 'false') +'</single>'
    xml += '<answernumbering>abc</answernumbering>'
    xml += '</question>'
    return xml

def answer_to_xml(answer):
    xml = '<answer fraction="'+str(answer['weight'])+'">'
    xml += '<text>'+answer['text']+'</text>'
    xml += '</answer>'
    return xml

def md_match_to_image_tag(match):
    file_name = match.group(1)
    return build_image_tag(file_name)

def build_image_tag (file_name):
    base64_image = ''
    extension = file_name.split('.')[-1]
    with open(file_name, "rb") as f:
        data = f.read()
        base64_image += data.encode("base64")
    return '<img src="data:image/'+extension+';base64,'+base64_image+'" />'

if __name__ == '__main__':
    md_file_name = sys.argv[1]
    md_file = open(md_file_name, 'r')
    md_script = md_file.read()
    dictionary = md_script_to_dictionary(md_script)
    # create json file for `debugging` purpose
    json_file = open(md_file_name+'.json', 'w')
    json_file.write(json.dumps(dictionary))
    for section_caption in dictionary:
        section = dictionary[section_caption]
        xml_file = open(md_file_name+'-'+section_caption+'.xml', 'w')
        xml_file.write(section_to_xml(section))
