import os
import shutil
import random
import pypandoc
import json
import zipfile
from flask import Flask, request, render_template, make_response, send_from_directory
from m2m import md_to_xml_string
app = Flask(__name__)


def create_random_string(length):
    lowercase = 'abcdefghijklmnopqrtuvwxyz'
    return ''.join(random.choice(lowercase) for i in range(length))


def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_doc_and_pdf(src_file_name, doc_file_name, pdf_file_name, zf):
    # generate doc
    try:
        pypandoc.convert_file(src_file_name, 'docx', outputfile=doc_file_name)
        zf.write(doc_file_name)
    except Exception as error:
        print(error)
    try:
        pypandoc.convert_file(src_file_name, 'pdf', outputfile=pdf_file_name)
        zf.write(pdf_file_name)
    except Exception as error:
        print(error)


def create_md(src_file_name, md, zf):
    f = open(src_file_name, 'w')
    f.write(md)
    f.close()
    zf.write(src_file_name)


def create_all_doc_and_pdf(directory_name, t_md, s_md, zf):
    # define teacher and student file name
    t_src_file_name = directory_name + '_teacher.md'
    t_doc_file_name = directory_name + '_teacher.docx'
    t_pdf_file_name = directory_name + '_teacher.pdf'
    s_src_file_name = directory_name + '_student.md'
    s_doc_file_name = directory_name + '_student.docx'
    s_pdf_file_name = directory_name + '_student.pdf'
    # write teacher's files
    create_md(t_src_file_name, t_md, zf)
    create_doc_and_pdf(t_src_file_name, t_doc_file_name, t_pdf_file_name, zf)
    # write student's files
    create_md(s_src_file_name, s_md, zf)
    create_doc_and_pdf(s_src_file_name, s_doc_file_name, s_pdf_file_name, zf)


def create_xml(directory_name, s_md, zf):
    # generate xml
    xml_dictionary = json.loads(md_to_xml_string(s_md))
    for test_name in xml_dictionary:
        test = xml_dictionary[test_name]
        xml_file_name = directory_name + test_name.strip() + '.xml'
        f = open(xml_file_name, 'w')
        f.write(test)
        f.close()
        zf.write(xml_file_name)


def get_s_md(t_md):
    s_md = ''
    for md_row in t_md.split('\n'):
        md_row = md_row.rstrip()
        if md_row[-10:] == ' (correct)':
            md_row = md_row[:-10] + ' '
        elif md_row[-6:] == ' (ans)':
            md_row = md_row[:-6] + ' '
        s_md += md_row + '\n'
    return s_md


@app.route('/statics/<path:path>')
def serve_static(path):
    return send_from_directory('statics', path)


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/convert', methods=['POST'])
def convert():
    t_md = request.form['md']
    s_md = get_s_md(t_md)
    # prepare directory_name
    random_string = create_random_string(5)
    directory_name = 'result/' + random_string + '/'
    zip_file_name = 'result/' + random_string + '.zip'
    create_directory_if_not_exists(directory_name)
    zf = zipfile.ZipFile(zip_file_name, mode='w')
    # create doc and pdf for teacher and student
    create_all_doc_and_pdf(directory_name, t_md, s_md, zf)
    create_xml(directory_name, s_md, zf)
    # zip it
    zf.close()
    f = open(zip_file_name, 'rb')
    file_content = f.read()
    response = make_response(file_content, 200)
    response.headers['Content-type'] = 'application/zip'
    os.remove(zip_file_name)
    shutil.rmtree(directory_name)
    return response


if __name__ == '__main__':
    app.run()
