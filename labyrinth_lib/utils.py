# functions.py
# This file is part of labyrinth
#
# Copyright (C) 2006 - Don Scorgie
#                    - Andreas Sliwka
#
# labyrinth is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# labyrinth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Labyrinth; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301  USA
#

# This file defines various useful functions
# that can be accessed from anywhere :)

import sys
from os.path import join, dirname, exists, isdir, isfile
import os
import warnings
try:
    from xdg import BaseDirectory
except ImportError:
    if os.name != 'nt':
        raise

__BE_VERBOSE=os.environ.get('DEBUG_LABYRINTH',0)
if __BE_VERBOSE:
    def print_debug(*data):
        sys.stderr.write("\n".join(data) + "\n")
else:
    def print_debug(*data):
        pass

# FIXME: this is a no-go, but fast and efficient
# global variables
use_bezier_curves = False
default_colors = {
        "text" : (0.0, 0.0, 0.0),
        "fg" : (0.0, 0.0, 0.0),
        "bg" : (0.0, 0.0, 0.0),
        "base" : (0.0, 0.0, 0.0)
        }

selected_colors = {
        "text" : (0.0, 0.0, 0.0),
        "fg" : (0.0, 0.0, 0.0),
        "bg" : (0.0, 0.0, 0.0),
        "border" : (0.0, 0.0, 0.0),             # bounding box
        "fill" : (0.0, 0.0, 0.0)                # bounding box
        }

default_font = None

def get_save_dir ():
    ''' Returns the path to the directory to save the maps to '''
    if os.name == 'nt':
        savedir = os.path.join(os.path.expanduser('~'), '.labyrinth')
        if not os.access (savedir, os.W_OK):
            os.makedirs (savedir)
        return savedir
    
    old_savedir = os.path.join (os.path.expanduser('~'), ".gnome2", "labyrinth")
    savedir = BaseDirectory.save_data_path("labyrinth")
    
    # Migrate maps to the new save directory.   
    if os.path.exists(old_savedir) and os.path.isdir(old_savedir):
        
        for m in os.listdir(old_savedir):
            try:
                os.rename(os.path.join(old_savedir, m),
                        os.path.join(savedir, m))
            except Exception as e:
                warnings.warn("Failed to migrate %s: %s" % (m, e))
        
        # remove old dir
        try:
            os.rmdir(old_savedir)
        except Exception as e:
            warnings.warn("Could not remove old map dir (%s): %s" % (old_savedir, e))
    
    return savedir

def get_images_dir ():
    return os.path.join(get_save_dir(), 'images')

def parse_coords (string):
    if string == "None":
        return None
    local = string[1:string.find(',')]
    local_2 = string[string.find (',')+1:string.find(')')]
    coord = (float(local),  float(local_2))
    return coord

__data_dir = None

def get_data_dir():
    '''returns the data dir. Tries to find it the first time its called'''
    global __data_dir
    if __data_dir is not None:
        return __data_dir

    #decide wether we run under development or if the program has been installed
    path = join(dirname(__file__), '..')
    if isdir(path) and isfile(join(path, "AUTHORS")):
        # Running in development
        __data_dir = join(path , 'data')

    else:
        # Running installed
        if os.name != 'nt':
            __data_dir = "/usr/share/labyrinth"
        else:
            __data_dir = join(dirname(sys.argv[0]),"data")
    return __data_dir

def get_data_file_name (file_name):
    ''' takes a string and returns it with the data directory prepended.'''
    return os.path.join(get_data_dir(), file_name)

def get_data_file (file_name):
    ''' takes a string and either returns a data file of that name or raises an exception if it cant find it '''
    return open(get_data_file_name(file_name))

# Drawing functions

# These are thought outline styles.
# Currently, there is only 1 - STYLE_NORMAL, which is the slightly rounded corners
# - The normal thought type
STYLE_NORMAL = 0
STYLE_EXTENDED_CONTENT = 1

def draw_thought_outline (context, ul, lr, background_color, am_root = False, am_primary = False, style=STYLE_NORMAL):
    draw_thought_extended(context, ul, lr, am_root, am_primary, background_color, style == STYLE_EXTENDED_CONTENT)

# This is used to find the required margin from the (real) ul / lr coords to the edge of the
# box area.  Makes selection of thoughts less erratic
def margin_required (style = STYLE_NORMAL):
    if style == STYLE_NORMAL:
        return margin_thought_classic ()
    else:
        print ("Error: Unknown thought margine style: "+str(style))

# Classic thought style drawing code
def margin_thought_classic ():
    return (5, 5, 5, 5)

def gtk_to_cairo_color(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0)

def draw_thought_extended (context, ul, lr, am_root, am_primary, background_color, fatborder=False, dashborder=False):
    context.move_to (ul[0], ul[1]+5)
    context.line_to (ul[0], lr[1]-5)
    context.curve_to (ul[0], lr[1], ul[0], lr[1], ul[0]+5, lr[1])
    context.line_to (lr[0]-5, lr[1])
    context.curve_to (lr[0], lr[1], lr[0], lr[1], lr[0], lr[1]-5)
    context.line_to (lr[0], ul[1]+5)
    context.curve_to (lr[0], ul[1], lr[0], ul[1], lr[0]-5, ul[1])
    context.line_to (ul[0]+5, ul[1])
    context.curve_to (ul[0], ul[1], ul[0], ul[1], ul[0], ul[1]+5)
    if am_root:
        bg = selected_colors["bg"]
        context.set_source_rgb (bg[0], bg[1], bg[2])
    elif am_primary:
        context.set_source_rgb (0.937, 0.831, 0.000)
    else:
        r,g,b = gtk_to_cairo_color(background_color)
        context.set_source_rgb (r, g, b)
    context.fill_preserve ()
    context.set_source_rgb (0,0,0)
    if dashborder:
        context.set_dash([4.0], 0.0)
    if fatborder:
        orig_line_width = context.get_line_width ()
        context.set_line_width (5.0)
        context.stroke ()
        context.set_line_width (orig_line_width)
    else:
        context.stroke ()

    if dashborder:
        context.set_dash([], 0.0)

# Export outline stuff
def export_thought_outline (context, ul, lr, background_color, am_root = False, am_primary = False, style=STYLE_NORMAL, move=(0,0)):
    real_ul = (ul[0]+move[0], ul[1]+move[1])
    real_lr = (lr[0]+move[0], lr[1]+move[1])
    draw_thought_extended (context, real_ul, real_lr, False, am_primary, background_color, style == STYLE_EXTENDED_CONTENT)
