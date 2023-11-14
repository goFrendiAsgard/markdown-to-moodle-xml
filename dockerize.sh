set -e
docker build . -t gofrendi/markdown-to-moodle
docker run -d -p 5000:5000 --name markdown-to-moodle gofrendi/markdown-to-moodle
docker push gofrendi/markdown-to-moodle