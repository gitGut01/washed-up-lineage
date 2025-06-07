import { Component, OnInit, ViewEncapsulation, NgZone, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import cytoscape from 'cytoscape';
import { adjustLabelSize } from '../../utils/cytoscape-utils';
import { DataService } from '../../services/data.service';
import { Router, ActivatedRoute } from '@angular/router';
import { CytoscapeService } from '../../services/cytoscape.service'; 
import { LineageHighlightService } from '../../services/lineage-highlight.service';
import { defineNodeHtmlNode } from './html-nodes';

const LARGE_GRAPH_THRESHOLD = 200000;

@Component({
  selector: 'app-datamodel-lineage',
  templateUrl: './datamodel-lineage.component.html',
  styleUrls: ['./datamodel-lineage.component.scss'],
  standalone: true,
  imports: [],
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DatamodelLineageComponent implements OnInit {
  private cy: cytoscape.Core | null = null;
  private graphState = { zoom: 1, pan: { x: 0, y: 0 } };
  
  // Performance optimization flags
  nodeCount = 0;
  isLargeGraph = false;

  constructor(
    private dataService: DataService,
    private router: Router,
    private route: ActivatedRoute,
    private cytoscapeService: CytoscapeService,
    private lineageHighlightService: LineageHighlightService,
    private ngZone: NgZone,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {    
    this.route.queryParams.subscribe(params => {
      const objectId = params['object_id'];
      const path = '/datamodel-lineage';
      
      this.destroyCurrentCy();
      this.cdr.markForCheck();

      if (!objectId) {
        // If no object is specified, navigate to global lineage view
        this.router.navigate(['/global-lineage']);
        return;
      }
      
      // Load object lineage - for data models and procedures
      this.dataService.getObjectLineage(objectId).subscribe(response => {
        this.processAndRenderElements(response, path);
        this.lineageHighlightService.highlightObjectEdgeLineage(objectId, this.cy);
      });
    });
  }
  
  private processAndRenderElements(response: any, path: string) {
    // Process data outside Angular zone for better performance
    this.ngZone.runOutsideAngular(() => {
      // Chunk processing large datasets
      const elements = this.dataService.mapElements(response);

      this.nodeCount = elements.filter((el: any) => el.group === 'nodes').length;
      this.renderGraph(elements, path);
    });
  }

  renderGraph(elements: any[], path: string) {
    let cy: cytoscape.Core;

    cy = this.cytoscapeService.initializeCytoscape('cy', elements, true, true);
    defineNodeHtmlNode(cy);
    setTimeout(() => {
      adjustLabelSize(cy);
    }, 0);
    this.cytoscapeService.htmlNodeStyling(cy);

    
    // restore zoom and pan if we have previous state, otherwise center the graph
    if (this.graphState.zoom !== 1 || this.graphState.pan.x !== 0 || this.graphState.pan.y !== 0) {
      cy.zoom(this.graphState.zoom);
      cy.pan(this.graphState.pan);
    } else {
      // Center the graph on the middle of the network after a small delay to ensure rendering is complete
      setTimeout(() => {
        try {
          // First fit all elements to the viewport
          cy.fit();
          // Then center the viewport on the middle of the graph
          cy.center();
        } catch (e) {
          console.warn('Error centering graph:', e);
        }
      }, 100);
    }
    
    this.cy = cy;
  
    this.setUpCytoscapeInstance(cy, path);
    
    // Hide loading indicator
    this.ngZone.run(() => this.cdr.markForCheck());
  }
  
  setUpCytoscapeInstance(cy: cytoscape.Core, path: string) {
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const objectId = node.data().id;

      this.cytoscapeService.selectAndCenter(cy, objectId);
      const queryParams: any = {
        object_id: objectId,
        show_info: true
      };
      this.router.navigate([path], { queryParams });
    });

    cy.on('tap', (event) => {
      if (event.target === cy) {
        this.router.navigate([path], { queryParams: {show_info: null }, queryParamsHandling: 'merge' });
      }
    });
    
    // initial selection based on URL
    const params = this.route.snapshot.queryParams;
    const initId = params['object_id'];
    if (initId) {
      this.cytoscapeService.deselectAllNodes(cy);
      const node = cy.nodes().filter(`[id = "${initId}"]`);
      if (node.length > 0) {
        node.data('isSelected', true);
        this.cytoscapeService.selectAndCenter(cy, initId);
      }
    }
  }
  

  destroyCurrentCy() {
    if (this.cy) {
      this.graphState.zoom = this.cy.zoom();
      this.graphState.pan = this.cy.pan();
      this.cy.destroy();
      this.cy = null;
    }
  }
}