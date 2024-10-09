import pickle


class DescriptorStorage:
    pickle_filename = "d:\\descriptors.pkl"

    @staticmethod
    def get_storage():
        """Gets descriptor storage"""
        try:
            with open(DescriptorStorage.pickle_filename, "rb") as pickle_reader:
                return pickle.load(pickle_reader)
        except Exception:
            return {}

    @staticmethod
    def save_storage(descriptors):
        """Saves descriptor storage"""
        with open(DescriptorStorage.pickle_filename, "wb") as pickle_writer:
            pickle.dump(descriptors, pickle_writer)
