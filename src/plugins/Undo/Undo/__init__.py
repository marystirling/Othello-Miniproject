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

        gameChildren = core.load_children(active_node)
        
        maxIndex = 0
        for potentialGameStateNode in gameChildren:
           

          currentGameStateName = core.get_attribute(potentialGameStateNode, 'state_name')
        
        # only undo if not the first state
        if currentGameStateName != 'OthelloGameState1':
            
            # retrieve index off of current state
            numeric_part = ""
            index = len(currentGameStateName) - 1
            while index >= 0 and currentGameStateName[index].isdigit():
                numeric_part = currentGameStateName[index] + numeric_part
                index -= 1

            if numeric_part:
                currStateIndex = int(numeric_part)
                logger.info(currStateIndex)
            
            new_index = currStateIndex - 1
            
            # get state name with one less index
            newGameStateName = 'OthelloGameState' + str(new_index)
            
            # retrieve old state 
            othelloGame = core.get_parent(currentGameState)
            logger.info(othelloGame)
            
            all_states = core.load_children(othelloGame)
            logger.info(all_states)
            
            # find correct state want to undo to (one previous)
            for stateNode in all_states:
              if core.is_instance_of(stateNode, META['OthelloGameState']):
                thisStateName = core.get_attribute(stateNode, 'state_name')
                if thisStateName == newGameStateName:
                  logger.info(thisStateName)
                  new_state = core.copy_node(stateNode, META['OthelloGame'])
                  core.set_attribute(currentGameState, 'state_name', 'TRASH_STATE')
                  self.util.save(self.root_node, self.commit_hash, self.branch_name, 'new game state')
