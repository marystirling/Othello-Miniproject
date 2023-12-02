define(['./constants'], function (CONSTANTS) {
    return {
        getBoardDescriptor: (core, META, boardNode, nodeHash) => {
            console.log('getting board descriptor');
            // populates 2d array representing the board
            // const board = Array.from({ length: 8 }, () => Array(8).fill(CONSTANTS.PIECE.EMPTY));
            const board = []
            for(let i = 0; i < 64; i += 1) {
                board.push(CONSTANTS.PIECE.EMPTY);
            }
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                const row = Number(core.getAttribute(node, 'row'));
                const column = Number(core.getAttribute(node, 'column'));
                let value = CONSTANTS.PIECE.EMPTY;
                
                // determine if any pieces on tile, if so, get its piece color
                const pieces = core.getChildrenPaths(node);
                if (pieces.length > 0) {
                    const pieceColor = core.getAttribute(nodeHash[pieces[0]], 'color');
                    value = (pieceColor === 'black') ? CONSTANTS.PIECE.BLACK : CONSTANTS.PIECE.WHITE;
                }
                //board[row][column] = value;
                board[row * 8 + column] = value;
            });
            console.log('returning board descriptor');
            return board;
        },

        getGameStateDescriptor: (core, META, gameStateNode, nodeHash) => {
            const descriptor = {
                player: CONSTANTS.PLAYER.BLACK,
                board: null,
                position2path: null
            };
            console.log('getting gameState descriptor');

            // in game state, get pointer path to current player, gets attribute, and then sets descriptor.player 
            const currentPlayerPath = core.getPointerPath(gameStateNode, 'currentPlayer');
            if (core.getAttribute(nodeHash[currentPlayerPath], 'color') == 'black') {
                descriptor.player = CONSTANTS.PLAYER.BLACK;
            } else {
                descriptor.player = CONSTANTS.PLAYER.WHITE;
            }

            // load children of game state to find board node
            core.getChildrenPaths(gameStateNode).forEach(potentialBoard => {
                const boardNode = nodeHash[potentialBoard];
                if(core.isInstanceOf(boardNode, META.Board)) {
                    descriptor.board = this.getBoardDescriptor(core, META, boardNode, nodeHash)
                    descriptor.position2path = this.getPositionHash(core, boardNode, nodeHash);
                };
            });
            console.log('returning gamestate descriptor');
            return descriptor;
        },
        
        getPositionHash: (core, boardNode, nodeHash) => {
            const hash = {};
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                const row = Number(core.getAttribute(node, 'row'));
                const column = Number(core.getAttribute(node, 'column'));
 
                hash[row * 8 + column] = core.getPath(node);
            });
            return hash;
        }
    }
});

