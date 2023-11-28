define(['./constants'], function (CONSTANTS) {
    return {
        getBoardDescriptor: (core, META, boardNode, nodeHash) => {
            const board = [];
            for(let i=0;i<64;i+=1) {
                board.push(CONSTANTS.PIECE.EMPTY);
            }
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                const row = Number(core.getAttribute(node, 'row'));
                const column = Number(core.getAttribute(node, 'column'));
                let value = CONSTANTS.PIECE.EMPTY;
                const pieces = core.getChildrenPaths(node);
                if (pieces.length > 0) {
                    const pieceNode = nodeHash[pieces[0]];
                    const color = core.getAttribute(pieceNode, 'color');
                    
                    if (color === 'black') {
                        value = CONSTANTS.PIECE.BLACK;
                    } else if (color === 'white') {
                        value = CONSTANTS.PIECE.WHITE;
                    }
                }
                board[row * 8 + column] = value;
            });
            return board;
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

