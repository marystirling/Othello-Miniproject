import React, {useCallback, useState} from 'react';
import Board from './board';
import CONSTANTS from 'constants.js';

export default function Othello({player, win, board, flips, totalBlacks, totalWhites}) {
    const getLabel = () => {
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
        <Board player={player} board={board} win={win} flips = {flips}/>
    </div>
    );
}