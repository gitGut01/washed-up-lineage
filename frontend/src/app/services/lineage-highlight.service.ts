import { Injectable } from '@angular/core';
import { DataService } from './data.service';
import cytoscape from 'cytoscape';

@Injectable({
  providedIn: 'root'
})
export class LineageHighlightService {
  // Default colors - can be overridden by components
  private upstream_color = '#012d66';
  private downstream_color = '#70d7ff';
  private standard_edge_color = 'black';
  private bi_color = '#9f60fc';

  constructor(private dataService: DataService) {}

  /**
   * Highlights edges in a cytoscape graph based on the lineage of an object
   * @param objectId The ID of the object to highlight lineage for
   * @param cy The cytoscape instance
   * @param customColors Optional custom colors for edge highlighting
   */
  highlightObjectEdgeLineage(
    objectId: string, 
    cy: cytoscape.Core | null,
    customColors?: { 
      upstream?: string, 
      downstream?: string, 
      standard?: string 
    }
  ) {
    if (!objectId || !cy) {
      return;
    }

    // Use custom colors if provided, otherwise use defaults
    const upstreamColor = customColors?.upstream || this.upstream_color;
    const downstreamColor = customColors?.downstream || this.downstream_color;
    const standardColor = customColors?.standard || this.standard_edge_color;

    // Map edge ID to direction
    let lineageEdgeMap = new Map<string, { direction: string, line_mode: string }>();
    this.dataService.getObjectLineageEdges(objectId).subscribe(response => {
      // Extract and store edge IDs and directions
      if (response && response.elements && Array.isArray(response.elements)) {
        response.elements.forEach((element: { 
          group: string; 
          data?: { 
            id: string; 
            source: string; 
            target: string; 
            edge_type: string, 
            direction: string,
            line_mode: string
          } 
        }) => {
          if (element.data && element.data.id && element.data.direction) {
            lineageEdgeMap.set(element.data.id, { direction: element.data.direction, line_mode: element.data.line_mode });
          }
        });
      }

      // Use batch operation for improved performance
      cy.batch(() => {
        // Loop once through all edges: reset and apply styles
        const allEdges = cy.edges();
        if (allEdges) {
          allEdges.forEach(edge => {
            const edgeId = edge.id();
            const edgeData = lineageEdgeMap.get(edgeId);

            let z_index = 1;
            let width = 3;

            // Example usage of direction-based styling
            let isInLineage = edgeData !== undefined;

            let edge_color = standardColor;
            if (edgeData?.line_mode === 'bi') {
              edge_color = this.bi_color;
              z_index = 2;
              width = 7;
            } else if (edgeData?.direction === 'UPSTREAM') {
              edge_color = upstreamColor;
            } else if (edgeData?.direction === 'DOWNSTREAM') {
              edge_color = downstreamColor;
            }

            edge.style({
              'opacity': isInLineage ? 1 : 0.2,
              'width': isInLineage ? width : 1,
              'z-index': isInLineage ? z_index : 0,
              'line-color': edge_color,
              'target-arrow-color': edge_color,
              'source-arrow-color': edge_color
            });
          });
        }
      });
    });
  }

  /**
   * Reset all edges to default styling
   * @param cy The cytoscape instance
   */
  resetEdges(cy: cytoscape.Core | null) {
    if (!cy) return;
    
    // Use batch operation for improved performance
    cy.batch(() => {
      const edges = cy.edges();
      if (edges) {
        edges.style({
          'opacity': 1,
          'width': 1,
          'z-index': 0,
          'line-color': this.standard_edge_color,
          'target-arrow-color': this.standard_edge_color,
          'source-arrow-color': this.standard_edge_color
        });
      }
    });
  }
}
