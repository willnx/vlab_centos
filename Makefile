clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rm `docker ps -a -q`
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel --universal

uninstall:
	-pip uninstall -y vlab-centos-api

install: uninstall build
	pip install -U dist/*.whl

test: uninstall install
	cd tests && nosetests -v --with-coverage --cover-package=vlab_centos_api

images: build
	docker build -f ApiDockerfile -t willnx/vlab-centos-api .
	docker build -f WorkerDockerfile -t willnx/vlab-centos-worker .

up:
	docker-compose -p vlabcentos up --abort-on-container-exit
