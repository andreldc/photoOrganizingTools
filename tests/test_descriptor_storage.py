import os
import unittest

from storage.descriptor_storage import DescriptorStorage


class TestDescriptorStorage(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_descriptors.pkl"
        DescriptorStorage.pickle_filename = self.test_file

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_get_storage(self):
        descriptors = {"image1.jpg": [0.1, 0.2, 0.3], "image2.jpg": [0.4, 0.5, 0.6]}
        DescriptorStorage.save_storage(descriptors)
        loaded_descriptors = DescriptorStorage.get_storage()
        self.assertEqual(descriptors, loaded_descriptors)

    def test_get_storage_empty(self):
        loaded_descriptors = DescriptorStorage.get_storage()
        self.assertEqual(loaded_descriptors, {})


if __name__ == "__main__":
    unittest.main()
