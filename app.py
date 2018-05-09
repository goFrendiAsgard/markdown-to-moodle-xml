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


@app.route('/statics/<path:path>')
def serve_static(path):
    return send_from_directory('statics', path)


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
    zf.write(src_file_name)
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
    f = open(zip_file_name, 'rb')
    file_content = f.read()
    response = make_response(file_content, 200)
    response.headers['Content-type'] = 'application/zip'
    os.remove(zip_file_name)
    shutil.rmtree(directory_name)
    return response


if __name__ == '__main__':
    app.run()
