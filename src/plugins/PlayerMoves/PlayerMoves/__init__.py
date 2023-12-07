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
    


    nodesList = core.load_sub_tree(active_node)
    
    nodes = {}
    
    # collect all nodes path
    for node in nodesList:
      nodes[core.get_path(node)] = node
    
    for tileNode in nodesList: 
      if core.is_instance_of(tileNode, META['Tile']):
        tileRow = core.get_attribute(tileNode, 'row')
        tileCol = core.get_attribute(tileNode, 'column')
        if tileRow == new_tile_r and tileCol == new_tile_c:
          currRow = tileRow
          currColumn = tileCol
          active_node = tileNode
          currentTile = active_node
          break
        
      
    paths = core.get_children_paths(active_node)

    logger.info('tile row: {0}'.format(currRow))
    logger.info('tile column: {0}'.format(currColumn))
    
    # checks to see if the tile is empty (does not contain a piece)
    tilePiece = core.get_children_paths(currentTile)
    
    # if tile contains a piece, returns "false" as the next piece cannot be placed here
    if len(tilePiece) != 0:
      logger.error('TILE IS NOT VALID PLACE FOR UPCOMING PIECE')
      return
    else:
      logger.info('tile does not contain piece')

    
    # Board contains Tile
    board = core.get_parent(currentTile)
    
    # GameState contains Board
    gameState = core.get_parent(board)
    othelloGame = core.get_parent(gameState)

    # get OthelloGameState with highest index
    currentGameState = 'OthelloGameState1'
    currentGameStateNode = ''
    maxIndex = 0
    allGameStates = core.load_children(othelloGame)
    for potentialGameState in allGameStates:
      if core.is_instance_of(potentialGameState, META['GameState']):
        stateName = core.get_attribute(potentialGameState, 'state_name')
        logger.info('POTENTIAL STATE: {0}'.format(core.get_attribute(potentialGameState, 'state_name')))
        stateName = core.get_attribute(potentialGameState, 'state_name')
        index = ''.join([char for char in stateName if char.isdigit()])
        if index and int(index) > maxIndex:
            gameStateNode = potentialGameState
            gameState = potentialGameState
            gameStateName = stateName
            maxIndex = int(index)
    logger.info('FINAL STATE: {0}: {1}'.format(gameStateName, gameStateNode))
        
    if str(gameStateName) != "OthelloGameState1":
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
        
        
    stateChildren = core.load_sub_tree(gameStateNode)
    logger.info('current player: {0}'.format(currentPlayer))
    logger.info('opposing player: {0}'.format(opposite))

   
    
    
    # print out result value if next piece can be placed at this tile
    if len(final_flips) > 0:
      logger.info('flips {0} at these (row, column) pairs: {1}'.format(opposite, final_flips))
   

    logger.info('IN PLAYER MOVES VALID TILES: {0}'.format(final_flips))
    gameStateName = str(gameStateName)
    index_str = ''.join([char for char in gameStateName if char.isdigit()])
    if index_str:
      index = int(index_str)
    new_index = index + 1
    newStateName = gameStateName.rstrip(index_str) + str(new_index)
    
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
    
