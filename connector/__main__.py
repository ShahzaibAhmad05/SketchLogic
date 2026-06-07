from connector.parser import parse_args


def main() -> None:
    """
    Entry point for the connector system.
    """

    args = parse_args()

    from connector.controller import run
    run(args.input_image_path, args.model_results_json_path, args.output_json_path)


if __name__ == "__main__":
    main()
