set -e
docker build . -t gofrendi/markdown-to-moodle
docker run gofrendi/markdown-to-moodle -p 5000:5000 -d
docker push gofrendi/markdown-to-moodle