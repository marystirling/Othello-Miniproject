"""
This is where the implementation of the plugin code goes.
The Flipping-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('PlayerMoves')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class PlayerMoves(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    logger.info('in PlayerMoves: {0}'.format(active_node))
    currentTile = core.load_sub_tree(active_node)[0]
    
    currRow = core.get_attribute(currentTile, 'row')
    currColumn = core.get_attribute(currentTile, 'column')
    logger.info('tile row: {0}'.format(currRow))
    logger.info('tile column: {0}'.format(currColumn))
    
    # checks to see if the tile is empty (does not contain a piece)
    tilePiece = core.get_children_paths(currentTile)
    
    # if tile contains a piece, returns "false" as the next piece cannot be placed here
    if len(tilePiece) != 0:
      logger.info('false')
      logger.error('TILE IS NOT VALID PLACE FOR UPCOMING PIECE')
      return
    else:
      logger.info('tile does not contain piece')

    
    # Board contains Tile
    board = core.get_parent(currentTile)
    
    # GameState contains Board
    gameState = core.get_parent(board)
    logger.info('game state::::: {0}'.format(gameState))
    # get all nodes at gameState node
    nodesList = core.load_sub_tree(gameState)
    
    # get the game state
    for gameStateNode in nodesList:
     
      if (core.is_instance_of(gameStateNode, META['GameState'])):
        gameStateName = core.get_attribute(gameStateNode, 'state_name')
        logger.info('game state: {0}'.format(gameStateName))
        
        
        if str(gameStateName) != "OthelloGameState1":
          #currentMoveTile = core.get_parent(nodes[core.get_pointer_path(gameStateNode, 'currentMove')])
          currentMovePath = core.get_pointer_path(gameStateNode, 'currentMove')
          for node in nodesList:
            if node['nodePath'] == currentMovePath:
              currentMoveNode = node
              currentMove = core.get_attribute(currentMoveNode, 'color')
        # retrieve pointer path to currentPlayer 
        currentPlayerPath = core.get_pointer_path(gameStateNode, 'currentPlayer')
        for node in nodesList:
          if node['nodePath'] == currentPlayerPath:
            currentPlayerNode = node
            currentPlayer = core.get_attribute(currentPlayerNode, 'color')

        
        if currentPlayer == 'black':
          opposite = 'white'
        elif currentPlayer == 'white':
          opposite = 'black'
        
        
        

    logger.info('current player: {0}'.format(currentPlayer))
    logger.info('opposing player: {0}'.format(opposite))

    # collect board information of tiles and possible pieces/connections
    board = []
    # dictionary of rows to organize board by rows
    rows = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7:{}}
    for boardNode in nodesList:
        if (core.is_instance_of(boardNode, META['Board'])):
            allTiles = core.get_children_paths(boardNode)
            for tile in allTiles:
                for currentTileNode in nodesList:
                    if currentTileNode['nodePath'] == tile:
                        tileRow = core.get_attribute(currentTileNode, 'row')
                        tileColumn = core.get_attribute(currentTileNode, 'column')
                        tilePiece = core.get_children_paths(currentTileNode)
                        tilePieceColor = "none"
                        # gets color of tile if there is a piece on that tile; if not, stays 'none'
                        for tilePieceNode in nodesList:
                            if len(tilePiece) > 0:
                                if tilePieceNode['nodePath'] == tilePiece[0]:
                                    tilePieceColor = core.get_attribute(tilePieceNode, 'color')
                                    break
                    
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
                        
                        break
            
           
            for r in range(0, 8):
              row = []
              for c in range(0, 8):
                row.append({"color": rows[r][c]})
              # at each row to board list
              board.append(row)
            break


    logger.info(board)
    
    # variable that holds the boolean value if piece can be placed at certain tile
    result = False
    
    # list of coordinates of opposite color pieces that can be flipped if this tile chosen
    final_flips = []
    
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
            final_flips.append(flip)
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
            final_flips.append(flip)
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
            final_flips.append(flip)
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
            final_flips.append(flip)
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
            final_flips.append(flip)
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
            final_flips.append(flip)
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
            final_flips.append(flip)
            result = True
      whichRow -= 1
      whichCol += 1
    
    
    # print out result value if next piece can be placed at this tile
    if len(final_flips) > 0:
      logger.info('flips {0} at these (row, column) pairs: {1}'.format(opposite, final_flips))
    logger.info(result)
    
    if result: 
      gameStateName = str(gameStateName)
      index_str = ''.join([char for char in gameStateName if char.isdigit()])
      if index_str:
        index = int(index_str)
      new_index = index + 1
      newStateName = gameStateName.rstrip(index_str) + str(new_index)
      
      
      #new_state = core.create_node({'parent':META['GameFolder'], 'base':META['OthelloGameState']})
      
      # Copy the contents of the current node into the new node
      new_state = core.copy_node(gameState, META['OthelloGame'])
      
      # Set the name of the new node separately
      core.set_attribute(new_state, 'state_name', newStateName)
      
      
        
        
      # find tile with correct row and column in new_state 
      nodesList = core.load_sub_tree(new_state)
      
      for boardNode in nodesList:
        if (core.is_instance_of(boardNode, META['Board'])):
          allTiles = core.load_children(boardNode)
          for tile in allTiles:
            thisRow = core.get_attribute(tile, 'row')
            thisCol = core.get_attribute(tile, 'column')
            
            if thisRow == currRow and thisCol == currColumn:
              parent_tile = tile
              
            for flip in final_flips:
              if flip[0] == thisRow and flip[1] == thisCol:
                childPiece = core.load_children(tile)
                core.set_attribute(childPiece[0], 'color', currentPlayer)
      
      # new piece on current tile is placed with currentPlayer color
      new_piece = core.create_node({'parent': parent_tile, 'base': META['Piece']})
      core.set_attribute(new_piece, 'color', currentPlayer)
      
      # set currentMove pointer to point from our new_state to the new_piece placed
      core.set_pointer(new_state, 'currentMove', new_piece)
      
      # set prev_state pointer to point from our new_state to the previous game state
      core.set_pointer(new_state, 'prevState', gameState)
      
      # set currentPlayer pointer to point from our new_state to the opposite color placed
      for playerNode in nodesList:
        if (core.is_instance_of(playerNode, META['Player'])):
          playerNodeColor = core.get_attribute(playerNode, 'color')
          if playerNodeColor == opposite:
            newPlayer = playerNode
      core.set_pointer(new_state, 'currentPlayer', newPlayer)
      
      self.util.save(self.root_node, self.commit_hash, self.branch_name, 'new game state')
     
    else:
      logger.error('TILE IS NOT VALID PLACE FOR UPCOMING PIECE')