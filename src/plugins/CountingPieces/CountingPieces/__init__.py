"""
This is where the implementation of the plugin code goes.
The CountingPieces-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('CountingPieces')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class CountingPieces(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    self.namespace = None
    META = self.META
    
    nodesList = core.load_sub_tree(active_node)
    nodes = {}
    
    boardNode = active_node
    
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

    self.create_message(self.active_node, 'CountingPiecesResult', {'totalWhites': totalWhites, 'totalBlacks': totalBlacks})

