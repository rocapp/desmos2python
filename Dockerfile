FROM ubuntu:rolling as ubuntu
FROM python:3.10 as base

LABEL Author, Robert Ahlroth Capps

ENV PATH=${PATH}:/root/.local:/root/.local/bin

#: (pseudo)install package -> docker (move via bind)
COPY . .
COPY dist/* ${APP_HOME}/
COPY desmos2python.egg-info ${APP_HOME}

# install all requirements, then install package locally
COPY requirements/* ${APP_HOME}/requirements/

#: cd -> pkg directory, then install requirements
WORKDIR ${APP_HOME}
RUN python3.10 -m pip install --upgrade pip
RUN python3.10 -m pip install --upgrade ipython
#: explicit cache dir
ENV PIP_CACHE_DIR=/root/.cache
RUN python3.10 -m pip install \
    --no-warn-script-location --user --upgrade \
    -r requirements/requirements.txt -r requirements/dev-requirements.txt \
    -r requirements/build-requirements.txt

#: ! explicitly set to --no-cache for installing the wheel
RUN python3.10 -m pip install --no-cache-dir --user --upgrade $(ls *.whl | head -1)
#: ! ensure resources are initialized properly
RUN python3.10 setup.py init_resources_d2p

# # # # # # #
#:  [test]  #
# # # # # # #

#: run tests
FROM base as test
ENV APP_HOME /desmos2python
ENV PATH=/root/local/bin:/root/.local:$PATH
COPY --from=base . ${APP_HOME}
WORKDIR ${APP_HOME}
RUN pytest

# # # # # # # #
#:  [latest]  #
# # # # # # # #

#: latest build
FROM base as latest
ENV APP_HOME /desmos2python
ENV PATH=/root/local/bin:/root/.local:$PATH
COPY --from=base . ${APP_HOME}
WORKDIR ${APP_HOME}

CMD ["/usr/bin/env", "bash", "-c", "ipython"]
