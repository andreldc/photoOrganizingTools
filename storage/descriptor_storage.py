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


class HistogramStorage:
    pickle_filename = "d:\\histograms.pkl"

    @staticmethod
    def get_storage():
        """Gets histogram storage"""
        try:
            with open(HistogramStorage.pickle_filename, "rb") as pickle_reader:
                return pickle.load(pickle_reader)
        except Exception:
            return {}

    @staticmethod
    def save_storage(histograms):
        """Saves histogram storage"""
        with open(HistogramStorage.pickle_filename, "wb") as pickle_writer:
            pickle.dump(histograms, pickle_writer)


class DuplicateHistogramStorage:
    pickle_filename = "d:\\duplicates.pkl"

    @staticmethod
    def get_storage():
        """Gets duplicates storage"""
        try:
            with open(DuplicateHistogramStorage.pickle_filename, "rb") as pickle_reader:
                return pickle.load(pickle_reader)
        except Exception:
            return {}

    @staticmethod
    def save_storage(duplicates):
        """Saves duplicates storage"""
        with open(DuplicateHistogramStorage.pickle_filename, "wb") as pickle_writer:
            pickle.dump(duplicates, pickle_writer)
