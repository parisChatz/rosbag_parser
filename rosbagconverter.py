import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import rosbag_parser as rp
import os
import sys

class RosbagConverter:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("guis/guiv1.glade")
        self.builder.connect_signals(self)
        self.label = self.builder.get_object("label_path")

    def on_button_path_file_set(self, widget):
        self.path = widget.get_file().get_path()
        self.label.set_text(f"Selected file path:\n {self.path}") 
        self.rp_instance = rp.RosbagParser(os.path.normpath(self.path))

    def on_button_get_topics_clicked(self, widget):
        try:
            self.rp_instance.get_topics(["all"])
            self.label.set_text(f"Common topics on all rosbags to convert:\n{self.rp_instance.topics_to_parse}")
        except AttributeError:
            self.label.set_text("First select folder with rosbags!")

    def on_button_convert_clicked(self, widget):
        try:
            self.rp_instance.parse_rosbags()
            self.label.set_text("Conversion Complete!")
            sys.exit(1)

        except AttributeError:
            self.label.set_text("Select folder of rosbags and get topics first!")

    def on_main_window_destroy(self, widget):
        gtk.main_quit()

    def run(self):
        window = self.builder.get_object("main_window")
        window.show_all()
        gtk.main()

if __name__ == "__main__":
    converter = RosbagConverter()
    converter.run()