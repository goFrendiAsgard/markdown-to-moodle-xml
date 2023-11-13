FROM python:3.10.0

RUN apt-get update --fix-missing
RUN apt-get install -y texlive-full texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra

COPY . .

RUN pip install -r requirements.txt

CMD python app.py