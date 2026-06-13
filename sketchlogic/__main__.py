from sketchlogic.parser import parse_args


def main() -> None:
    """
    Entry point for the sketchlogic system.
    """

    args = parse_args()
    print(f"Debug mode: {args.debug}")
    from sketchlogic.controller import run
    run(args.input_image_path, args.output_json_path, args.debug)


if __name__ == "__main__":
    main()
