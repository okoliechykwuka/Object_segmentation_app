# Object_segmentation_app

This is an Object Segmentation App that uses the Detectron2 library and FastAPI web framework. The app allows users to segment objects in real time, returning the segmented feeds  with a mask overlay of the identified objects.

The app is built using Python 3.7 or higher and requires the installation of the Detectron2 and FastAPI libraries, along with other dependencies specified in the requirements.txt file.

To run the app, navigate to the project directory and run the following command:

`
uvicorn main:app --reload
`

This will start the app on the default port 8000. To use the app, navigate to http://localhost:8000 in your web browser and upload an image. The app will perform object segmentation and return the segmented image with a mask overlay.

Please note that this app is intended for educational and demonstration purposes only.

For more information on how to use the app, please refer to the documentation and comments in the source code.

**App Interface**


![Homepage](https://github.com/okoliechykwuka/Object_segmentation_app/blob/main/detectron2/Screenshot%202023-03-09%20210403.png)


![Detection page](https://github.com/okoliechykwuka/Object_segmentation_app/blob/main/detectron2/image.png)
