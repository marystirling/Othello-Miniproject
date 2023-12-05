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
    
    
    nodesList = core.load_sub_tree(active_node)
    nodes = {}
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node
      
    paths = core.get_children_paths(active_node)
    
    
    # TODO: need to adjust this to get most recent - or change META to get pointer
    # find the most recent game state
    logger.info('in main')
    currentGameState = 'OthelloGameState1'
    currentGameStateNode = ''
    for p in paths:
      stateNode = nodes[p]
      if(core.is_instance_of(stateNode, META['OthelloGameState'])):
        stateName = core.get_attribute(stateNode, 'state_name')
        if stateName == 'OthelloGameState1':
          currentGameState = stateName
          currentGameStateNode = stateNode
    
    # call validTiles function to get a list of validTiles left to play
    validTiles = self.validTiles(currentGameStateNode)
    logger.info(self.validTiles(currentGameStateNode))
  
    # call countingPieces function to get total whites and blacks
    totalWhites, totalBlacks = self.countingPieces(currentGameStateNode)
    logger.info('totalWhites from main: {0}'.format(totalWhites))
    logger.info('totalBlacks from main: {0}'.format(totalBlacks))
    
    # check to see if win Condition (no Valid Tiles)
    winner = None
    if len(validTiles) == 0:
      # white wins
      if totalWhites > totalBlacks:
        winner = 'white'
      # black wins
      elif totalBlacks > totalWhites:
        winner = 'black'
      # tie - by default white wins
      else:
        winner = 'white'
    else:
      logger.info('no winner yet!')
    
    descriptor = self.buildDescriptor(currentGameStateNode)
    descriptor['win'] = winner
    logger.info('descriptor: {0}'.format(descriptor))
    self.create_message(active_node, json.dumps(descriptor))
    
  
  # function to get descriptor
  # {'player': colorString, 'board': [flattened array with piece color], 'position2path': nodePath}
  def buildDescriptor(self, stateNode):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META

    nodesList = core.load_sub_tree(stateNode)
    for potentialBoard in nodesList:
      if core.is_instance_of(potentialBoard, META['Board']):
        boardNode = potentialBoard
    
    nodes = {}
    
    # boardNode = active_node
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node
      
      
    # retrieve pointer path to currentPlayer 
    currentPlayerPath = core.get_pointer_path(stateNode, 'currentPlayer')
    for node in nodesList:
      if node['nodePath'] == currentPlayerPath:
        currentPlayerNode = node
        currentPlayer = core.get_attribute(currentPlayerNode, 'color')
    logger.info('currentPlayer: {0}'.format(currentPlayer))
    
    # flattened array of 64 pieces
    # initialzie each element with an empty piece ('-') - no piece placed
    board = []
    for i in range(0, 64):
      board.append('-')
    
    # collect piece color if a tile contains one, if not empty ('-')
    # also gives paths to each tile for player2Path in descriptor (hash_map)
    allTilePaths = core.get_children_paths(boardNode)
    logger.info(allTilePaths)
    hash_map = {}
    for tilePath in allTilePaths:
      tileNode = nodes[tilePath]
      if core.is_instance_of(tileNode, META['Tile']):
        row = core.get_attribute(tileNode, 'row')
        column = core.get_attribute(tileNode, 'column')
        pieceNodes = core.get_children_paths(tileNode)
        pieceColor = '-'
        if len(pieceNodes) > 0:
          pieceNode = nodes[pieceNodes[0]]
          pieceColor = core.get_attribute(pieceNode, 'color')
        # add that pieceColor to flattened array 
        board[row * 8 + column] = pieceColor
        hash_map[row * 8 + column] = tilePath
    
    
    
    # return descriptor data structure 
    descriptor = {'player': currentPlayer,
                  'board': board,
                  'position2path': hash_map}
    
    return descriptor
  
  # function to count the total white and black pieces on board -> returns tuple
  def countingPieces(self, stateNode):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    
    nodesList = core.load_sub_tree(stateNode)
    for potentialBoard in nodesList:
      if core.is_instance_of(potentialBoard, META['Board']):
        boardNode = potentialBoard
    
    nodes = {}
    
    # boardNode = active_node
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node
    
    totalWhites = 0
    totalBlacks = 0
    
    for node in nodesList:
      if (core.is_instance_of(node, META['Tile'])):
        tilePiece = core.get_children_paths(node)
        tilePieceColor = "none"
        # gets color of tile if there is a piece on that tile; if not, stays 'none'
        for tilePieceNode in nodesList:
          if len(tilePiece) > 0:
            if tilePieceNode['nodePath'] == tilePiece[0]:
              tilePieceColor = core.get_attribute(tilePieceNode, 'color')
              if tilePieceColor == 'white':
                totalWhites += 1
              elif tilePieceColor == 'black':
                totalBlacks += 1
    logger.info('whites: {0}'.format(totalWhites))
    logger.info('blacks: {0}'.format(totalBlacks))

    #self.create_message(self.active_node, 'CountingPiecesResult', {'totalWhites': totalWhites, 'totalBlacks': totalBlacks})
    return totalWhites, totalBlacks

  
  # function to check if there are any valid tiles -> returns list of (row,col) tile pairs if piece can be placed there
  def validTiles(self, stateNode):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META

    nodesList = core.load_sub_tree(stateNode)
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
    return validTiles
    #self.create_message(self.active_node, 'ValidTilesResult', validTiles)
