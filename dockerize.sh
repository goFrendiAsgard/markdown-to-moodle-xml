set -e
docker build . -t gofrendi/markdown-to-moodle
docker start --name markdown-to-moodle -p 5000:5000 -d gofrendi/markdown-to-moodle
docker push gofrendi/markdown-to-moodle