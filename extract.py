import pickle

import numpy as np

TIME_DELTA = 1492001758
ROUNDS_COUNT = 100
MIN_CONFIDENCE = 0.8

def load_data():
    data_file = open('pupil_data', 'rb')
    data = pickle.load(data_file)
    data_file.close()
    return data

def load_timestamps():
    timestamps_file = open('timestamps', 'r')
    row_timestamps = timestamps_file.read().split('\n')
    timestamps = []
    for timestamp in row_timestamps:
        if timestamp:
            timestamp_loaded = [int(x) for x in timestamp.split(';')]
            timestamps.append({
                'start': timestamp_loaded[1] / 1000000,
                'finish': timestamp_loaded[2] / 1000000,
                'lie': bool(timestamp_loaded[3]),
            })
    timestamps_file.close()
    return timestamps
    
def load_samples(data, timestamps):
    samples = []
    timestamp_i = 0
    current_timestamp = timestamps[timestamp_i]
    current_sample = []
    for pos in data['pupil_positions']:
        if pos['timestamp'] + TIME_DELTA > current_timestamp['finish']:
            samples.append(current_sample)
            current_sample = []
            timestamp_i += 1
            if timestamp_i == ROUNDS_COUNT:
                break
            current_timestamp = timestamps[timestamp_i]
        if pos['timestamp'] + TIME_DELTA > current_timestamp['start']:
            if pos['confidence'] > MIN_CONFIDENCE:
                diameter = pos['diameter']
                norm_pos_x = pos['norm_pos'][0]
                norm_pos_y = pos['norm_pos'][1]
                current_sample.append({
                    'x': norm_pos_x,
                    'y': norm_pos_y,
                    'd': diameter,
                })
    return samples

def get_length(x1, y1, x2, y2):
    return ((x2-x1) ** 2 + (y2 - y1) ** 2) ** (1 / 2)
    
def get_speed(sample, timestamp):
    path_length = 0
    cur_x = -1
    cur_y = -1
    for measure in sample:
        if measure['x'] == 0.5 and measure['y'] == 0.5:
            continue
        if cur_x == -1 and cur_y == -1:
            cur_x = measure['x']
            cur_y = measure['y']
            continue
        path_length += get_length(measure['x'], measure['y'], cur_x, cur_y)
        cur_x = measure['x']
        cur_y = measure['y']
    return path_length / (timestamp['finish'] - timestamp['start'])
    
def extract_features(samples, timestamps):
    extracted = []
    for i in range(ROUNDS_COUNT):
        mean_x = np.mean([x['x'] for x in samples[i] if x != 0.5])
        mean_y = np.mean([x['y'] for x in samples[i] if x != 0.5])
        std_x = np.std([x['x'] for x in samples[i] if x != 0.5])
        std_y = np.std([x['y'] for x in samples[i] if x != 0.5])
        std_diameter = np.std([x['d'] for x in samples[i]])
        mean_diameter = np.mean([x['d'] for x in samples[i]])
        pupil_speed = get_speed(samples[i], timestamps[i])
        lie = int(timestamps[i]['lie'])
        extracted.append([
            mean_x, std_x,
            mean_y, std_y,
            mean_diameter, std_diameter,
            pupil_speed, lie
        ])
    return extracted
    
def write_csv(extracted):
    with open('pupil.csv', 'w') as file:
        for features in extracted:
            file.write(';'.join([str(x) for x in features]) + '\n')
    
def main():
    data = load_data()
    timestamps = load_timestamps()
    samples = load_samples(data, timestamps)
    extracted = extract_features(samples, timestamps)
    write_csv(extracted)
    
if __name__ == '__main__':
    main()