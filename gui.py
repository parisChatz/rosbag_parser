import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

class Window:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("guis/guiv1.glade")
        self.builder.connect_signals(self)

        
    # Callback for when the button is clicked
    def on_button_topics_clicked(self, widget):
        print("Topics clicked")

    def on_button_get_topics_clicked(self, widget):
        print("get topics")

    def on_button_convert_clicked(self, widget):
        print("I convert")

    def on_button_path_file_set(self, widget):
        # Get the path of the selected file
        self.path = widget.get_file().get_path()
        # Handle the path selection event here
        print("Selected file path: ", self.path)

    def on_main_window_destroy(self, widget):
        gtk.main_quit()

    def run(self):
        window = self.builder.get_object("main_window")
        window.show_all()
        gtk.main()

if __name__ == "__main__":
    Window().run()