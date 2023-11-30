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
                if(pieces.length > 0) {
                    const pieceColor = core.getAttribute(nodeHash[pieces[0]], 'color');
                    value = (pieceColor === 'black') ? CONSTANTS.PIECE.BLACK : CONSTANTS.PIECE.WHITE;
                }
                board[row][column] = value
                //board[row * 8 + column] = value;
            });
            return board;
        },
        getPositionHash: (core, boardNode, nodeHash) => {
            const hash = {};
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                const row = Number(core.getAttribute(node, 'row'));
                const column = Number(core.getAttribute(node, 'column'));
 
                hash[row][column] = core.getPath(node);
            });
            return hash;
        }
    }
});

