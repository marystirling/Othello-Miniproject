"""
This is where the implementation of the plugin code goes.
The BuildDescriptorPy-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('BuildDescriptorPy')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class BuildDescriptorPy(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    import json
    
    
    
    # find the current game state
    currentGameState = ''
    currentGameStateNode = ''
    gameChildren = core.load_children(active_node)
    
    # if only one game state children of OthelloGame, then 1
    # find the most recent game state by looking at OthelloGameState index
    # default is 1 (first state automatically)
    # trash states from undo will have index 0 so they will never be accessed
    currentGameState = 1
    currentGameStateNode = ''
    maxIndex = 0
    for stateNode in gameChildren:
        if core.is_instance_of(stateNode, META['OthelloGameState']):
            index = core.get_attribute(stateNode, 'state_num')
            logger.info('STATE NUM IS: {0}'.format(index))
            if index and index > maxIndex:
                currentGameStateNode = stateNode
                currentGameState = index
                maxIndex = index

        
          
        
    logger.info('current game state: {0}, {1}'.format(currentGameState, currentGameStateNode))
    
    # call validTiles function to get a list of validTiles left to play
    validTiles, connections, currentPlayer, allTileNodes = self.validTiles(currentGameStateNode)
  
    # call countingPieces function to get total whites and blacks
    totalWhites, totalBlacks = self.countingPieces(allTileNodes)

    
    # check to see if win Condition (no Valid Tiles)  
    if len(validTiles) == 0:
      winner = True
    else:
      winner = False
    
    
    descriptor = self.buildDescriptor(currentGameStateNode, validTiles, allTileNodes)
    descriptor['win'] = winner
    descriptor['player'] = currentPlayer
    descriptor['flips'] = connections
    descriptor['totalWhites'] = totalWhites
    descriptor['totalBlacks'] = totalBlacks
    logger.info('descriptor: {0}'.format(descriptor))
    self.create_message(active_node, json.dumps(descriptor))
    
  
  # function to get descriptor
  # {'player': colorString, 'board': [flattened array with piece color]}
  def buildDescriptor(self, stateNode, validTiles, allTileNodes):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META

    
    validTilesFlattened = []
    for validTile in validTiles:
      validRow = validTile[0]
      validCol = validTile[1]
      validTilesFlattened.append(validRow * 8 + validCol)

    
    
    # flattened array of 64 pieces
    # initialzie each element with an empty piece ('-') - no piece placed
    board = ['-'] * 64

    for i in validTilesFlattened:
      board[i] = 'valid_move'
    
    # collect piece color if a tile contains one, if not empty ('-')
    for tileNode in allTileNodes:
      if core.is_instance_of(tileNode, META['Tile']):
        row = core.get_attribute(tileNode, 'row')
        column = core.get_attribute(tileNode, 'column')
        pieceNodes = core.load_children(tileNode)
        if len(pieceNodes) > 0:
          pieceColor = core.get_attribute(pieceNodes[0], 'color')
          # add that pieceColor to flattened array 
          board[row * 8 + column] = pieceColor
    
    
    descriptor = {'board': board}
    
    return descriptor
  
  # function to count the total white and black pieces on board -> returns tuple
  def countingPieces(self, allTileNodes):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    
    totalWhites = 0
    totalBlacks = 0
    
    for tileNode in allTileNodes:
      if (core.is_instance_of(tileNode, META['Tile'])):
        tileChildren = core.load_children(tileNode)
        tilePieceColor = "none"
        # gets color of tile if there is a piece on that tile; if not, stays 'none'
        if len(tileChildren) > 0:
            tilePieceColor = core.get_attribute(tileChildren[0], 'color')
            if tilePieceColor == 'white':
              totalWhites += 1
            elif tilePieceColor == 'black':
              totalBlacks += 1
    

    return totalWhites, totalBlacks

  
  # function to check if there are any valid tiles -> returns list of (row,col) tile pairs if piece can be placed there
  def validTiles(self, stateNode):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META

    gameStateChildren = core.load_children(stateNode)
    for potentialBoard in gameStateChildren:
      if core.is_instance_of(potentialBoard, META['Board']):
        boardNode = potentialBoard
    # collect board information of tiles and possible pieces/connections
    board = []
    # dictionary of rows to organize board by rows
    rows = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7:{}}

    allTileNodes = core.load_children(boardNode)
    for currentTileNode in allTileNodes:
        if core.is_instance_of(currentTileNode, META['Tile']):
            tileRow = core.get_attribute(currentTileNode, 'row')
            tileColumn = core.get_attribute(currentTileNode, 'column')
            tilePiece = core.load_children(currentTileNode)
            tilePieceColor = "none"
            # gets color of tile if there is a piece on that tile; if not, stays 'none'
            if len(tilePiece) > 0:
                tilePieceColor = core.get_attribute(tilePiece[0], 'color')
                
        
            # organize tile colors by their row number 
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
      # at each row to board list
      board.append(row)
    
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
    connections = {}
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    logger.info('({0},{1}) flips ({2}, {3})'.format(currRow, currColumn, flip[0], flip[1]))
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
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
                  if (currRow, currColumn) != flip:
                    if currRow * 8 + currColumn in connections:
                        connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                        connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                  final_flips.append(flip)
                  validTiles.append((currRow, currColumn))
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))

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
                    if currRow * 8 + currColumn in connections:
                      connections[currRow * 8 + currColumn].append((flip[0], flip[1]))
                    else: 
                      connections[currRow * 8 + currColumn] = [(flip[0], flip[1])]
                    final_flips.append(flip)
                    validTiles.append((currRow, currColumn))
            whichRow -= 1
            whichCol += 1

    logger.info('IN BUILD DESCRIPTOR VALID TILES: {0}'.format(validTiles))
    return validTiles, connections, currentPlayer, allTileNodes

