import cytoscape from 'cytoscape';
// @ts-ignore
import nodeHtmlLabel from 'cytoscape-node-html-label';

// Track if nodeHtmlLabel has been initialized
let nodeHtmlLabelInitialized = false;

/**
 * Initialize nodeHtmlLabel extension for Cytoscape
 * This function ensures the extension is only initialized once
 */
export function initializeNodeHtmlLabel() {
  if (!nodeHtmlLabelInitialized) {
    nodeHtmlLabel(cytoscape);
    nodeHtmlLabelInitialized = true;
  }
}

// Initialize on import
initializeNodeHtmlLabel();
