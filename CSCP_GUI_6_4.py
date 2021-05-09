# TODO - fix paging menu
# color code faders red for mains / poss color labels
# fix display labels
# VCA master labels & icon
# get routing buttons working
# get L>B & R>B working
# menu for connection config
# menu to select which stips to display/filter
# menu to select which routing buttons to display
# snapshots
# sync to mixer vs mixer sync to UI

# NOTES:
# was difficult installing rtmidi into this project which is needed by mido
# Not sure what quite fixed it in the end, needed to deal with a wheel file, got confused with venv's
# https://spotlightkid.github.io/python-rtmidi/installation.html#requirements

# V6.4 - upgrading to mixer 2.1 to use midi input
# GOT MIDI INPUT FROM REAPER WORKING!!!
# Now, the output! - then real mixer with two way control CSCP <-> MIDI!


import sys

#from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QVBoxLayout, QHBoxLayout, QGridLayout, \
#     QWidget, QPushButton, QSlider, QLabel, QAction, QActionGroup

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, \
     QLabel, QSlider, QToolBar, QAction, QActionGroup

import CSCP_mixer_2_1 as CSCP_mixer


class Routing:

    def __init__(self, strip, mixer, bus_type, button_qty=8, pages=3):
        self.strip = strip
        self.mixer = mixer

        self.bus_type = bus_type
        self.pages = pages
        self.current_page = 0

        self.routing_widget = QWidget()
        self.routing_widget.setProperty("cssClass", ["routing"])
        layout = QGridLayout()
        self.routing_widget.setLayout(layout)

        label = QLabel(bus_type+str(' Routing'), alignment=Qt.AlignCenter)
        label.setProperty('cssClass', ['routing'])
        layout.addWidget(label, 0, 0, 1, 2)

        self.routing_btns = []
        row = 1
        col = 0
        for i in range(button_qty):
            btn = QPushButton(checkable=True)
            if self.bus_type == 'Main':
                btn.setProperty('cssClass', ['red'])

            elif self.bus_type == 'Aux':
                btn.setProperty('cssClass', ['green'])
            self.routing_btns.append(btn)
            layout.addWidget(btn, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        if self.pages > 1:
            self.page_down = QPushButton('<')
            self.page_up = QPushButton('>')

            self.page_down.clicked.connect(self.create_page_callback('down'))
            self.page_up.clicked.connect(self.create_page_callback('up'))

            layout.addWidget(self.page_down, row, col)
            layout.addWidget(self.page_up, row, col+1)

        self.set_routing_page(self.current_page)

    def next_page(self, direction):
        if direction == 'up':
            self.current_page += 1
            if self.current_page > self.pages - 1:
                self.current_page = self.pages - 1
        elif direction == 'down':
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = 0

        self.set_routing_page(self.current_page)

    def set_routing_page(self, page):
        for i in range(len(self.routing_btns)):
            bus = i + page*len(self.routing_btns)
            try:
                self.routing_btns[i].disconnect() # remove any currently connected callbacks
            except:
                print('could not disconnect routing button callbacks')

            self.routing_btns[i].clicked.connect(self.create_routing_button_callback(bus))
            self.routing_btns[i].setText(str(bus+1))

    def create_routing_button_callback(self, bus):

        if self.bus_type == 'Main':

            def routing_callback():
                if debug:
                    print(self.strip, '{} routing button {} press'.format(self.bus_type, bus))
                    print('DEBUG', self.strip, bus)
                self.mixer.toggle_main(self.strip, bus)
            return routing_callback

        elif self.bus_type == 'Aux':
            def routing_callback():
                if debug:
                    print(self.strip, '{} routing button {} press'.format(self.bus_type, bus))
                self.mixer.toggle_aux(self.strip, bus)
            return routing_callback

        else:
            return False

    def create_page_callback(self, direction):
        def paging_callback():
            print('page {} press'.format(direction))
            self.next_page(direction)

        return paging_callback

    def refresh(self):
        for i, button in enumerate(self.routing_btns):
            bus = i + self.current_page * len(self.routing_btns)

            if self.bus_type == 'Main':
                if self.mixer.strips[self.strip].m_routing[bus]:

                    self.routing_btns[i].setChecked(True)

                else:
                    self.routing_btns[i].setChecked(False)

            elif self.bus_type == 'Aux':
                if self.mixer.strips[self.strip].a_sends[bus]:

                    self.routing_btns[i].setChecked(True)

                else:
                    self.routing_btns[i].setChecked(False)

        # Disable the routing widget if the host path is of type Main or Aux
        if self.mixer.strips[self.strip].path_type:
            if 'Main' in self.mixer.strips[self.strip].path_type or 'Aux' in self.mixer.strips[self.strip].path_type:
                self.routing_btns[bus].setChecked(False)  # TODO - this is a hack, for some reason if the button is checked when set disabled, the active background is still displayed, even though text and border cleared by css
                                                          # for some reason this hack is only working on the main routing buttons, not aux routing... would need to apply to cut buttons as well
                                                          # should just figure out why CSS is not working as expected
                self.routing_widget.setDisabled(True)
            else:
                self.routing_widget.setDisabled(False)


class InputRouting:
    def __init__(self, strip, mixer):
        self.strip = strip
        self.mixer = mixer

        self.input_routing_widget = QWidget()
        self.input_routing_widget.setProperty("cssClass", ["input_routing"])
        layout = QGridLayout()
        self.input_routing_widget.setLayout(layout)

        self.label = QLabel('Input Routing', alignment=Qt.AlignCenter)
        self.l_to_b = QPushButton('L>B')
        self.r_to_b = QPushButton('R>B')

        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.l_to_b, 1, 0)
        layout.addWidget(self.r_to_b, 1, 1)

    def refresh(self):
        if self.mixer.strips[self.strip].path_width == 'Stereo':
            self.input_routing_widget.setDisabled(False)
        else:
            self.input_routing_widget.setDisabled(True)


class Display:
    def __init__(self, strip, mixer):
        self.strip = strip
        self.mixer = mixer

        self.display_widget = QWidget()
        self.display_widget.setProperty("cssClass", ['display'])
        layout = QVBoxLayout()
        self.display_widget.setLayout(layout)

        self.row1 = QLabel('row1', alignment=Qt.AlignCenter)
        self.row2 = QLabel('row2', alignment=Qt.AlignCenter)
        self.row3 = QLabel('row3', alignment=Qt.AlignCenter)

        self.row1.setProperty("cssClass", ['display'])
        self.row2.setProperty("cssClass", ['display'])
        self.row3.setProperty("cssClass", ['display'])

        layout.addWidget(self.row1)
        layout.addWidget(self.row2)
        layout.addWidget(self.row3)

    def refresh(self):
        self.row1.setText(str(self.mixer.strips[self.strip].label))
        self.row2.setText(str(self.mixer.strips[self.strip].path_width))
        self.row3.setText(str(self.mixer.strips[self.strip].path_type))


class Fader:
    def __init__(self, strip, mixer):

        self.strip = strip
        self.mixer = mixer

        self.fader_widget = QWidget()
        self.fader_widget.setProperty("cssClass", ["fader"])

        layout = QVBoxLayout()
        self.fader_widget.setLayout(layout)

        self.cut_btn = QPushButton('CUT', checkable=True, clicked=self.toggle_cut)
        self.pfl_btn = QPushButton('PFL', checkable=True, clicked=self.toggle_pfl)

        self.cut_btn.setProperty('cssClass', ['red'])
        self.pfl_btn.setProperty('cssClass', ['green'])

        self.fader = QSlider(maximum=1023, sliderMoved=self.move_fader)

        layout.addWidget(self.cut_btn)
        layout.addWidget(self.fader)
        layout.addWidget(self.pfl_btn)

    def toggle_cut(self):
        self.mixer.toggle_cut(self.strip)

    def toggle_pfl(self):
        self.mixer.toggle_pfl(self.strip)

    def move_fader(self):
        self.mixer.move_fader(self.strip, self.fader.value())

    def refresh(self):
        if self.mixer.strips[self.strip].pfl:
            self.pfl_btn.setChecked(True)
        else:
            self.pfl_btn.setChecked(False)

        if self.mixer.strips[self.strip].path_type and 'Main' in self.mixer.strips[self.strip].path_type:
            self.cut_btn.setDisabled(True)
        else:
            self.cut_btn.setDisabled(False)

        if self.mixer.strips[self.strip].cut:
            self.cut_btn.setChecked(False)  # Inverted display state, underlying data is On = 1 Cut = 0
        else:
            self.cut_btn.setChecked(True)

        self.fader.setValue(self.mixer.strips[self.strip].fader_level)


class Strip:

    def __init__(self, strip, mixer, parent_window=None):
        """
        :param parent_window:
        :param strip_data: Strip object from CSCP_mixer, usually passed as mixer.strips[i] referencing a CSCP_mixer.Mixer() object
        """
        self.strip_data = mixer.strips[strip]

        strip_widget = QWidget()
        strip_widget.setProperty("cssClass", ["strip"])

        strip_layout = QVBoxLayout()
        strip_widget.setLayout(strip_layout)

        strip_label = QLabel(str(self.strip_data.id + 1), alignment=Qt.AlignCenter)
        strip_label.setProperty('cssClass', ["strip"])
        strip_layout.addWidget(strip_label)

        self.main_routing = Routing(self.strip_data.id, mixer, 'Main', button_qty=4, pages=1)
        self.aux_routing = Routing(self.strip_data.id, mixer, 'Aux')
        self.input_routing = InputRouting(self.strip_data.id, mixer)
        self.display = Display(self.strip_data.id, mixer)
        self.fader = Fader(self.strip_data.id, mixer)

        strip_layout.addWidget(self.main_routing.routing_widget)
        strip_layout.addWidget(self.aux_routing.routing_widget)
        strip_layout.addWidget(self.input_routing.input_routing_widget)
        strip_layout.addWidget(self.display.display_widget)
        strip_layout.addWidget(self.fader.fader_widget)

        parent_window.addWidget(strip_widget)

    def refresh(self):
        self.display.refresh()
        self.input_routing.refresh()
        self.main_routing.refresh()
        self.aux_routing.refresh()
        self.fader.refresh()


class BaseView(QWidget):
    """ The main view window for the GUI """

    def __init__(self, mixer):
        """
        :param mixer: a CSCP_mixer.Mixer() object - Back end data model and comms handling with a physical mixer
        :param faders:
        """
        super().__init__()

        #faders = faders.split('-')
        #self.faders = range(int(faders[0]) - 1, int(faders[1]))

        header_area = QVBoxLayout()
        self.setLayout(header_area)

        self.header = QLabel('Page heading', alignment=Qt.AlignCenter)
        self.sub_header = QLabel('some text', alignment=Qt.AlignCenter)

        header_area.addWidget(self.header)
        header_area.addWidget(self.sub_header)

        self.strips_area = QHBoxLayout()
        self.layout().addLayout(self.strips_area)

        #self.strip1 = Strip(0, mixer, self.strips_area)
        #self.strip2 = Strip(1, mixer, self.strips_area)
        #self.strip3 = Strip(2, mixer, self.strips_area)
        #self.strip4 = Strip(3, mixer, self.strips_area)
        #self.strip5 = Strip(4, mixer, self.strips_area)
        #self.strip6 = Strip(5, mixer, self.strips_area)

    def refresh(self):
        self.strip1.refresh()
        self.strip2.refresh()
        self.strip3.refresh()
        self.strip4.refresh()
        self.strip5.refresh()
        self.strip6.refresh()


class FaderView(BaseView):
    def __init__(self, mixer, first=1, last=12):
        super().__init__(mixer)
        self.strips = []

        for i in range(first-1, last):
            self.strips.append(Strip(i, mixer, self.strips_area))

    def refresh(self):
        for strip in self.strips:
            strip.refresh()


class AuxOutputView(BaseView):
    def __init__(self):
        super().__init__()


class MainOutputView(BaseView):
    def __init__(self):
        super().__init__()


class MainNavButtonGroup(QActionGroup):

    def __init__(self, toolbar, views, active_view):
        super().__init__(toolbar)

        for view in views:
            action = QAction(view, checkable=True)
            if view == active_view:
                action.setChecked(True)
            self.addAction(action)
            toolbar.addAction(action)


class SubNavButtons(QActionGroup):
    def __init__(self, toolbar, entries, active_entry):
        super().__init__(toolbar)
        for entry in entries:
            action = QAction(entry, checkable=True)
            if entry == active_entry:
                action.setChecked(True)
            self.addAction(action)
            toolbar.addAction(action)


class ViewMenu(QToolBar):
    # Class to use for each main view
    views = (FaderView, AuxOutputView, MainOutputView)
    view_labels = ('Faders', 'Aux Outputs', 'Mains')

    subviews = {FaderView: ('1-12', '13-24', '25-36'),
                AuxOutputView: ('1-8', '9-16', '17-24'),
                MainOutputView: ('1-4',),
                }

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.current_view = FaderView
        self.current_subviews = {FaderView: ViewMenu.subviews[FaderView][0],
                                 AuxOutputView: ViewMenu.subviews[AuxOutputView][0],
                                 MainOutputView: ViewMenu.subviews[MainOutputView][0],
                                 }

        self.main_view_menu = MainNavButtonGroup(self, ViewMenu.view_labels, ViewMenu.view_labels[0])

        self.sub_view_menu = SubNavButtons(self, ViewMenu.subviews[ViewMenu.views[0]], self.current_subviews[ViewMenu.views[0]])

        for action in self.main_view_menu.actions():
            # Rather than just calling a function with no params, create a bespoke function for each button
            action.triggered.connect(self._create_mainview_button_callback(action))

        for action in self.sub_view_menu.actions():
            # Rather than just calling a function with no params, create a bespoke function for each button
            action.triggered.connect(self._create_subview_button_callback(action))

    def _create_mainview_button_callback(self, actionx): # todo wanted to use 'action' here but would not work so apended x, outside scope?
        def _mainview_button_callback():

            view_class = ViewMenu.views[ViewMenu.view_labels.index(actionx.text())]
            self.current_view = view_class
            view = view_class(self.current_subviews[view_class])
            self.parent_window.setCentralWidget(view)   # Apply view to main window. Note, this destroys the previouos
                                                        # view, so currently creating new view from scratch on each
                                                        # change rather than holding them all in memory

            # Remove individual existing sub-menu actions from toolbar (Don't seem to be able to remove the group,
            # and re-instantiating the group will add extra buttons rather than replace)
            for button in self.sub_view_menu.actions():
                self.removeAction(button)
            # Create a toolbar action group containing the appropriate submenus
            self.sub_view_menu = SubNavButtons(self, ViewMenu.subviews[view_class], self.current_subviews[view_class]) # then add the new submenu
            for action in self.sub_view_menu.actions():
                action.triggered.connect(self._create_subview_button_callback(action))

        return _mainview_button_callback

    def _create_subview_button_callback(self, action):
        """ Creates and returns a function that can be called later
            Allows a e.g. a button press to call a function with params / tailored to the specific button
        """
        def _subview_button_callback():
            view_class = self.current_view
            #view = view_class(self.parent_window.mixer, act)
            self.current_subviews[view_class] = action.text()
            self.parent_window.setCentralWidget(view)

        return _subview_button_callback


class CscpGui(QMainWindow):
    """ Main Window.
        Subclass of QMainWindow to setup the GUI
    """
    def __init__(self, mixer):
        super().__init__()
        self.mixer = mixer
        # Set some main window's properties
        self.setWindowTitle('MixR')
        #self.mixer = mixer
        #self.main_view = BaseView(self.mixer, '1-12')
        #self.setCentralWidget(self.main_view)

        #main_view = BaseView(mixer)
        main_view = FaderView(mixer)

        self.setCentralWidget(main_view)

        self.addToolBar(ViewMenu(self))

        # Set up timer to periodically call my refresh code
        self.timerval = 0  # debug - timer loop counter
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(REFRESH_RATE)
        self.refresh_timer.timeout.connect(self.refresh_gui)
        self.refresh_timer.start()

    def update_status(self):
        status_text = str(self.timerval) + ' | ' + self.mixer.connection.status + ' to ' + self.mixer.connected_mixer_name

        if self.mixer.connection.status == 'Connection Lost!':
            self.statusBar().setStyleSheet("background-color:#a00; color:white;")

        elif self.mixer.connection.status == 'Not Connected':
            self.statusBar().setStyleSheet("background-color:#444; color:#aaa;")

        else:
            # trying to connect
            self.statusBar().setStyleSheet("background-color:#444; color:#aaa;")
            status_text += ' on ' + self.mixer.connection.address + ' Port ' + str(self.mixer.connection.port)

        self.statusBar().showMessage(status_text)  # TODO - show connection status and ping?

        # TODO - set heartbeat if connected, on RHS

    def refresh_gui(self):
        self.timerval += 1
        self.mixer.process_messages()  # TODO - think about moving this to a thread in mixer
        self.centralWidget().refresh()
        self.update_status()


def main(mixer, qss):
    """
    :param mixer: CSCP_mixer.Mixer object
    :param qss:
    """
    # Create an instance of QApplication
    cscp_app = QApplication(sys.argv)

    # Load qss style sheet
    try:
        with open(qss, "r") as fh:
            cscp_app.setStyleSheet(fh.read())
    except FileNotFoundError:
        print("I'm naked! (stylesheet not found. Expecting a file named {} in the same folder as this file)".format(qss))

    # Create a QMainWindow for a Mixer
    view = CscpGui(mixer)
    # Show it
    view.show()
    # Execute the GUI's main loop and handle the exit
    sys.exit(cscp_app.exec_())


def set_debug_mode():
    """ Enable debug mode (additional print statements) if file is run with argument "debug" passed
        I.E. from terminal - 'python CSCP_GUI.py debug'
        :return: bool
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        return True
    return False


if __name__ == '__main__':

    qss = 'CSCP_style_1_1.qss'  # External style sheet to use

    REFRESH_RATE = 200  # Timer value in ms to periodically refresh the gui
    # Refreshing too frequently causes fader adjustments to conflict. 100 is a good number to use.

    # Connection info for my physical mixer
    mixer_IP_address = "192.169.1.200"
    TCP_port = 12345

    fader_qty = 36  # TODO - read back from mixer or allow user choice?

    # Create back-end data model with a comms interface with a physical mixer
    mixer = CSCP_mixer.Mixer(mixer_IP_address, TCP_port, fader_qty)

    debug = set_debug_mode()
    main(mixer, qss)  # Run the GUI
