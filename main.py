#!/usr/bin/python

import urwid
import copy
import random
import sys
import threading



palette = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', 'black', 'dark red'),
    ('dead', 'black', 'light gray'),
    ('live', 'white', 'dark red'),
    ('bg1', '', '', '', 'g7', '#60a'),
    ('bg2','white', 'dark blue'),
    ('touched', 'black', 'light gray'),]

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    else:
	print ""



def update_cell(loop,data_list):
	loop.widget = data_list[0]
	data_list[1].Refresh()
	loop.set_alarm_in(1,update_cell,data_list)

class LineBoxDerrived(urwid.LineBox):

    def __init__(self, original_widget):
        self.__super.__init__(original_widget)
	self.touched = False

    def mouse_event(self,size, event, button, col, row, focus):
	self.touched = True
	return self.touched


class Board:
	columns = urwid.Columns([ 
			LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(),1)) for y in range (50)],0)

	pile = urwid.Pile( [copy.deepcopy(columns) for y in range(17)])
	
	cell_state=[[0 for y in range(len(columns.widget_list))] for x in range(len(pile.widget_list))]
	
	i = random.randrange(0,len(pile.widget_list)-5)
	j = random.randrange(0,len(columns.widget_list)-5)		
	cell_state[i][j] = 1
	pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	cell_state[i-1][j] = 1
	pile.widget_list[i-1].widget_list[j] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	cell_state[i][j-1] = 1
	pile.widget_list[i].widget_list[j-1] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	cell_state[i-1][j-1] = 1
	pile.widget_list[i-1].widget_list[j-1] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	cell_state[i+1][j+1] = 1
	pile.widget_list[i+1].widget_list[j+1] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	cell_state[i+2][j+1] = 1
	pile.widget_list[i+1].widget_list[j+1] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1))
	
	def GetBoard(self):
		return Board.pile;

	def Kill(self,i,j):
		#if (Board.pile.widget_list[i].widget_list[j].touched == True):
			#Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.AttrMap(urwid.BoxAdapter(urwid.SolidFill(),1),'touched'))
		#else:
		Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.BoxAdapter(urwid.SolidFill(),1))
		Board.cell_state[i][j] = 0;
	
	def Spawn(self,i,j):
		if (Board.pile.widget_list[i].widget_list[j].touched == True) or self.NumOfTouched(i,j) > 1:
			Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.AttrMap(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1),'touched'))
			Board.pile.widget_list[i].widget_list[j].touched = True
		else:
			Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.AttrMap(urwid.BoxAdapter(urwid.SolidFill(fill_char='@'),1),'live'))
		Board.cell_state[i][j] = 1;
	
	def GetCellStatus(self,i,j):
		if i < 0 or i > len(Board.pile.widget_list)-1 or j < 0 or j > len(Board.columns.widget_list)-1:
			return 0
		return 	Board.cell_state[i][j]	
		
	def NumOfNeighbors(self,i,j):	
		return 	self.GetCellStatus(i-1,j-1)+self.GetCellStatus(i-1,j)+self.GetCellStatus(i-1,j+1)+self.GetCellStatus(i,j-1)+self.GetCellStatus(i,j+1)+self.GetCellStatus(i+1,j-1)+self.GetCellStatus(i+1,j)+self.GetCellStatus(i+1,j+1)
	
	def GetCellTouched(self,i,j):
		if i < 0 or i > len(Board.pile.widget_list)-1 or j < 0 or j > len(Board.columns.widget_list)-1:
			return 0
		return 	Board.pile.widget_list[i].widget_list[j].touched

	def NumOfTouched(self,i,j):	
		return 	self.GetCellTouched(i-1,j-1)+self.GetCellTouched(i-1,j)+self.GetCellTouched(i-1,j+1)+self.GetCellTouched(i,j-1)+self.GetCellTouched(i,j+1)+self.GetCellTouched(i+1,j-1)+self.GetCellTouched(i+1,j)+self.GetCellTouched(i+1,j+1)

	def Evolve(self,i,j):
		if i < 0 or i > len(Board.pile.widget_list)-1 or j < 0 or j > len(Board.columns.widget_list)-1:
			return		
				
		n = self.NumOfNeighbors(i,j)
		
		if Board.cell_state[i][j] == 1:
			#if (Board.pile.widget_list[i].widget_list[j].touched == True) or n > 3 or n < 2:
			if n > 3 or n < 2:
				self.Kill(i,j)
				Board.cell_state[i][j] = 0
			else:
				n = self.NumOfTouched(i,j)
				if n >=1 and (Board.pile.widget_list[i].widget_list[j].touched == False) :
					Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.AttrMap(urwid.BoxAdapter(urwid.SolidFill(fill_char='*'),1),'touched'))	
					Board.pile.widget_list[i].widget_list[j].touched = True
				if n < 2 and (Board.pile.widget_list[i].widget_list[j].touched == True):
					Board.pile.widget_list[i].widget_list[j] = LineBoxDerrived(urwid.AttrMap(urwid.BoxAdapter(urwid.SolidFill(fill_char='*'),1),'live'))		
		else:	  				
			if n == 3 or (Board.pile.widget_list[i].widget_list[j].touched == True) :	
				self.Spawn(i,j)
				Board.cell_state[i][j] = 1
	
	def Refresh(self):
		for i in range(len(Board.pile.widget_list)):
    			for j in range(len(Board.columns.widget_list)):
      				self.Evolve(i,j)
		
board = Board()
fillB = urwid.Filler(urwid.LineBox(board.pile,"The Game of Life - By Dusha for Pusha and Nusha :)"))
mapB = urwid.AttrMap(fillB, 'bg2')


txt = urwid.Text(('banner', u" The Game Of Life! "), align='center')
map1 = urwid.AttrMap(txt, 'streak')
fill = urwid.Filler(map1)
map2 = urwid.AttrMap(fill, 'bg1')

loop = urwid.MainLoop(map2,palette, unhandled_input=exit_on_q)
loop.set_alarm_in(1,update_cell,[mapB,board])
loop.screen.set_terminal_properties(colors=256)
loop.run()
