import cytoscape from 'cytoscape';

/**
 * Dagre layout options
 */
export interface DagreLayoutOptions extends cytoscape.BaseLayoutOptions {
  name: 'dagre';
  rankDir?: 'TB' | 'LR' | 'BT' | 'RL'; // Top-Bottom, Left-Right, Bottom-Top, Right-Left
}



/**
 * Adjust label size to fit the node
 * @param cy cytoscape instance
 */
export function adjustLabelSize(cy: any, margin: number = 20){
  cy.nodes().forEach((node:any) => {
    const label = document.querySelector(`.node-container[data-id='${node.data('id')}']`);
    if (label) {
      const style = window.getComputedStyle(label);
      const totalWidth = parseFloat(style.width) + margin;
      const totalHeight = parseFloat(style.height) + margin;

      node.style({
        'width': totalWidth,
        'height': totalHeight,
        'background-color': 'red'
      });
    }
  });

}