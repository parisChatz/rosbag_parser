#!/usr/bin/env python3

"""This script parses BAG files in a path and saves them to a directory in CSV format.

When run the script prompts the user to give desired topics to save or even ask for all the topics available.
The script scans the given path for bag files and gets the topics for each rosbag file. 
After determining the common topics among all rosbags, if a topic from the user is not found then it 
outputs an error. Else, for each bag file in the given path, the script creates a CSV file in the rosbag directory
with the name of each CSV file the same as the name of the corresponding rosbag.

The script takes one argument:
    - the path to the ROS bag file folder directory

Usage: python3 rosbag_parser.py /path/to/rosbag/folder/path
"""

import logging
import os
import sys

import pandas as pd
import rosbag

__author__ = "Paris Chatzithanos"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = "Paris Chatzithanos"
__date__ = "2023/04/22"
__license__ = "MIT"
__version__ = "2.0.1"
__maintainer__ = "Paris Chatzithanos"
__email__ = "parischatz94@gmail.com"
__status__ = "Development"

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


class TopicNotFoundInBagError(Exception):
    """
    Exception class for when specified topics are not found in rosbag file.
    """

    pass


class BagsNotFoundError(Exception):
    """
    Exception class for when there are no rosbag files in the specified directory.
    """

    pass


class RosbagParser:
    """
    A class for parsing rosbags and saving as CSV files.
    """

    def __init__(self, folder_path, topics_to_parse=[]):
        """
        Initializes an instance of the RosbagParser class.

        Parameters:
        folder_path (str): Path to the directory containing the rosbag files.
        topics_to_parse (list): Optional list of topic names to parse from the rosbag files.

        Returns:
            None.
        """
        self.setup_logging()
        try:
            if not os.path.exists(folder_path):
                raise FileNotFoundError
            self.folder_path = folder_path
            self.topics_to_parse = topics_to_parse

        except FileNotFoundError as e:
            logging.error(
                f"{repr(e)}: The specified folder does not exist. Please check if path given is"
                " correct."
            )
            sys.exit(1)

    def setup_logging(self):
        """
        Sets up the logging for the application.
        """
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG,
        )

    def get_topics(self, topic_list):
        """
        This method returns a list of topics that are common among all the rosbags in the specified folder_path.
        If topic_list parameter is ["all"], then all the topics present in the rosbags will be returned.

        Parameters:
            topic_list (list): A list of topic names to search for, or the string "all" to search for all topics.
        Returns:
            Returns a list of topics that are common among all the rosbags in the specified folder_path.
        """
        all_topics = self._get_all_topics()

        if topic_list[0] == "all":
            common_topics = self._find_common_topics(all_topics)
        else:
            common_topics = self._find_common_topics_with_user_topic_list(all_topics, topic_list)

        # Sorted common_topics alphabetically after the "/" (x[1]) of rostopics
        self.topics_to_parse = sorted(common_topics, key=lambda x: x[1])
        return self.topics_to_parse

    def _get_all_topics(self):
        """
        Scan every .bag file in the specified folder and return a list of lists with all the topics
        found in each rosbag file.

        Args:
            None.

        Returns:
            A list of lists. Each sub-list contains all the topics of one rosbag file in the specified folder.

        Raises:
            BagsNotFoundError: If no .bag files are found in the specified folder. The program exits with
                a status code of 1, printing an error message to the console.
        """
        try:
            found_bags = False
            all_topics = []
            for file in os.scandir(self.folder_path):
                if file.name.endswith(".bag"):
                    found_bags = True
                    with rosbag.Bag(file.path) as bag:
                        topics = list(bag.get_type_and_topic_info().topics.keys())
                        all_topics.append(topics)
            if not found_bags:
                raise BagsNotFoundError
            return all_topics

        except BagsNotFoundError as e:
            logging.error(f"{repr(e)}: No bags in {self.folder_path}")
            sys.exit(1)

    def _find_common_topics(self, all_topics):
        """
        Given a list of lists with all the topics found in each rosbag file, this method returns a list
        with the topics that are common in all rosbag files.

        Args:
            all_topics (list): A list of lists, where each inner list contains all the topics found in one rosbag
            file.

        Returns:
            A list with the topics that are common to all of the rosbag files.
        """
        recurrent_topics = set(all_topics[0])
        for topic_list in all_topics:
            recurrent_topics.union(set(topic_list))
        return list(recurrent_topics)

    def _find_common_topics_with_user_topic_list(self, all_topics, topic_list):
        """
        Given a list of lists with all the topics found in each rosbag file, and a user-specified list of topics, this
        method returns a list with the topics that are common to all rosbag files and the user-specified topic list.

        Args:
            all_topics (list): A list of lists, where each inner list contains all the topics found in one rosbag file.
            topic_list (list): A list of topics specified by the user.

        Returns:
            A list with the topics that are common to all of the rosbag files and the user-specified topic list.

        Raises:
            TopicNotFoundInBagError: If one or more topics from the user-specified topic list are not found in a rosbag
            file in the directory, this exception is raised.
        """
        try:
            file = None
            for file_obj in os.scandir(self.folder_path):
                if file_obj.name.endswith(".bag"):
                    with rosbag.Bag(file_obj.path) as bag:
                        topics = list(bag.get_type_and_topic_info().topics.keys())
                        different_topics = list(set(topic_list) - set(topics))
                        if different_topics:
                            raise TopicNotFoundInBagError
                        file = file_obj.name
            common_topics = list(set(topic_list).intersection(set(all_topics[0])))
            return common_topics

        except TopicNotFoundInBagError as e:
            if file is None:
                file = "any file"
            logging.error(f"{repr(e)}: Topics {different_topics} not found in {file}")
            sys.exit(1)

    def parse_rosbags(self, topics=None, save_csv=True):
        """
        Given a list of topics, this method opens every rosbag in a folder path and saves the data for every
        topic in the list.

        Args:
            topics (list): A list of topics to save the data for each .bag file.
            save_csv (boolean): Optional variable for saving the dataframe in a .csv file.

        Returns:
            None.
        """
        topics = topics or self.topics_to_parse
        for bag_file in os.scandir(self.folder_path):
            if bag_file.name.endswith(".bag") and bag_file.is_file():
                df = pd.DataFrame(columns=topics)
                with rosbag.Bag(bag_file.path) as bag:
                    rows = self._extract_rows_from_bag(bag, topics)
                    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                if save_csv:
                    filename = os.path.splitext(bag_file.name)[0]
                    self._save_df_to_csv(df, filename)

    def _extract_rows_from_bag(self, bag, topics):
        """
        Extracts rows of data from a ROS bag file.

        Args:
            bag (rosbag.Bag): The ROS bag file object to extract data from.
            topics (list of str): The list of topics to extract messages from.

        Returns:
            list of dict: A list of dictionaries, where each dictionary corresponds to a row of data
            extracted from the ROS bag file. The keys of each dictionary are the topic names and the
            "Timestamp" key represents the message timestamp.
        """
        rows = []
        for topic, msg, t in bag.read_messages(topics=topics):
            row = {col_topic: None for col_topic in topics}
            row[topic] = msg
            row["Timestamp"] = t
            rows.append(row)
        return rows

    def _save_df_to_csv(self, df, filename):
        """
        Saves a Pandas DataFrame to a CSV file.

        Args:
            df (pandas.DataFrame): The DataFrame to save to a CSV file.
            filename (str): The name of the output CSV file, without the extension.

        Returns:
            None
        """
        csv_path = os.path.join(self.folder_path, f"{filename}.csv")
        df.to_csv(csv_path, index=True)


def main():
    try:
        if len(sys.argv) <= 1:
            logging.error(
                "Please provide the path to the rosbag folder when running the script. \nExample:"
                " python3 rosbag_parser.py /path/to/rosbag_folder"
            )
            sys.exit(1)
        folder_path = sys.argv[1]
        parser = RosbagParser(folder_path)
        while True:
            topics = input(
                "Enter the topics you want to parse (separate multiple topics with space or type"
                " all): "
            )
            topics = topics.lower().split()
            if all(topic.startswith("/") for topic in topics) or topics[0] == "all":
                break
            logging.error("Error: All topics must start with '/'")
        # Check the topics
        parser.get_topics(topics)
        # Parse rosbags
        parser.parse_rosbags()

    except KeyboardInterrupt:
        print("\n")
        logging.error("Program interrupted by user")


if __name__ == "__main__":
    main()
