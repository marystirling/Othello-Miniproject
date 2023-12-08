"""
This is where the implementation of the plugin code goes.
The Undo-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('Undo')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Undo(PluginBase):
  def main(self):
        active_node = self.active_node
        core = self.core
        logger = self.logger
        self.namespace = None
        META = self.META

        # starts in Game Folder - contains OthelloGame
        gameFolderChildren = core.load_children(active_node)
        for othelloGameNode in gameFolderChildren:
           if core.is_instance_of(othelloGameNode, META['OthelloGame']):
              allGameStates = core.load_children(othelloGameNode)
              break
        
        logger.info(othelloGameNode)
        maxIndex = 0
        currentGameState = 1
        for potentialGameState in allGameStates:
          if core.is_instance_of(potentialGameState, META['GameState']):
            index = core.get_attribute(potentialGameState, 'state_num')
            if index and index > maxIndex:
              currentGameStateNum = index
              maxIndex = index
              currentGameState = potentialGameState
           

        logger.info(currentGameStateNum)
        # only undo if not the first state (default initial state has index of 1)
        if currentGameStateNum != 1:
          
          # set a value of 0 since will never access state again (default is 1 and that state will always be there)
          # thus, all valid states have state_num >= 1
          core.set_attribute(currentGameState, 'state_num', 0)
          self.util.save(self.root_node, self.commit_hash, self.branch_name, 'undo last move')
