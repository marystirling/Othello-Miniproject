import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { icon } from '@fortawesome/fontawesome-svg-core/import.macro'
import { useState } from 'react';
import CONSTANTS from 'constants.js';

export default function Tile({player, piece, position, win}) {

    const [hasMouse, setMouse, onHasMouseChange] = useState(false);

    const onTileClick = () => {
        if (piece === CONSTANTS.PIECE.VALID_MOVE) {
            WEBGME_CONTROL.playerMoves(player, position);
        }
    }

    const onMouseEnter = () => {
        setMouse(true);
    }

    const onMouseLeave = () => {
        setMouse(false);
    }

    const getPiece = () => {
        console.log('GP:',player,piece,position,win);
        const styleBlack = {fontSize:'70px', paddingLeft:'8px',paddingTop:'2px'};
        const styleWhite = {fontSize:'70px', paddingLeft:'13px',paddingTop:'2px'};
        const dStyle = player === CONSTANTS.PLAYER.BLACK ? 
            JSON.parse(JSON.stringify(styleBlack)) : 
            JSON.parse(JSON.stringify(styleWhite));
        dStyle.opacity = 0.5;

        let style = dStyle;
        let myIcon = null;
        switch (piece) {
            case CONSTANTS.PIECE.BLACK:
                style = styleBlack;
                myIcon = icon({name:'circle', family:'classic', style:'solid'});
                break;
            case CONSTANTS.PIECE.WHITE:
                style = styleWhite;
                myIcon = icon({name:'circle', family:'classic', style:'regular'});
                break;
            default:
                if(hasMouse) {
                    if(player === CONSTANTS.PLAYER.BLACK) {
                        myIcon = icon({name:'circle', family:'classic', style:'solid'});
                    } else {
                        myIcon = icon({name:'circle', family:'classic', style:'regular'});
                    }
                }
        }

        if(myIcon !== null) {
            return (<FontAwesomeIcon style={style} icon={myIcon} size='xl'/>); 
        }

        return null;
    }

    const getTile = () => {
        console.log(piece);
        const style = {
            width:'80px', 
            height:'80px', 
            borderColor:'black',
            borderWidth:'2px',
            border:'solid'};
            if (piece === CONSTANTS.PIECE.VALID_MOVE) {
                style.backgroundColor = '#87CEEB';
            }else if(hasMouse) {
                if(piece === CONSTANTS.PIECE.EMPTY) {
                    style.backgroundColor = '#F4C095';
                } else {
                    style.backgroundColor = '#1D7874';
                    style.opacity = 0.75;
                }
            }
            return (<div onClick={onTileClick} 
                style={style}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>{getPiece()}</div>);
    }

    return getTile();
}