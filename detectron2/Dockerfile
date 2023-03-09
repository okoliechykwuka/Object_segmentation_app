FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu18.04

WORKDIR /detectron2

ADD . /detectron2


#Install MINICONDA
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda.sh && \
	/bin/bash Miniconda.sh -b -p /opt/conda && \
	rm Miniconda.sh

ENV PATH /opt/conda/bin:$PATH


# Install gcc as it is missing in our base layer
RUN apt-get update && apt-get -y install gcc 

# Create the environment:
# Install gcc as it is missing in continuumio/miniconda:latest
RUN conda env create -f environment.yml


# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "detectron3",  "/bin/bash", "-c"]

# Activate the environment, and make sure it's activated:
RUN conda activate detctron3
RUN echo "Make sure fastapi is installed:"
RUN python -c "import fastapi"


EXPOSE 5000

# The code to run when container is started:
ENTRYPOINT ["conda", "run", "-n", "detectron3", "python", "src/app.py"]

CMD = ["uvicorn", 'app:app --reload']
