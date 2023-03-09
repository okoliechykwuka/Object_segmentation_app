## Installation Steps

1. Install Anaconda https://docs.anaconda.com/anaconda/install/windows/

2. Create a environment.yml file containing the following code.  **Done**
   
    name: detectron2
    channels:
    - pytorch_
    - conda-forge
    - anaconda
    - defaults
    dependencies:
    - python=3.8
    - fastapi>=0.88.0
    - python-multipart
    - python_jose
    - pymongo
    - pydantic
    - passlib
    - uvicorn
    - websockets
    - httpx
    - opencv_python
    - imutils
    - numpy==1.23.4
    - pywin32
    - cudatoolkit=11.0
    - torch
    - torchvision==0.8.2
    - git
    - pip
    - pip:
        - git+https://github.com/facebookresearch/detectron2.git@v0.3
        

3. Launch the Anaconda terminal, navigate to the **environment.yml** file and run `conda env create -f environment.yml`

4. Activate the environment `conda activate detectron2`

### Run the script

cd detectron2/app folder  and run   `uvicorn main:app --reload`

5. ones the server is running, open login.html in your browser.


pip install git+github.com/facebookresearch/detectron2.git