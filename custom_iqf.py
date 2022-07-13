import glob
import os
import shutil
from typing import Any, Dict, Optional

import cv2
import numpy as np

from iquaflow.datasets import DSModifier

class DSModifierDirSaveJPEG(DSModifier):

    def __init__(self, ds_modifier: Optional[DSModifier] = None):
        self.name = "dir_modifier"
        self.ds_modifier = ds_modifier
        self.params = {"modifier": "{}".format(self._get_name())}

    # def is_input_file(self, data_file):
    #    return all(omi not in data_file for omi in self.omit) and any(ext in data_file for ext in self.extensions)

    def _ds_input_modification(self, data_input: str, mod_path: str) -> str:
        """Modify images
        Iterates the data_input path loading images, processing with _mod_img(), and saving to mod_path

        Args
            data_input: str. Path of the original folder containing images
            mod_path: str. Path to the new dataset

        Returns:
            Name of the new folder containign the images
        """
        input_name = os.path.basename(data_input)
        dst = os.path.join(mod_path, input_name)
        os.makedirs(dst, exist_ok=True)
        for enu,data_file in enumerate(os.listdir(data_input)):
            file_path = os.path.join(data_input, data_file)
            dst_fn = os.path.join(dst, data_file.split('.')[0]+'.jpg')
            if os.path.isdir(file_path):
                continue
            if os.path.exists(dst_fn):
                continue
            loaded = cv2.imread(file_path, -1)
            print(enu,file_path)
            assert loaded.ndim == 2 or loaded.ndim == 3, (
                "(load_img): File " + file_path + " not valid image"
            )
            # size_raw+= np.size(loaded)
            imgp = self._mod_img(loaded)
            # print(loaded.shape)
            cv2.imwrite(
                dst_fn,
                imgp
                )
        return input_name

    def _mod_img(self, img: np.array) -> np.array:
        """Modify single image
        This method should be overwitten for child classes. In this Base version just return the image unchanged.

        Args
            img: Numpy array. Original image

        Returns:
            img: Numpy array. Modified image
        """
        return img  # just leave the img as is


class DSModifier_quant(DSModifierDirSaveJPEG):

    def __init__(
        self,
        ds_modifier: Optional[DSModifier] = None,
        params: Dict[str, Any] = {"bits": 4},
    ):
        self.name = f"quant{params['bits']}_modifier"
        self.params: Dict[str, Any] = params
        self.ds_modifier = ds_modifier
        self.params.update({"modifier": "{}".format(self._get_name())})

    def _mod_img(self, img: np.array) -> np.array:
        rec_img = img.copy()
        rec_img = rec_img & (0xFF << (8 - self.params["bits"]))
        return rec_img


class DSModifier_jpg(DSModifierDirSaveJPEG):

    def __init__(
        self,
        ds_modifier: Optional[DSModifier] = None,
        params: Dict[str, Any] = {"quality": 65},
    ):
        self.name = f"jpg{params['quality']}_modifier"
        self.params: Dict[str, Any] = params
        self.ds_modifier = ds_modifier
        self.params.update({"modifier": "{}".format(self._get_name())})

    def _mod_img(self, img: np.array) -> np.array:
        par = [cv2.IMWRITE_JPEG_QUALITY, self.params["quality"]]
        retval, tmpenc = cv2.imencode(".jpg", img, par)
        # size_proc+= np.size(tmpenc)
        rec_img = cv2.imdecode(tmpenc, -1)
        return rec_img


class DSModifierResize(DSModifierDirSaveJPEG):

    def __init__(
        self,
        ds_modifier: Optional[DSModifier] = None,
        params: Dict[str, Any] = {"scaleperc": 100}
    ):
        self.name = f"resize{params['scaleperc']}"
        self.params: Dict[str, Any] = params
        self.ds_modifier = ds_modifier
        self.params.update({"modifier": "{}".format(self._get_name())})

    def _ds_input_modification(self, data_input: str, mod_path: str) -> str:

        input_name = os.path.basename(data_input)
        dst_compressed = os.path.join(mod_path, 'images_compressed')
        dst_resized_back = os.path.join(mod_path, input_name)

        os.makedirs(dst_compressed, exist_ok=True)
        os.makedirs(dst_resized_back, exist_ok=True)

        for data_file in os.listdir(data_input):

            file_path = os.path.join(data_input, data_file)

            if os.path.isdir(file_path):
                continue

            loaded = cv2.imread(file_path, -1)

            assert loaded.ndim == 2 or loaded.ndim == 3, (
                "(load_img): File " + file_path + " not valid image"
            )

            imgp = self._mod_img(loaded)

            cv2.imwrite(os.path.join(dst_compressed, data_file.split('.')[0]+'.jpg'), imgp)

            resized_back = cv2.resize(
                imgp,
                (int(loaded.shape[1]), int(loaded.shape[0])),
                interpolation = cv2.INTER_CUBIC
            )

            cv2.imwrite(os.path.join(dst_resized_back, data_file.split('.')[0]+'.jpg'), resized_back)

        return input_name

    def _mod_img(self, img: np.array) -> np.array:
        scale_percent = self.params["scaleperc"] # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation = cv2.INTER_CUBIC)
