/*globals define*/
/*eslint-env node, browser*/

/**
 * Generated by PluginGenerator 2.20.5 from webgme on Fri Jul 21 2023 23:34:11 GMT-0500 (Central Daylight Time).
 * A plugin that inherits from the PluginBase. To see source code documentation about available
 * properties and methods visit %host%/docs/source/PluginBase.html.
 */

define([
    'plugin/PluginConfig',
    'text!./metadata.json',
    'plugin/PluginBase',
    'othello-miniproject/constants',
    'othello-miniproject/utils'
], function (
    PluginConfig,
    pluginMetadata,
    PluginBase,
    CONSTANTS,
    UTILS) {
    'use strict';

    pluginMetadata = JSON.parse(pluginMetadata);

    /**
     * Initializes a new instance of BuildDescriptor.
     * @class
     * @augments {PluginBase}
     * @classdesc This class represents the plugin BuildDescriptor.
     * @constructor
     */
    function BuildDescriptor() {
        // Call base class' constructor.
        PluginBase.call(this);
        this.pluginMetadata = pluginMetadata;
    }

    /**
     * Metadata associated with the plugin. Contains id, name, version, description, icon, configStructure etc.
     * This is also available at the instance at this.pluginMetadata.
     * @type {object}
     */
    BuildDescriptor.metadata = pluginMetadata;

    // Prototypical inheritance from PluginBase.
    BuildDescriptor.prototype = Object.create(PluginBase.prototype);
    BuildDescriptor.prototype.constructor = BuildDescriptor;

    /**
     * Main function for the plugin to execute. This will perform the execution.
     * Notes:
     * - Always log with the provided logger.[error,warning,info,debug].
     * - Do NOT put any user interaction logic UI, etc. inside this method.
     * - callback always has to be called even if error happened.
     *
     * @param {function(Error|null, plugin.PluginResult)} callback - the result callback
     */
    BuildDescriptor.prototype.main = function (callback) {
        const {core, logger, META, activeNode, result} = this;

        const nodeHash = {};


        core.loadSubTree(activeNode)
        .then(nodes=>{
            nodes.forEach(node => {
                nodeHash[core.getPath(node)] = node;
            });
            
            let gameStateNode;
            // find gameState inside context of OthelloGame
            core.getChildrenPaths(activeNode).forEach(potentialState => {
                const node = nodeHash[potentialState];
                if(core.isInstanceOf(node, META.OthelloGameState)) {
                    if (core.getAttribute(node, 'state_name') === 'OthelloGameState1') {
                        gameStateNode = node;
                        return true;
                    }
                }
                return false
            });

            if (!gameStateNode) {
                throw new Error("No Othello GameState found in the context of OthellOGame");
            }
                    
            
            return this.invokePlugin('CheckWinCondition',{pluginConfig:{}});
        })
        .then(inner => {
            const descriptor = UTILS.getGameStateDescriptor(core, META, gameStateNode, nodeHash);
            descriptor.win = JSON.parse(inner.messages[0].message);
            this.createMessage(activeNode, JSON.stringify(descriptor));
            result.setSuccess(true);
            callback(null, result);
        })
        .catch(e=>{
            logger.error(e);
            result.setSuccess(false);
            callback(e, null);
        });
    };

    return BuildDescriptor;
});
