import React, {useCallback, useState} from 'react';
import Board from './board';
import CONSTANTS from 'constants.js';

export default function Othello({player, win, board}) {
    const getLabel = () => {
            let totalWhites = 0;
            let totalBlacks = 0;
        board.forEach(piece => {
            if (piece === CONSTANTS.PIECE.BLACK) {
                totalBlacks = totalBlacks + 1;
            } else if (piece === CONSTANTS.PIECE.WHITE) {
                totalWhites = totalWhites + 1;
            }
        });
        if(!win) {
            if (player === CONSTANTS.PLAYER.BLACK) {
                return `Player Black's Turn (Black: ${totalBlacks}, White: ${totalWhites})`;
            } else {
                return `Player White's Turn (Black: ${totalBlacks}, White: ${totalWhites})`;
            }
        } else {
            if (totalBlacks > totalWhites) {
                return 'Player black won!'
            } else if (totalWhites > totalBlacks) {
                return 'Player white won!'
            } else {
                return 'Game ended in tie.'
            }
            
        }
    }
    return (
    <div style={{ width: '100%', height: '100%', fontFamily:'fantasy', fontSize:'36px', fontWeight:'bold'}}>
        {getLabel()}
        <Board player={player} board={board} win={win}/>
    </div>
    );
}