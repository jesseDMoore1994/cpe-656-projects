import argparse
import glob
from statistics import mean
from pprint import PrettyPrinter
pp = PrettyPrinter()


def parse_csv(filename):
    with open(filename) as f:
        contents = f.read()
        lines = contents.splitlines()
        return [
            {
                key: float(value)
                for (key, value) in zip(
                    lines[0].split(','),
                    line.replace('"', '').split(',')
                )
            } for line in lines[1:]
        ]


def get_data_from_files(pattern):
    return [
        calculate_power_for_each_entry(parse_csv(input_csv))
        for input_csv in glob.glob(pattern)
    ]


def calculate_power_for_each_entry(data):
    for entry in data:
        milliamps = entry['Current (nA)'] / 1000000
        millivolts = entry['Voltage (mV)']
        entry['Power (mW)'] = milliamps * millivolts
    return data


# When LED is on Power averages ~8000 mW, when its off its way less.
def find_led_ON(data, start_idx):
    for index, entry in enumerate(data[start_idx:], start_idx):
        if entry['Power (mW)'] > 3000: # if power > 4000 mW assume LED on
            return index


def find_led_OFF(data, start_idx):
    for index, entry in enumerate(data[start_idx:], start_idx):
        if entry['Power (mW)'] < 3000: # if power < 4000 mW assume LED off
            return index


def get_encryption_data(trial):
    data_start_idx = find_led_OFF(trial, find_led_ON(trial, 0))
    data_end_idx = find_led_ON(trial, data_start_idx)
    return trial[data_start_idx:data_end_idx]


def get_net_of_key(trial, key):
    return trial[-1][key] - trial[0][key]


def get_average_of_key(trial, key):
    return mean([datapoint[key] for datapoint in trial])


def get_percentage_error_for_datapoint(datapoint, key, estimate):
    return (
        abs(datapoint[key] - estimate)
        / datapoint[key]
    ) * 100


def get_percentage_errors_for_key(trial, key, estimate):
    return [
        get_percentage_error_for_datapoint(datapoint, key, estimate)
        for datapoint in trial
    ]


def get_average_percentage_error_for_key(trial, key, estimate):
    return mean(get_percentage_errors_for_key(trial, key, estimate))


def get_metrics(trial, bytes_per_trial):
    return {
#        'start_time(ns)' : trial[0]['Time (ns)'],
#        'end_time(ns)' : trial[-1]['Time (ns)'],
        'time_delta(ns)' : get_net_of_key(trial, 'Time (ns)'),
#        'number_of_datapoints': len(trial),
#        'number_of_bytes_processed': bytes_per_trial,
#        'current_average(nA)': get_average_of_key(trial, 'Current (nA)'),
#        'current_average_percentage_error(%)': get_average_percentage_error_for_key(
#            trial, 'Current (nA)', get_average_of_key(trial, 'Current (nA)')
#        ),
#        'voltage_average(mV)': get_average_of_key(trial, 'Voltage (mV)'),
#        'voltage_average_percentage_error(%)': get_average_percentage_error_for_key(
#            trial, 'Voltage (mV)', get_average_of_key(trial, 'Voltage (mV)')
#        ),
        'power_average(mW)': get_average_of_key(trial, 'Power (mW)'),
        'power_average_percentage_error(%)': get_average_percentage_error_for_key(
            trial, 'Power (mW)', get_average_of_key(trial, 'Power (mW)')
        ),
#        'net_energy_consumed_(uJ)': get_net_of_key(trial, 'Energy (uJ)'),
        'estimated_power_per_byte(mW/B)': get_average_of_key(trial, 'Power (mW)')/bytes_per_trial,
        'estimated_energy_consumed_per_byte(uJ/B)':  get_net_of_key(trial, 'Energy (uJ)')/bytes_per_trial,
        'estimated_time_consumed_per_byte(ns/B)':  get_net_of_key(trial, 'Time (ns)')/bytes_per_trial,
    }


def get_trial_metrics(glob_pattern, bytes_per_trial):
    return [
        get_metrics(get_encryption_data(trial), bytes_per_trial)
        for trial in get_data_from_files(glob_pattern)
    ]


def get_complete_metrics(trial_metrics):
    return {
#        'average_current_percentage_error(%)': get_average_of_key(
#            trial_metrics,
#            'current_average_percentage_error(%)'
#        ),
#        'average_power_percentage_error(%)': get_average_of_key(
#            trial_metrics,
#            'voltage_average_percentage_error(%)'
#        ),
#        'average_voltage_percentage_error(%)': get_average_of_key(
#            trial_metrics,
#            'voltage_average_percentage_error(%)'
#        ),
        'estimated_power_per_byte(mW/B)': get_average_of_key(
            trial_metrics, 'estimated_power_per_byte(mW/B)'
        ),
        'estimated_energy_consumed_per_byte(uJ/B)': get_average_of_key(
            trial_metrics, 'estimated_energy_consumed_per_byte(uJ/B)'
        ),
        'estimated_time_consumed_per_byte(ns/B)': get_average_of_key(
            trial_metrics, 'estimated_time_consumed_per_byte(ns/B)'
        ),
        'percent_error_power_per_byte(%)': get_average_percentage_error_for_key(
            trial_metrics,
            'estimated_power_per_byte(mW/B)',
            get_average_of_key(trial_metrics, 'estimated_power_per_byte(mW/B)')
        ),
        'percent_error_energy_consumed_per_byte(%)': get_average_percentage_error_for_key(
            trial_metrics,
            'estimated_energy_consumed_per_byte(uJ/B)',
            get_average_of_key(trial_metrics, 'estimated_energy_consumed_per_byte(uJ/B)')
        ),
        'percent_error_time_consumed_per_byte(%)': get_average_percentage_error_for_key(
            trial_metrics,
            'estimated_time_consumed_per_byte(ns/B)',
            get_average_of_key(trial_metrics, 'estimated_time_consumed_per_byte(ns/B)')
        ),
    }


def main(glob_pattern, bytes_per_trial):
    return {
        'complete_metrics': get_complete_metrics(get_trial_metrics(glob_pattern, bytes_per_trial)),
        'trial_metrics': get_trial_metrics(glob_pattern, bytes_per_trial)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='This project returns interpreted power data from a ccs energytrace csv.'
    )
    parser.add_argument('-i','--input-glob',help='glob of CSV files to be interpreted', required=True)
    parser.add_argument('-b','--bytes-per-trial', help='Bytes parsed in each trail',required=True)
    args = parser.parse_args()
    results = main(args.input_glob, int(args.bytes_per_trial))
    pp.pprint(results)
