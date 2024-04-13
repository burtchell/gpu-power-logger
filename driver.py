#!/usr/bin/env python3

import pynvml

import subprocess
import argparse
import time
import datetime
import yaml


def setup_pynvml():
    pynvml.nvmlInit()
    n_devices = pynvml.nvmlDeviceGetCount()
    devices = []
    for i in range(n_devices):
        devices.append(pynvml.nvmlDeviceGetHandleByIndex(i))
    return devices, n_devices


def monitor_program(command, frequency, devices, n_devices):
    results = []

    # launch process on another thread
    proc = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # meanwhile, record GPU power
    while True:
        time_correction = time.time()
        for i in range(n_devices):
            timestamp = (
                datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
            )
            timestamp = (
                timestamp[:-2] + ":" + timestamp[-2:]
            )  # add colon for timezone UTC offset
            results.append(
                {
                    "timestamp": timestamp,
                    "duration": frequency,
                    "gpu/power-usage": (
                        pynvml.nvmlDeviceGetPowerUsage(devices[i]) / 1000  # milliwatts
                    ),
                }
            )

        if proc.poll() is not None:
            break

        time_correction = time.time() - time_correction
        time.sleep(frequency - time_correction)

    return results


def output_to_manifest_yaml(results: list, region: str, filename: str):
    with open(filename, "w") as outfile:
        with open("./manifest_header.yml", "r") as infile:
            outfile.writelines(infile.readlines())
        outfile.write("\n")
        tree = {
            "tree": {
                "children": {
                    "child": {
                        "pipeline": ["gpu-carbon-estimator"],
                        "defaults": {"region": region},
                        "inputs": results,
                    }
                }
            }
        }
        yaml.dump(tree, outfile, default_flow_style=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--frequency",
        type=float,
        default=1.0,
        help="Frequency to query the GPUs (in seconds)",
    )
    parser.add_argument("-r", "--region", default="US", help="Two-character UN/LOCODE")
    parser.add_argument(
        "-o", "--output", default="gpu_power.yml", help="Output filename"
    )
    parser.add_argument(
        "command",
        nargs="*",
        default=["sleep", "10"],
        help="The command (and arguments) to monitor ('sleep 10' by default)",
    )
    args = parser.parse_args()

    devices, n_devices = setup_pynvml()
    results = monitor_program(args.command, args.frequency, devices, n_devices)
    output_to_manifest_yaml(results, args.region, args.output)
