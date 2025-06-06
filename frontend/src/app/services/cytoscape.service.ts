import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { Injectable } from '@angular/core';

import { DagreLayoutOptions } from '../utils/cytoscape-utils';
import { edgeNormal } from '../utils/edge-utils';


cytoscape.use(dagre);

@Injectable({
  providedIn: 'root'
})


export class CytoscapeService {
  
  getDagreLayoutOptions(isDatamodel:boolean = true) {
    let rankSep = isDatamodel ? 500 : 720;
    return {
      name: 'dagre',
      rankDir: 'LR',
      ranker: 'tight-tree',
      nodeSep: 200,
      edgeSep: 100,
      rankSep: rankSep,
      acyclicer: 'greedy',
      align: 'DR',
      edgeWeight: (edge: cytoscape.EdgeSingular) => {
        return edge.source().data('type') === 'StoredProcedure' ? 1 : 30;
      }
    };
  }


  getNoHtmlStylingLabel(){
    let jsons = [{
      selector: 'node',
      style: {
        'label': 'data(id)',
        'text-valign': 'center',
        'text-halign': 'center',
        'color': '#000',
        'font-weight': 'bold',
        'font-size': '12px',
        'width': 'label',
        'height': '10px',
        'padding-left': '25px',
        'padding-right': '25px',
        'opacity': 1,
        'shape': 'roundrectangle',
      },
    },
    {
      selector: 'node[node_type = "NORMAL"]',
      style: {
        'background-color': '#A6CAEC',
      },
    },
    {
      selector: 'node[node_type = "LEAF"]',
      style: {
        'background-color': '#f3d36c',
      },
    },
    {
      selector: 'node[node_type = "ROOT"]',
      style: {
        'background-color': '#B4E5A2',
      },
    },
    {
      selector: 'node[node_type = "StoredProcedure"]',
      style: {
        'background-color': 'black',
        'border-color': '#91d5ff',
        'color': 'white',
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': '5px',
        'border-color': 'grey',
      },
    }]

    return jsons;
  }

  getNoHtmlStylingEdges(){
    let jsons = [
      {
        selector: 'edge',
        style: {
          'source-endpoint': `53% 0%`,
          'target-endpoint': `-53% 0%`
        }
      }
    ]
    return jsons;
  }

  getLineModeStyling(){
    let jsons = [
      {
        selector: 'edge[line_mode = "dash"]',
        style: {
          'line-style': 'dashed',
          'line-dash-pattern': [6, 10],
        },
      },
      {
        selector: 'edge[line_mode = "bi"]',
        style: {
          'line-style': 'dashed',
          'line-dash-pattern': [6, 10],
          'target-arrow-shape': 'triangle',
          'source-arrow-shape': 'triangle',
        },
      },
      {
        selector: 'edge',
        style: {
          'line-color': 'black',
          'width': 0.5,
          'source-arrow-color': 'black',
          'target-arrow-color': 'black',
          'target-arrow-shape': 'triangle',
        },
      },
    ]
    return jsons;
  }

  getHtmlNodeStyling(){
    let jsons = [
      {
        selector: 'node',
        style: {
          'opacity': 0,
          'shape': 'roundrectangle',
        },
      },
    ];

    return jsons;
  }


  backgroundDotStyling(
    cy: cytoscape.Core, 
    cyContainer: HTMLElement, 
    backgroundDotSize: number = 20, 
    maxZoom: number = 0.6
  ){
    cy.on('viewport', () => {
      const pan = cy.pan();
      const zoom = cy.zoom();
      if (cyContainer) {
        // Use real zoom for position and size
        cyContainer.style.backgroundPosition = `${pan.x}px ${pan.y}px`;
        cyContainer.style.backgroundSize = `${backgroundDotSize * zoom}px ${backgroundDotSize * zoom}px`;
    
        // Exponential fade based on zoom up to maxZoom
        const norm = Math.min(1, zoom / maxZoom);
        // Fade slower using square root
        const opacity = Math.sqrt(norm);
        const dotRadius = zoom;
        cyContainer.style.backgroundImage = `radial-gradient(circle, rgba(189, 189, 189, ${opacity}) ${dotRadius}px, transparent ${dotRadius}px)`;
      }
    });
  }

  mouseOverStyle(cy: cytoscape.Core, cyContainer: HTMLElement){
    cy.emit('viewport');
    cy.on('mouseover', 'node', () => {
      if (cyContainer) {
        cyContainer.style.cursor = 'pointer';
      }
    });

    cy.on('mouseout', 'node', () => {
      if (cyContainer) {
        cyContainer.style.cursor = 'default';
      }
    });
  }

  onNodeMoving(cy: cytoscape.Core, isDatamodel: boolean = true) {
    cy.on('position', 'node', (event) => {
      const node = event.target;
  
      cy.batch(() => {
        // Get edges connected to this moving node
        const connectedEdges = node.connectedEdges();
  
        // Call edgeNormal on each connected edge
        connectedEdges.forEach((edge: cytoscape.EdgeSingular) => {
          edgeNormal(edge, isDatamodel);
        });
      });
    });
  }


  standardNodeStyling(cy: cytoscape.Core) {
    let noHTMLStyling = [...this.getNoHtmlStylingLabel(), ...this.getLineModeStyling(), ...this.getNoHtmlStylingEdges()];

    cy.style()
    .fromJson(noHTMLStyling)
    .update(); 
  }

  htmlNodeStyling(cy: cytoscape.Core){
    let htmlStyling = [...this.getLineModeStyling(), ...this.getHtmlNodeStyling()];
    cy.style()
    .fromJson(htmlStyling)
    .update(); 
  }

  deselectAllNodes(cy: cytoscape.Core) {
    cy.batch(() => {
      cy.nodes().data('isSelected', false);
    });
  }

  normalizeAllEdges(cy: cytoscape.Core, isDatamodel: boolean = true) {
    cy.batch(() => {
      cy.edges().forEach(edge => {
        edgeNormal(edge, isDatamodel);
      });
    });
  }

  selectAndCenter(cy: cytoscape.Core, id: string, duration: number = 100) {
    this.deselectAllNodes(cy);
    const node = cy.nodes().filter(`[id = "${id}"]`);
    if (node.length > 0) {
      node.data('isSelected', true);
      try {
        const pos = node.position();
        const currZoom = cy.zoom();
        const targetPan = {
          x: cy.width() / 2 - pos.x * currZoom,
          y: cy.height() / 2 - pos.y * currZoom
        };
        cy.animate({ pan: targetPan }, { duration, easing: 'ease-out' });
      } catch { /* no-op */ }
    }
  }



  initializeCytoscape(containerId: string, elements: any, isDatamodel:boolean = true, normalizeEdges: boolean = true) {
    const cyContainer = document.getElementById(containerId);
    if (!cyContainer) {
      throw new Error('Container element not found');
    }
    let cy = cytoscape({
      container: cyContainer,
      elements: elements,
      zoomingEnabled: true,
      userZoomingEnabled: true,
      minZoom: 0.1,
      maxZoom: 2,
      layout: this.getDagreLayoutOptions(isDatamodel) as DagreLayoutOptions,
    });

    this.backgroundDotStyling(cy, cyContainer);
    this.mouseOverStyle(cy, cyContainer);

    if (normalizeEdges) {
      this.normalizeAllEdges(cy, isDatamodel);
      this.onNodeMoving(cy, isDatamodel);
    }
    return cy;
  }
}
