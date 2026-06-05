from model.parser import parse_args


def main() -> None:
    """
    Entry point for the model system.
    """

    args = parse_args()

    from model.controller import run
    run(args.input_image_path, args.output_json_path)


if __name__ == "__main__":
    main()
