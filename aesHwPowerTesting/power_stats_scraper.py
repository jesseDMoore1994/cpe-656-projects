import argparse
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


def calculate_power_for_each_entry(data):
    for entry in data:
        milliamps = entry['Current (nA)'] / 1000000
        millivolts = entry['Voltage (mV)']
        entry['Power (mW)'] = milliamps * millivolts
    return data


# When LED is on Power averages ~8000 mW, when its off its way less.
def find_led_ON(data, start_idx):
    for index, entry in enumerate(data[start_idx:], start_idx):
        if entry['Power (mW)'] > 6000: # if power > 6000 mW assume LED on
            return index


def find_led_OFF(data, start_idx):
    for index, entry in enumerate(data[start_idx:], start_idx):
        if entry['Power (mW)'] < 6000: # if power < 6000 mW assume LED off
            return index


def find_first_trial(data):
    led_on_idx = find_led_ON(data, 0)
    led_off_idx = find_led_OFF(data, led_on_idx)
    return led_off_idx


def parse_next_trial(data, start_idx):
    led_on_idx = find_led_ON(data, start_idx)
    led_off_idx = find_led_OFF(data, led_on_idx)
    trial_data = data[start_idx:led_on_idx-1]
    next_trial_idx = led_off_idx
    return trial_data, next_trial_idx


def get_trials(data, number_of_trials):
    trial_data = []
    trial_idx = find_first_trial(data)
    for _ in range(number_of_trials):
        trial, next_trial_idx = parse_next_trial(data, trial_idx)
        trial_data.append(trial)
        trial_idx = next_trial_idx
    return trial_data


def get_net_of_key(trial, key):
    return trial[-1][key] - trial[0][key]


def get_average_of_key(trial, key):
    return mean([datapoint[key] for datapoint in trial])


def get_trial_metrics(trial, bytes_per_trial):
    return {
        'start_time_(ns)' : trial[0]['Time (ns)'],
        'end_time_(ns)' : trial[-1]['Time (ns)'],
        'time_delta_(ns)' : get_net_of_key(trial, 'Time (ns)'),
        'number_of_datapoints': len(trial),
        'number_of_bytes_processed': bytes_per_trial,
        'average_current_(nA)': get_average_of_key(trial, 'Current (nA)'),
        'average_voltage_(mV)': get_average_of_key(trial, 'Voltage (mV)'),
        'average_power_(mW)': get_average_of_key(trial, 'Power (mW)'),
        'net_energy_consumed_(uJ)': get_net_of_key(trial, 'Energy (uJ)'),
        'energy_consumed_per_byte_(uJ/B)':  get_net_of_key(trial, 'Energy (uJ)')/bytes_per_trial
    }


def get_average_of_key_for_all_trials(trial_metrics, key):
    return mean([metric[key] for metric in trial_metrics])


def interpret_trials(trials, bytes_per_trial, number_of_trials):
    trial_metrics = [get_trial_metrics(trial, bytes_per_trial) for trial in trials]
    return {
        'number_of_trials': number_of_trials,
        'bytes_per_trial': bytes_per_trial,
        'total_bytes_processed': bytes_per_trial * number_of_trials,
        'average_time_(ns)': get_average_of_key_for_all_trials(trial_metrics, 'time_delta_(ns)'),
        'average_current_(nA)': get_average_of_key_for_all_trials(trial_metrics, 'average_current_(nA)'),
        'average_voltage_(mV)': get_average_of_key_for_all_trials(trial_metrics, 'average_voltage_(mV)'),
        'average_power_(mW)': get_average_of_key_for_all_trials(trial_metrics, 'average_power_(mW)'),
        'average_net_energy_consumed_(uJ)': get_average_of_key_for_all_trials(trial_metrics, 'net_energy_consumed_(uJ)'),
        'average_energy_consumed_per_byte_(uJ/B)': get_average_of_key_for_all_trials(trial_metrics, 'energy_consumed_per_byte_(uJ/B)'),
    }


def main(input_csv, bytes_per_trial, number_of_trials):
    data = calculate_power_for_each_entry(parse_csv(input_csv))
    trials = get_trials(data, number_of_trials)
    return interpret_trials(trials, bytes_per_trial, number_of_trials)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='This project returns interpreted power data from a ccs energytrace csv.'
    )
    parser.add_argument('-i','--input-csv',help='CSV file to be interpreted', required=True)
    parser.add_argument('-b','--bytes-per-trial', help='Bytes parsed in each trail',required=True)
    parser.add_argument('-n','--number-of-trials', help='Number of trials in csv file',required=True)
    args = parser.parse_args()
    results = main(args.input_csv, int(args.bytes_per_trial), int(args.number_of_trials))
    pp.pprint(results)
