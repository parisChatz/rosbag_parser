import gi

gi.require_version("Gtk", "3.0")
import os

from gi.repository import Gtk as gtk

import rosbag_parser as rp


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

            popup = gtk.Window(title="Select topics")
            box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=10)
            popup.add(box)
            label = gtk.Label(label="Select the topics to save in csv:")
            box.pack_start(label, True, True, 0)

            for topic in self.rp_instance.topics_to_parse:
                check_button = gtk.CheckButton(label=topic)
                box.pack_start(check_button, True, True, 0)

            button_box = gtk.ButtonBox(orientation=gtk.Orientation.HORIZONTAL)
            box.pack_start(button_box, True, True, 0)

            ok_button = gtk.Button(label="OK")
            button_box.pack_start(ok_button, True, True, 0)
            ok_button.connect("clicked", self.on_popup_ok_clicked, popup)

            all_button = gtk.Button(label="All")
            button_box.pack_start(all_button, True, True, 0)
            all_button.connect("clicked", self.on_popup_all_clicked)
            popup.show_all()

        except AttributeError:
            self.label.set_text("First select folder with rosbags!")

    def on_popup_ok_clicked(self, button, popup):
        selected_topics = []
        box = popup.get_children()[0]
        for child in box.get_children():
            if isinstance(child, gtk.CheckButton) and child.get_active():
                selected_topics.append(child.get_label())

        if selected_topics:
            self.label.set_text("Topics selected.")
        else:
            self.label.set_text("Please select at least one topic.")

        self.selected_topics = selected_topics
        popup.hide()

        popup_topics_checked = gtk.Window(title="Selected topics")
        scrolled_window = gtk.ScrolledWindow.new()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=10)
        popup_topics_checked.set_size_request(350, 500)

        for topic in selected_topics:
            label = gtk.Label.new(topic)
            hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.pack_start(label, expand=True, fill=True, padding=0)
            vbox.pack_start(hbox, expand=False, fill=False, padding=0)

        scrolled_window.add(vbox)
        popup_topics_checked.add(scrolled_window)
        popup_topics_checked.show_all()

    def on_popup_all_clicked(self, button):
        selected_topics = self.rp_instance.topics_to_parse
        self.label.set_text("All topics selected.")
        self.selected_topics = selected_topics

        popup_topics_checked = gtk.Window(title="Selected topics")
        scrolled_window = gtk.ScrolledWindow.new()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=10)
        popup_topics_checked.set_size_request(350, 500)

        for topic in selected_topics:
            label = gtk.Label.new(topic)
            hbox = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.pack_start(label, expand=True, fill=True, padding=0)
            vbox.pack_start(hbox, expand=False, fill=False, padding=0)

        scrolled_window.add(vbox)
        popup_topics_checked.add(scrolled_window)
        popup_topics_checked.show_all()

        for window in gtk.Window.list_toplevels():
            if window.get_title() == "Select topics":
                window.destroy()

    def on_button_convert_clicked(self, widget):
        try:
            self.rp_instance.parse_rosbags(self.selected_topics)
            self.label.set_text("Conversion Complete!")

        except AttributeError:
            self.label.set_text("Select folder of rosbags and get topics first!")

    def on_main_window_destroy(self, widget):
        gtk.main_quit()

    def run(self):
        self.builder.get_object("main_window").show_all()
        gtk.main()


if __name__ == "__main__":
    RosbagConverter().run()
