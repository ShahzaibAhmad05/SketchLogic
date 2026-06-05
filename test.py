from model.inference import infer
from pathlib import Path


def main():
    results = infer(Path("temp.jpg"))
    print(results)


if __name__ == "__main__":
    main()
