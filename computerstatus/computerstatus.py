#!/usr/bin/python
"""
Show status from a bunch of computers.
We actively connect to a specific address, and then we get updates sent by all computers to a server running there, which just
echos stuff to us.


<KNOWN COMPUTER> ---> <Display Computer == Us>
 ^
 |
<Remote A>
"""

import os
import gtk
import gobject, socket
import json

from defines import REMOTES_SERVER_HOST as HOST
from defines import OUT_SERVER_PORT as PORT
 
class RemotesStatusIcon(gtk.StatusIcon):
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menuitem action="Remotes"/>
              </menu>
             </menubar>
            </ui>
        '''
        actions = [
            ('Menu',  None, 'Menu'),
            ('Remotes', None, '_Remotes', None, 'Show Remote Computers', self.on_show_remotes)]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/Remotes').props.parent
        self.set_tooltip('Remotes: none yet')
        self.set_from_stock(gtk.STOCK_FIND)
        self.set_visible(True)
        self.connect('activate', self.on_show_remotes)
        self.connect('popup-menu', self.on_popup_menu)

        self._remotes = {}
        self._remotes_markup = 'none yet'
        self.start_connecting()

    def start_connecting(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print "connecting.."
        sock.connect((HOST, PORT))
        print "connected"
        gobject.io_add_watch(sock, gobject.IO_IN, self.handler)

    def handler(self, conn, *args):
        '''Asynchronous connection handler. Processes each line from the socket.'''
        print "handler"
        line = conn.recv(4096)
        if not len(line):
            print "Connection closed."
            return False
        print "got line %r" % line
        for l in line.split('\n'):
            if l.strip() == '': continue
            try:
                remotes = json.loads(l)
            except:
                print "not json: %r" % l
        self.update_remotes(remotes)
        return True

    def update_remotes(self, remotes):
        self._remotes = remotes
        self._remotes_markup = '<tt>' + '\n'.join(
            '%s%s' % (host.ljust(30), ip.ljust(30)) for host, ip in self._remotes.items())\
                + '</tt>'
        self._remotes_text = '\n'.join(
            '%s%s' % (host.ljust(30), ip.ljust(30)) for host, ip in self._remotes.items()) + '\n'
        with open(os.path.expanduser('~/.remotes.hosts'), 'w+') as f:
            f.write(self._remotes_text)
        self.set_tooltip_markup(self._remotes_markup)
     
    def on_show_remotes(self, data):
        dialog = gtk.AboutDialog()
        dialog.set_name('Remotes')
        #dialog.set_version('0.5.0')
        dialog.set_comments(self._remotes_text)
        #dialog.set_website('www.freede')
        dialog.run()
        dialog.destroy()

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

if __name__ == '__main__':
    RemotesStatusIcon()
    gtk.main()

