import os
import shutil
import random
import string
import pypandoc
import json
import zipfile
from flask import Flask, request, render_template, make_response
from m2m import md_to_xml_string
app = Flask(__name__)


def create_random_string(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/convert', methods=['POST'])
def convert():
    md = request.form['md']
    # prepare directory_name
    random_string = create_random_string(10)
    directory_name = 'result/' + random_string + '/'
    zip_file_name = 'result/' + random_string + '.zip'
    create_directory_if_not_exists(directory_name)
    zf = zipfile.ZipFile(zip_file_name, mode='w')
    # write markdown
    src_file_name = directory_name + '_document.md'
    doc_file_name = directory_name + '_document.docx'
    pdf_file_name = directory_name + '_document.pdf'
    f = open(src_file_name, 'w')
    f.write(md)
    f.close()
    # generate doc
    pypandoc.convert_file(src_file_name, 'docx', outputfile=doc_file_name)
    zf.write(doc_file_name)
    pypandoc.convert_file(src_file_name, 'pdf', outputfile=pdf_file_name)
    zf.write(pdf_file_name)
    # generate xml
    xml_dictionary = json.loads(md_to_xml_string(md))
    for test_name in xml_dictionary:
        test = xml_dictionary[test_name]
        xml_file_name = directory_name + test_name.strip() + '.xml'
        f = open(xml_file_name, 'w')
        f.write(test)
        f.close()
        zf.write(xml_file_name)
    # zip it
    zf.close()
    with open(zip_file_name) as f:
        file_content = f.read()
    response = make_response(file_content, 200)
    response.headers['Content-type'] = 'application/zip'
    os.remove(zip_file_name)
    shutil.rmtree(directory_name)
    return response


if __name__ == '__main__':
    app.run()
