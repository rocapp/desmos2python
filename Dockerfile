FROM ubuntu:rolling as base
LABEL Author, Robert Ahlroth Capps

RUN apt-get update && \
    apt-get install -yqq tox firefox

ENV PATH=${PATH}:/root/.local:/root/.local/bin

#: (pseudo)install package -> docker (move via bind)
COPY dist/* ${APP_HOME}/
COPY desmos2python.egg-info ${APP_HOME}

# install all requirements, then install package locally
COPY requirements.txt ${APP_HOME}

#: cd -> pkg directory, then install requirements
WORKDIR ${APP_HOME}
#: explicit cache dir
ENV PIP_CACHE_DIR=/root/.cache
RUN python3 -m pip install \
    --no-warn-script-location --user --upgrade \
    -r requirements.txt

#: ! explicitly set to --no-cache for installing the wheel
RUN python3 -m pip install --no-cache-dir --user --upgrade $(ls *.whl | head -1)


# # # # # # #
#:  [test]  #
# # # # # # #

#: run tests
FROM base as test
ENV APP_HOME /desmos2python
ENV PATH=/root/local/bin:/root/.local:$PATH
COPY --from=base . ${APP_HOME}
WORKDIR ${APP_HOME}
RUN tox


# # # # # # # #
#:  [latest]  #
# # # # # # # #

#: latest build
FROM base as latest
ENV APP_HOME /desmos2python
ENV PATH=/root/local/bin:/root/.local:$PATH
COPY --from=base . ${APP_HOME}
WORKDIR ${APP_HOME}

CMD ["/bin/bash"]