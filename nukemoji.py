


from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


import json
import nuke
import os
with open('/Users/donaldstrubler/PycharmProjects/nukemoji/eac.json') as f:
    data = json.load(f)

data.keys()



class Emoji(QWidget):
    def __init__(self):
        super(Emoji, self).__init__()

        self.base = "/Users/donaldstrubler/PycharmProjects/nukemoji"
        self.eac_json = "%s/eac.json" %self.base

        self.map = None
        self.load_eac_json()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("emoji search")
        self.search_bar.setMinimumHeight( 27 )

        self.size_button = QToolButton()
        self.size_button.setIcon( QIcon( QPixmap( "%s/img/128.png" %self.base ) ) )
        self.size_button.setIconSize( QSize( 24,24) )

        self.tone_button = QToolButton()
        #self.tone_button.setText( 'tone' )
        self.tone_button.setIcon( QIcon( QPixmap( self.get_path_from_keyword( "raised_hand" ) ) ) )
        self.tone_button.setIconSize( QSize( 24,24) )
        self.tone_menu = QMenu()
        self.tones = {}
        for i in range(5):
            c = i+1
            self.tones['act_%03d' %c] = QAction(self.tone_menu)

            self.tones['act_%03d' %c].setText(str(c))
            self.tones['act_%03d' %c].setIcon( QIcon( QPixmap( self.get_path_from_keyword( 'tone%01d' %c ) ) ) )
            self.tone_menu.addAction( self.tones['act_%03d' %c])

        self.tone_button.setMenu( self.tone_menu )

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget( self.search_bar )
        self.top_layout.addWidget( self.tone_button )
        self.top_layout.addWidget( self.size_button )

        self.master_layout = QVBoxLayout()
        self.master_layout.setContentsMargins( 0,0,0,0 )
        self.master_layout.setSpacing( 1 )
        self.setLayout( self.master_layout )

        self.master_layout.addLayout( self.top_layout )


        self.search_bar.textChanged.connect( self.filter_list )
        self.search_bar.returnPressed.connect( self.close )
        self.tone_menu.triggered.connect( self.set_tone_button )

        self.tone = None

        self.window = QListWidget()
        #self.window.setViewMode(QListWidget.IconMode)

        self.window.setAttribute(Qt.WA_TranslucentBackground)
        #self.window.setStyleSheet( "background:rgba(20,20,20,90);" )
        self.window.setIconSize( QSize( 32,32 ) )
        for k in sorted(self.map.keys() ):
            it = QListWidgetItem(k.replace(":", ''))
            ip = QPixmap(self.get_path_from_keyword(k.replace(":", '')))
            ip.scaledToHeight(32, Qt.SmoothTransformation)
            ic = QIcon( ip )
            it.setIcon( ic )
            it.setSizeHint(QSize(0,35) )
            it.setBackground( QBrush( QColor( 100,100,100,20 )  ) )
            self.window.addItem(it)


        self.master_layout.addWidget( self.window)

        self.em = {}
        self.set_tone(3)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground )

        self.window.itemDoubleClicked.connect( self.create_icon )

    def set_tone_button(self, action):

        t = int( action.text())
        self.set_tone(t)
        self.tone_button.setIcon( QIcon( QPixmap( self.get_path_from_keyword( "raised_hand_tone%01d" %t ) ) ) )
        self.filter_list()

    def set_tone(self, int):
        if int:
            if int > 0 and int < 6:
                self.tone = int

    def load_eac_json(self):
        with open(self.eac_json) as f:
            data = json.load(f)
            emoji_exists = [p.replace('.png', '') for p in os.listdir( "%s/lib_64" %self.base )]
            self.map = dict((str(v['alpha_code']), str(v['output'])) for k, v in data.iteritems() if str(v['output']) in emoji_exists )

    def get_path_from_keyword(self, word):
        return "%s/lib_128works/%s.png" %(self.base, self.map[":%s:" %word])

    def find_within_keywords(self, word):
        return [l for l in self.map.keys() if word in l]

    def filter_list(self):
        self.search_bar.setText(self.search_bar.text().replace(" ", '_'))
        phrase = self.search_bar.text()

        for i in range(self.window.count()):
            self.window.setItemHidden(self.window.item(i), True)
            item_txt = self.window.item(i).text()

            if phrase in item_txt :
                if "_tone" in item_txt:
                    if self.tone:
                        if "_tone%01d" %self.tone in item_txt:
                            self.window.setItemHidden(self.window.item(i), False)
                    else:
                        pass
                else:
                    self.window.setItemHidden(self.window.item(i), False)



    def create_icon(self, selection):
        if not selection:
            name = self.window.currentItem().text()
        else:
            name = selection.text()
        if len(nuke.selectedNodes())>0:
            for n in nuke.selectedNodes():
                n['icon'].setValue(self.get_path_from_keyword(name))

        else:
            ic = nuke.createNode( "Dot" )
            ic['hide_input'].setValue( True )
            ic['icon'].setValue( self.get_path_from_keyword( name) )
        self.close()