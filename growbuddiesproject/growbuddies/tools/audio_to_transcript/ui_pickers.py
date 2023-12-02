import threading
import wx

def _pick_directory(stop_event, shared_data):
    app = wx.App(False)  # Create a new app
    dialog = wx.DirDialog(None, "Select a folder:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
    if dialog.ShowModal() == wx.ID_OK:
        shared_data['transcript_folder'] = dialog.GetPath()
    dialog.Destroy()
    app.ExitMainLoop()
    stop_event.set()

def _pick_file(stop_event, shared_data):
    app = wx.App(False)
    dialog = wx.FileDialog(None, "Choose the mp3 file", wildcard="*.mp3",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)    
    if dialog.ShowModal() == wx.ID_OK:
        shared_data['mp3_filename'] = dialog.GetPath()
    dialog.Destroy()
    app.ExitMainLoop()
    stop_event.set()


def pick_directory():
    shared_data = {}
    stop_event = threading.Event()
    thread = threading.Thread(target=_pick_directory, args=(stop_event, shared_data,))
    thread.start()
    thread.join() # Wait until the dialog box is done.
    return shared_data['transcript_folder']

def pick_file():
    shared_data = {}
    stop_event = threading.Event()
    thread = threading.Thread(target=_pick_file, args=(stop_event, shared_data,))
    thread.start()
    thread.join() # Wait until the dialog box is done.
    return shared_data['mp3_filename']