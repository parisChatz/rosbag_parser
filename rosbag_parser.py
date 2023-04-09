#!/usr/bin/env python3

import rosbag
import os
import sys
import pandas as pd

# TODO Include logging module and remove prints

class TopicNotFoundInBagError(Exception):
    pass

class RosbagParser:
    # TODO create docstrings
    def __init__(self, folder_path, topics_to_parse=[]):
        try:
            if not os.path.exists(folder_path):
                raise FileNotFoundError
            self.folder_path = folder_path
            self.topics_to_parse = topics_to_parse
        
        except FileNotFoundError as e:
            print(f"{repr(e)}: The specified folder does not exist. Please check if path given is correct.")
            sys.exit(1)

    def check_topics(self, topic_list):
        try:
            for file in os.listdir(self.folder_path):
                if file.endswith(".bag"):
                    with rosbag.Bag(os.path.join(self.folder_path, file)) as bag:
                        topics = list(bag.get_type_and_topic_info().topics.keys())
                        if topic_list[0]!="all":
                            # If user specified which topics they want
                            common_topics = list(set(topic_list).intersection(topics))
                            different_topics = list(set(topic_list).difference(topics))
                            if different_topics:
                                raise TopicNotFoundInBagError
                            self.topics_to_parse = common_topics
                        else:
                            self.topics_to_parse = topics   

        except TopicNotFoundInBagError as e:
            print(f"{repr(e)}: Topics {different_topics} not found in {file}")
            sys.exit(1)

    def parse_rosbags(self, topics=None, save_csv=True):
        topics = topics or self.topics_to_parse
        for file in os.listdir(self.folder_path):
            if file.endswith(".bag"):
                df = pd.DataFrame(columns=topics)
                with rosbag.Bag(os.path.join(self.folder_path, file)) as bag:
                    rows = []
                    for topic, msg, t in bag.read_messages(topics=topics):
                        row = {col_topic: None for col_topic in topics}
                        row[topic] = msg
                        row['Timestamp'] = t
                        rows.append(row)
                    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                if save_csv:
                    filename = file.split(".")[0]
                    df.set_index('Timestamp', inplace=True)
                    df.to_csv(os.path.join(self.folder_path, f'{filename}.csv'), index=True)


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print("Please provide the path to the rosbag folder when running the script. \nExample: python3 rosbag_parser.py /path/to/rosbag_folder")
        sys.exit(1)
    folder_path = sys.argv[1]

    parser = RosbagParser(folder_path)

    while True:
        topics = input("Enter the topics you want to parse (separate multiple topics with space or type all): ")
        topics = topics.split()
        if any(topic.startswith("/") for topic in topics):
            break
        print("Error: All topics must start with '/'")

    # Check the topics
    parser.check_topics(topics)

    # Parse rosbags
    parser.parse_rosbags()
