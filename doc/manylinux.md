source https://gmagno.dev/2019/01/building-python-wheels-for-many-linux-es/


.travis.yml file
```yml
notifications:
  email: false
if: tag IS present
matrix:
  include:
  - sudo: required
    services:
      - docker
    env:
      - DOCKER_IMAGE=quay.io/pypa/manylinux1_x86_64
  - sudo: required
    services:
      - docker
    env:
      - DOCKER_IMAGE=quay.io/pypa/manylinux1_i686
      - PRE_CMD=linux32
install:
  - docker pull $DOCKER_IMAGE
script:
  - docker run --rm -v `pwd`:/io -e TWINE_USERNAME -e TWINE_PASSWORD $DOCKER_IMAGE $PRE_CMD /io/travis/build-wheels.sh
  - ls wheelhouse/
```


added build_wheel.sh to etc/build_wheel.sh
```
#!/bin/bash
set -e -x

export PYHOME=/home
cd ${PYHOME}

/opt/python/cp37-cp37m/bin/pip install twine cmake
ln -s /opt/python/cp37-cp37m/bin/cmake /usr/bin/cmake

# Compile wheels
for PYBIN in /opt/python/cp3*/bin; do
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
    "${PYBIN}/python" /io/setup.py sdist -d /io/wheelhouse/
done

# Bundle external shared libraries into the wheels and fix naming
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Test
for PYBIN in /opt/python/cp3*/bin/; do
    "${PYBIN}/pip" install -r /io/requirements-test.txt
    "${PYBIN}/pip" install --no-index -f /io/wheelhouse nb-cpp
    (cd "$PYHOME"; "${PYBIN}/pytest" /io/test/)
done

#  Upload
for WHEEL in /io/wheelhouse/nb_cpp*; do
    /opt/python/cp37-cp37m/bin/twine upload \
        --skip-existing \
        -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
        "${WHEEL}"
done
```


log
```
podman pull quay.io/pypa/manylinux1_x86_64:latest

# check it
# podman run -it --name mlinux quay.io/pypa/manylinux1_x86_64:latest  # initial test

# run interactively with mounted directoyr of the root of the source distribution
podman run -it --rm -v `pwd`:/io --name mlinux2 quay.io/pypa/manylinux1_x86_64:latest
# --inside 
/usr/bin/yum install libffi-dev   # this allows to compile cffi package

#!! that did not work
# try the debian based container
# manylinux_2_24 (Debian 9 based)
# x86_64 image: quay.io/pypa/manylinux_2_24_x86_64
podman pull quay.io/pypa/manylinux_2_24_x86_64

podman run -it --rm -v `pwd`:/io quay.io/pypa/manylinux_2_24_x86_64:latest

# now inside container, get rid of python 3.6 and 3.11 and install libffi-dev
rm -rf cp36-cp36m; rm -rf cp311-cp311; apt-get update; apt-get install libffi-dev
# success!

/io/etc/build_wheels.sh
...
No module named 'Cython'

```
