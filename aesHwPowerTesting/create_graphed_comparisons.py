import argparse
import glob
import json
import matplotlib.pyplot as plt
import pprint
pp = pprint.PrettyPrinter()


def parse_json(filename):
    with open(filename) as f:
        return {f"{filename}": json.load(f)}


def get_data_from_files(pattern):
    return [
        parse_json(input_json)
        for input_json in glob.glob(pattern)
    ]


def get_energy_per_byte(data):
    keys = [key for d in data for key in d.keys()]
    values = [
        d[key]["complete_metrics"]["estimated_energy_consumed_per_byte(uJ/B)"]
        for d in data for key in d.keys()
    ]
    return keys, values


def get_power_per_byte(data):
    keys = [key for d in data for key in d.keys()]
    values = [
        d[key]["complete_metrics"]["estimated_power_per_byte(mW/B)"]
        for d in data for key in d.keys()
    ]
    return keys, values


def get_time_per_byte(data):
    keys = [key for d in data for key in d.keys()]
    values = [
        d[key]["complete_metrics"]["estimated_time_consumed_per_byte(ns/B)"]
        for d in data for key in d.keys()
    ]
    return keys, values


def main(glob_pattern):
    fig, (energy, power, time) = plt.subplots(1, 3)
    data = get_data_from_files(glob_pattern)

    keys, values = get_energy_per_byte(data)
    energy.set_title("Energy Consumed per Byte in Environment.")
    energy.set_xlabel("environment")
    energy.set_ylabel("energy (uJ/B)")
    energy.bar(keys, values)

    keys, values = get_power_per_byte(data)
    power.set_title("Power per Byte in Environment.")
    power.set_xlabel("environment")
    power.set_ylabel("Power (mW/B)")
    power.bar(keys, values)

    keys, values = get_time_per_byte(data)
    time.set_title("Time Consumed per Byte in Environment.")
    time.set_xlabel("environment")
    time.set_ylabel("time (ns/B)")
    time.bar(keys, values)

    fig.set_size_inches(16, 10)
    fig.savefig('output.png', dpi=100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='This project returns interpreted power data from a ccs energytrace csv.'
    )
    parser.add_argument('-i','--input-glob',help='glob of json metrics to compare', required=True)
    args = parser.parse_args()
    main(args.input_glob)
