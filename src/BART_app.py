#!/usr/bin/env python

import os
import sys
import argparse

def create_argparser():
    parser = argparse.ArgumentParser(description="Run BART test.")

    parser.add_argument(
        "--condition",
        default=os.environ.get("BART_CONDITION", "control"),
        help="Port to connect to the robot.",
    )
    parser.add_argument(
        "--ip",
        default=os.environ.get("NAO_IP", "192.168.1.100"),
        help="Port to connect to the robot.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=os.environ.get("NAO_PORT", 9559),
        help="Port to connect to the robot.",
    )
    parser.add_argument(
        "--path",
        default=os.environ.get("BART_PATH",
            os.path.dirname(os.path.realpath(__file__))+"/results/"),
        help="Directory for storing the results of the BART test.",
    )
    parser.add_argument(
        "--balloons",
        type=int,
        default=os.environ.get("BART_BALLOONS", 30),
        help="# of balloons for the BART test.",
    )
    parser.add_argument(
        "--range",
        default=os.environ.get("BART_RANGE", [1, 127]),
        help="Range of explosion for balloons.",
    )

    return parser


if __name__ == "__main__":
    parser = create_argparser()
    args, unknown = parser.parse_known_args()
    sys.argv[1:] = unknown

    import kivy
    from kivy.core.window import Window
    from BART_app.bart import BART

    Window.fullscreen = False
    Window.maximize()
    # call the first window
    BART(args.condition, args.path,
        args.balloons, args.range,
        args.ip, args.port).run()

