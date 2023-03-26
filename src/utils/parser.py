"""Parse CLI arguments and set global settings."""

import argparse
import json

import src.utils.user_settings as settings
import src.utils.constants as constants


def parse_json() -> None:
    """TODO"""
    pass


def parse_gui_cli() -> None:
    """Parse GUI CLI args and set global settings in `user_settings.py`."""
    parser = argparse.ArgumentParser(
        usage="./gui.py [-h] [-d] [-s] [-e] [-t THEME] [-c COLOR]"
    )
    parser.add_argument("-d", "--debug", help="print debug info", action="store_true")
    parser.add_argument(
        "-s", "--smooth", help="smooth image before rendering", action="store_true"
    )
    parser.add_argument(
        "-e",
        "--export-index",
        help="exported filenames will use the index displayed in the GUI instead of the \
                        original image name",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--theme",
        help="configure theme, options are "
        + str(constants.THEMES)[1:-1].replace("'", "")
        + ", and the default theme is dark-hct",
    )
    parser.add_argument(
        "-c",
        "--color",
        help="contour color as name (e.g. red) or hex color code rrggbb",
    )
    args = parser.parse_args()

    if args.debug:
        settings.DEBUG = True
        print("Debug CLI option supplied.")

    if args.smooth:
        settings.SMOOTH_BEFORE_RENDERING = True
        print("Smooth CLI option supplied.")

    if args.export_index:
        settings.EXPORTED_FILE_NAMES_USE_INDEX = True
        print("Exported files will use the index displayed in the GUI.")

    if args.theme:
        if args.theme not in constants.THEMES:
            print(
                "Invalid theme specified. Options are "
                + (str(constants.THEMES))[1:-1].replace("'", "")
                + "."
            )
            exit(1)

        settings.THEME_NAME = args.theme
        if args.theme == "dark":
            # Theme color from dark.json
            settings.CONTOUR_COLOR = "3daee9"
        elif args.theme == "light":
            # Theme color from light.json
            settings.CONTOUR_COLOR = "3daef3"
        print(f"Theme {args.theme} specified.")

    if args.color:
        settings.CONTOUR_COLOR = args.color
        print(
            f"Contour color is {'#' if not args.color.isalpha() else ''}{args.color}."
        )
