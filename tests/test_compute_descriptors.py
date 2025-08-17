import unittest
from unittest.mock import MagicMock, patch

import numpy as np

import compute_descriptors


class TestComputeDescriptors(unittest.TestCase):
    @patch("compute_descriptors.cv.SIFT_create")
    def test_get_descriptors_no_keypoints(self, mock_sift_create):
        # SIFT returns no descriptors
        mock_sift = MagicMock()
        mock_sift.detectAndCompute.return_value = ([], None)
        mock_sift_create.return_value = mock_sift

        image = np.zeros((100, 100), dtype=np.uint8)
        result = compute_descriptors.get_descriptors(image)
        self.assertIsNone(result)

    @patch("compute_descriptors.cv.SIFT_create")
    def test_get_descriptors_with_keypoints(self, mock_sift_create):
        # SIFT returns descriptors and keypoints
        mock_kp = MagicMock()
        mock_kp.response = 0.05
        mock_sift = MagicMock()
        mock_sift.detectAndCompute.return_value = ([mock_kp], np.array([[1, 2, 3, 4]]))
        mock_sift_create.return_value = mock_sift

        image = np.zeros((100, 100), dtype=np.uint8)
        result = compute_descriptors.get_descriptors(image)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    @patch("compute_descriptors.get_all_files")
    @patch("compute_descriptors.DescriptorStorage")
    @patch("compute_descriptors.imread2")
    @patch("compute_descriptors.os.path.getmtime", return_value=1234567890)
    def test_get_all_descriptors_image(
        self, mock_getmtime, mock_imread2, mock_DescriptorStorage, mock_get_all_files
    ):
        # Setup mocks
        mock_get_all_files.return_value = ["img1.jpg"]
        mock_imread2.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_storage = {}
        mock_DescriptorStorage.get_storage.return_value = mock_storage
        mock_DescriptorStorage.save_storage.return_value = None

        # Patch get_descriptors to always return a list
        with patch("compute_descriptors.get_descriptors", return_value=[1, 2, 3]):
            compute_descriptors.get_all_descriptors(["dummy_path"])
            self.assertIn("img1.jpg", mock_storage)
            self.assertEqual(mock_storage["img1.jpg"][0], [1, 2, 3])

    @patch("compute_descriptors.get_all_files")
    @patch("compute_descriptors.DescriptorStorage")
    @patch("compute_descriptors.get_video_snapshots")
    @patch("compute_descriptors.os.path.getmtime", return_value=1234567890)
    def test_get_all_descriptors_video(
        self,
        mock_getmtime,
        mock_get_video_snapshots,
        mock_DescriptorStorage,
        mock_get_all_files,
    ):
        mock_get_all_files.return_value = ["vid1.mp4"]
        mock_get_video_snapshots.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_storage = {}
        mock_DescriptorStorage.get_storage.return_value = mock_storage
        mock_DescriptorStorage.save_storage.return_value = None

        with patch("compute_descriptors.get_descriptors", return_value=[4, 5, 6]):
            compute_descriptors.get_all_descriptors(["dummy_path"])
            self.assertIn("vid1.mp4", mock_storage)
            self.assertEqual(mock_storage["vid1.mp4"][0], [4, 5, 6])


if __name__ == "__main__":
    unittest.main()
