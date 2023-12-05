"""
This is where the implementation of the plugin code goes.
The ValidTiles-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('ValidTiles')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class ValidTiles(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    
    nodesList = core.load_sub_tree(active_node)
    nodes = {}
    
    
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node

    logger.info('in main of ValidTiles')
    currentGameState = 'OthelloGameState1'
    currentGameStateNode = ''
    for p in paths:
      stateNode = nodes[p]
      if(core.is_instance_of(stateNode, META['OthelloGameState'])):
        stateName = core.get_attribute(stateNode, 'state_name')
        if stateName == 'OthelloGameState1':
          currentGameState = stateName
          currentGameStateNode = stateNode
    
    nodesList = core.load_sub_tree(currentGameStateNode)
    for potentialBoard in nodesList:
      if core.is_instance_of(potentialBoard, META['Board']):
        boardNode = potentialBoard
    
    nodes = {}
    
    # boardNode = active_node
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node
    
    # collect board information of tiles and possible pieces/connections
    board = []
    # dictionary of rows to organize board by rows
    rows = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7:{}}
    for node in nodesList:
      if (core.is_instance_of(node, META['Tile'])):
        tileRow = core.get_attribute(node, 'row')
        tileColumn = core.get_attribute(node, 'column')
        tilePiece = core.get_children_paths(node)
        tilePieceColor = "none"
        # gets color of tile if there is a piece on that tile; if not, stays 'none'
        for tilePieceNode in nodesList:
          if len(tilePiece) > 0:
            if tilePieceNode['nodePath'] == tilePiece[0]:
              tilePieceColor = core.get_attribute(tilePieceNode, 'color')
          if tileRow == 0:
            rows[0][tileColumn] = tilePieceColor
          elif tileRow == 1:
            rows[1][tileColumn] = tilePieceColor
          elif tileRow == 2:
            rows[2][tileColumn] = tilePieceColor
          elif tileRow == 3:
            rows[3][tileColumn] = tilePieceColor
          elif tileRow == 4:
            rows[4][tileColumn] = tilePieceColor
          elif tileRow == 5:
            rows[5][tileColumn] = tilePieceColor
          elif tileRow == 6:
            rows[6][tileColumn] = tilePieceColor
          elif tileRow == 7:
            rows[7][tileColumn] = tilePieceColor    
    for r in range(0, 8):
      row = []
      for c in range(0, 8):
        row.append({"color": rows[r][c]})
      # add each row to board list
      board.append(row)
   
    logger.info(board)
    
    
    # get player turn and opposite player
    gameState = core.get_parent(boardNode)
    currentPlayerPtr = core.get_pointer_path(gameState, 'currentPlayer')
    gameStateChildren = core.load_children(gameState)
    
    for playerNode in gameStateChildren:
      if playerNode['nodePath'] == currentPlayerPtr:
        currentPlayer = core.get_attribute(playerNode, 'color')
        break
        
    if currentPlayer == 'black':
      opposite = 'white'
    elif currentPlayer == 'white':
      opposite = 'black'
      
    logger.info('current player: {0}'.format(currentPlayer))
    logger.info('opposing player: {0}'.format(opposite))
    
    
    
    
    validTiles = []
    final_flips = []
    for r in range(0, 8):
      for c in range(0, 8):
        currRow = r
        currColumn = c
        if board[r][c]['color'] == 'none':
        
          # checks leftward horizontal potential moves (same row index)
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichCol > 0 and not found_same_color:
            if whichCol != currColumn:
              if board[currRow][whichCol]['color'] == 'none':
                break
            if board[currRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((currRow, whichCol))
            elif board[currRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichCol -= 1


          # checks rightward horizontal potential moves (same row index)
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichCol < 8 and not found_same_color:
            if whichCol != currColumn:
              if board[currRow][whichCol]['color'] == 'none':
                break
            if board[currRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((currRow, whichCol))
            elif board[currRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichCol += 1

          # checking upward vertical potential moves (same column index)
          whichRow = currRow
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow > 0 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][currColumn]['color'] == 'none':
                break
            if board[whichRow][currColumn]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, currColumn))
            elif board[whichRow][currColumn]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichRow -= 1

          # checking downward vertical potential moves (same column index)
          whichRow = currRow
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow < 8 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][currColumn]['color'] == 'none':
                break
            if board[whichRow][currColumn]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, currColumn))
            elif board[whichRow][currColumn]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichRow += 1

          # check for right-up diagonal potential moves
          whichRow = currRow
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow < 8 and whichCol < 8 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][whichCol]['color'] == 'none':
                break
            if board[whichRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, whichCol))
            elif board[whichRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  final_flips.append(flip)
                  result = True
            whichRow += 1
            whichCol += 1

          # check for right-down diagonal potential moves
          whichRow = currRow
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow < 8 and whichCol > 0 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][whichCol]['color'] == 'none':
                break
            if board[whichRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, whichCol))
            elif board[whichRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichRow += 1
            whichCol -= 1

          # checks for left-down diagonal potential moves
          whichRow = currRow
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow > 0 and whichCol > 0 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][whichCol]['color'] == 'none':
                break
            if board[whichRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, whichCol))
            elif board[whichRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True

            whichRow -= 1
            whichCol -= 1

          # checks for left-up diagonal potential moves
          whichRow = currRow
          whichCol = currColumn
          potential_flips = []
          found_same_color = False
          found_opposite_color = False
          while whichRow > 0 and whichCol < 8 and not found_same_color:
            if whichRow != currRow:
              if board[whichRow][whichCol]['color'] == 'none':
                break
            if board[whichRow][whichCol]['color'] == opposite:
              found_opposite_color = True
              potential_flips.append((whichRow, whichCol))
            elif board[whichRow][whichCol]['color'] == currentPlayer:
              found_same_color = True
              if found_opposite_color:
                for flip in potential_flips:
                  if (currRow, currColumn) != flip:
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
                    result = True
            whichRow -= 1
            whichCol += 1

    logger.info(validTiles)
    self.create_message(self.active_node, 'ValidTilesResult', validTiles)