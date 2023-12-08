import React from 'react';
import * as ReactDOMClient from 'react-dom/client';
import Othello from './othello_widget';


console.log('entering widget/src/index.jsx');
const container = document.getElementById(VISUALIZER_INSTANCE_ID);
const root = ReactDOMClient.createRoot(container);
const onUpdateFromControl = (descriptor) => {
    console.log('rendering', descriptor);
    root.render(<Othello player = {descriptor.player} 
                                    board = {descriptor.board} 
                                    win = {descriptor.win} 
                                    flips = {descriptor.flips} 
                                    totalBlacks = {descriptor.totalBlacks}
                                    totalWhites = {descriptor.totalWhites}/>);
}
console.log('connecting to control');
WEBGME_CONTROL.registerUpdate(onUpdateFromControl);