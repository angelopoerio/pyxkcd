#! /usr/bin/env python

'''
Copyright (C) pyxkcd  Angelo Poerio <angelo.poerio@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import os
import urllib
import re
import sys
import threading
import gtk

gtk.gdk.threads_init()

class multiThread_Retrieve(threading.Thread):

	def __init__(self,status_widget,image_widget,comic_number):
		threading.Thread.__init__(self)
		self.status_widget = status_widget
		self.image_widget = image_widget
		self.comic_number = comic_number

	def get(self):
		s = re.compile("^Image URL")

		gtk.gdk.threads_enter()
		self.status_widget.push(1,"Downloading comic...")
		gtk.gdk.threads_leave()

		try:
			if self.comic_number is None:
				ln = urllib.urlopen("http://dynamic.xkcd.com/random/comic/")
			else:
				ln = urllib.urlopen("http://xkcd.com/"+self.comic_number)
				

			if ln.getcode() == 404:
				gtk.gdk.threads_enter()
				self.status_widget.push(1,"Error - could not get comic")
				warn_dlg = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,message_format="comic not found!",buttons=gtk.BUTTONS_OK)
				warn_dlg.set_icon(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))  			
				warn_dlg.run()
				warn_dlg.destroy()
				gtk.gdk.threads_leave()
				
			else:	
				for line in ln.readlines():
					if s.match(line):
						found_flag = True
						url_final = line.replace("Image URL (for hotlinking/embedding): ", "")

						url_parts = url_final.split("/")
						image_path = os.getenv("HOME") + "/.pyxkcd/" + url_parts[len(url_parts)-1]
						image_path = image_path.replace("?","")
						image_path = image_path.replace("&","")
						image_path = image_path.rstrip("\n")
						image_path = image_path.rstrip("\r")

						if not os.path.exists(os.getenv("HOME")+"/.pyxkcd"):
							os.mkdir(os.getenv("HOME")+"/.pyxkcd")

						fl = open(image_path,"w")
					
					
						lp = urllib.urlopen(url_final)
						fl.write(lp.read())
						fl.close()
						pixbuf = gtk.gdk.PixbufAnimation(image_path)
					
						gtk.gdk.threads_enter()
						self.image_widget.set_from_animation(pixbuf)
						url_final = url_final.rstrip('\n')	
						url_final = url_final.rstrip('\r')
						self.status_widget.push(1,"Done - "+url_final)
						gtk.gdk.threads_leave()
				
		except:
			gtk.gdk.threads_enter()
			self.status_widget.push(1,"Error connecting or writing temp files!")
			gtk.gdk.threads_leave()

		
	def run(self):
		self.get()
		

class xkcd:

	def getRand(self):
		multiThread_Retrieve(self.status,self.image,None).start()


	def close_app(self,widget):
		os.unlink("tmp/tmp.png")
		gtk.main_quit()
		return False

	def InputBox(self,title, label, parent, text=''):
    		dlg = gtk.Dialog(title, parent, gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK, gtk.RESPONSE_OK,gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		dlg.set_icon(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))    		
		lbl = gtk.Label(label)
    		lbl.show()
    		dlg.vbox.pack_start(lbl)
    		entry = gtk.Entry()
    		if text: 
			entry.set_text(text)
    		
		entry.show()
    		dlg.vbox.pack_start(entry, False)
    		resp = dlg.run()
    		text = entry.get_text()
    		dlg.hide()
    		
		if resp == gtk.RESPONSE_CANCEL:
			return None
		
		return text

	def get_comic_from_number(self,widget):
		number = self.InputBox('Enter comic\'s number','Number:',None)

		if number is not None:
			try:
				check = int(number)
				multiThread_Retrieve(self.status,self.image,number).start()
			except:
				err_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,message_format="Not a number!",buttons=gtk.BUTTONS_OK)
				err_dlg.set_icon(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))  			
				err_dlg.run()
				err_dlg.destroy()
				

	def delete_event(self, widget, event, data=None):
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()	

	def update(self,widget):
		self.getRand()

	def open_old_comics(self,widget):
		if not os.path.exists(os.getenv("HOME")+"/.pyxkcd"):
			warn_dlg = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,message_format="you have not yet saved comics!",buttons=gtk.BUTTONS_OK)
			warn_dlg.set_icon(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))  			
			warn_dlg.run()
			warn_dlg.destroy()
		else:
			dialog = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			dialog.set_current_folder(os.getenv("HOME")+"/.pyxkcd")
			response = dialog.run()
			if response == gtk.RESPONSE_OK:
				self.image.set_from_animation(gtk.gdk.PixbufAnimation(dialog.get_filenames()[0]))
			dialog.destroy()


	def about(self,widget):
		about = gtk.AboutDialog()
        	about.set_program_name("pyxkcd")
        	about.set_version("0.0.3")
        	about.set_copyright("(c) Angelo Poerio")
        	about.set_comments("pyxkcd is a simple reader for http://xkcd.com comics")
        	about.set_website("http://pyxkcd.sourceforge.net")
		about.set_authors(["Angelo Poerio <angelo.poerio@gmail.com>"])
		about.set_icon(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))
		about.set_license('''
Copyright (C) pyxkcd  Angelo Poerio <angelo.poerio@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
		''')

        	about.set_logo(gtk.gdk.pixbuf_new_from_file("pics/icon.png"))
        	about.run()
        	about.destroy()

	def __init__(self):
		builder = gtk.Builder()
	   	builder.add_from_file("xml/xkcd.glade")
		self.window = builder.get_object("window1")
		self.window.set_title("pyxkcd")
		self.window.set_icon_from_file("pics/icon.png")
		self.window.set_size_request(800, 600)
        	self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.connect("destroy", self.destroy)
		self.window.connect("delete_event", self.delete_event)
		self.status = builder.get_object("statusbar1")
		self.scrolled = builder.get_object("scrolledwindow1")
		self.image = gtk.Image()
		self.image.show()
		self.scrolled.add_with_viewport(self.image)
		self.image.set_from_animation(gtk.gdk.PixbufAnimation("pics/icon.png"))
		self.about_menu_item = builder.get_object("imagemenuitem10")
		self.about_menu_item.connect("activate",self.about)
		self.open_menu_item = builder.get_object("imagemenuitem7")
		self.open_menu_item.connect("activate",self.open_old_comics)
		self.refresh_menu_item = builder.get_object("imagemenuitem6")
		self.refresh_menu_item.connect("activate",self.update)
		self.quit_menu_item = builder.get_object("imagemenuitem5")
		self.quit_menu_item.connect("activate",self.destroy)
		self.get_comic_menu_item = builder.get_object("imagemenuitem8")
		self.get_comic_menu_item.connect("activate",self.get_comic_from_number)
		self.window.show()

	def start(self):
		gtk.main()

app = xkcd()
app.start()
