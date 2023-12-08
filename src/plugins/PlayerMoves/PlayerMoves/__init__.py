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

    # get the position of the tileClicked
    config = self.get_current_config()
    position = config['position']
    

    # get the tiles to be flipped by tileClicked
    flips = config['flips']
    final_flips = flips[str(position)]
    
    # get the row and column from tileClicked
    for pos_r in range(0, 8):
      for pos_c in range(0, 8):
        if (pos_r * 8 + pos_c) == position:
          new_tile_r = pos_r
          new_tile_c = pos_c
          break
    
    gameChildren = core.load_sub_tree(active_node)

    # getting the current tile node that was clicked based on our config above
    for tileNode in gameChildren: 
      if core.is_instance_of(tileNode, META['Tile']):
        tileRow = core.get_attribute(tileNode, 'row')
        tileCol = core.get_attribute(tileNode, 'column')
        if tileRow == new_tile_r and tileCol == new_tile_c:
          currRow = tileRow
          currColumn = tileCol
          active_node = tileNode
          currentTile = active_node
          break

    logger.info('tile row: {0}'.format(currRow))
    logger.info('tile column: {0}'.format(currColumn))

    # Board contains Tile
    board = core.get_parent(currentTile)
    
    # GameState contains Board
    gameState = core.get_parent(board)
    othelloGame = core.get_parent(gameState)

    # get OthelloGameState with highest index
    maxIndex = 0
    allGameStates = core.load_children(othelloGame)
    gameStateNum = 1
    gameStateNode = ''
    for potentialGameState in allGameStates:
      if core.is_instance_of(potentialGameState, META['GameState']):
        index = core.get_attribute(potentialGameState, 'state_num')
        if index and index > maxIndex:
            gameStateNode = potentialGameState
            gameState = potentialGameState
            gameStateNum = index
            maxIndex = index
    logger.info('game state index retrieved: {0}'.format(gameStateNum))
    
    
    # retrieve pointer path to currentPlayer 
    gameStateChildren = core.load_children(gameStateNode)
    currentPlayerPath = core.get_pointer_path(gameStateNode, 'currentPlayer')
    for node in gameStateChildren:
      if node['nodePath'] == currentPlayerPath:
        currentPlayerNode = node
        currentPlayer = core.get_attribute(currentPlayerNode, 'color')

        if currentPlayer == 'black':
          opposite = 'white'
        elif currentPlayer == 'white':
          opposite = 'black'
        
        break

    logger.info('current player: {0}'.format(currentPlayer))
    logger.info('opposing player: {0}'.format(opposite))


    # print out result value if next piece can be placed at this tile
    if len(final_flips) > 0:
      logger.info('flips {0} at these (row, column) pairs: {1}'.format(opposite, final_flips))
   

    # get next game state num
    newGameStateNum = gameStateNum + 1
    logger.info('new game state index state_num: {0}'.format(newGameStateNum))

    # Copy the contents of the current node into the new node
    new_state = core.copy_node(gameState, META['OthelloGame'])

    # Set the name of the new node separately
    core.set_attribute(new_state, 'state_num', newGameStateNum)
    
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
        break
    
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
          break
    core.set_pointer(new_state, 'currentPlayer', newPlayer)
    
    self.util.save(self.root_node, self.commit_hash, self.branch_name, 'new game state')
    
