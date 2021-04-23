import pandas as pd

from formula1.dataset import ErgastDataset


def main():
    print("Building dataset")

    dataset = ErgastDataset()
    print(dataset.build_dataset())


if __name__ == "__main__":
    main()
