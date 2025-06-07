import { Component, OnInit, ViewEncapsulation, NgZone, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { DataService } from '../../services/data.service';
import { Router, ActivatedRoute } from '@angular/router';
import { CytoscapeService } from '../../services/cytoscape.service';
import { DagreLayoutOptions } from '../../utils/cytoscape-utils';

cytoscape.use(dagre);

const LARGE_GRAPH_THRESHOLD = 200000;

@Component({
  selector: 'app-global-lineage',
  templateUrl: './global-lineage.component.html',
  styleUrls: ['./global-lineage.component.scss'],
  standalone: true,
  imports: [],
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class GlobalLineageComponent implements OnInit {
  private currentObjectId: string | null = null;

  private cy: cytoscape.Core | null = null;
  // private graphState = { zoom: 1, pan: { x: 0, y: 0 } }; // Zoom/pan restoration removed
  
  // Performance optimization flags
  nodeCount = 0;
  isLargeGraph = false;

  constructor(
    private dataService: DataService,
    private router: Router,
    private route: ActivatedRoute,
    private cytoscapeService: CytoscapeService,
    private ngZone: NgZone,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const newObjectId = params['object_id'];
      const path = '/global-lineage';

      
      if (this.cy && newObjectId && newObjectId !== this.currentObjectId) {
        this.handleNodeSelectionChange(newObjectId);
        this.currentObjectId = newObjectId;
        return; // Prevent full re-render
      } else if (this.cy && !newObjectId && this.currentObjectId) {
        this.cytoscapeService.deselectAllNodes(this.cy);
        this.currentObjectId = null;
        return; // Prevent full re-render
      }

      // Proceed with full graph load/reload
      this.currentObjectId = newObjectId; // Store current objectId for initial load context

      // destroy previous instance
      if (this.cy) this.destroyCurrentCy();

      // Show loading state
      this.cdr.markForCheck();

      // Default view - load all objects
      this.dataService.getAllObjects().subscribe(response => {
        if (response && response.elements) {
          response.elements = response.elements.map((element: any) => {
            if (element.group === 'nodes') {
              element.data = {
                ...element.data,
                id: element.data.name || element.data.id,
                isSelected: false
              };
            }
            return element;
          });
        }
        this.processAndRenderElements(response, path);
      });
    });
  }
  
  /**
   * Process and render graph elements
   */
  private processAndRenderElements(response: any, path: string) {
    // Process data outside Angular zone for better performance
    this.ngZone.runOutsideAngular(() => {
      // Chunk processing large datasets
      const elements = this.dataService.mapElements(response);

      this.nodeCount = elements.filter((el: any) => el.group === 'nodes').length;
      this.isLargeGraph = this.nodeCount > LARGE_GRAPH_THRESHOLD;
      this.renderGraph(elements, path);
    });
  }

  renderGraph(elements: any[], path: string) {
    let cy: cytoscape.Core;
    const cyContainer = document.getElementById('cy');

    if (!cyContainer) {
      console.error("Cytoscape container 'cy' not found!");
      // Potentially hide loading indicator and return
      this.ngZone.run(() => this.cdr.markForCheck());
      return;
    }

    cy = this.cytoscapeService.initializeCytoscape('cy', elements, true, false);
    this.cytoscapeService.standardNodeStyling(cy);
    
    // Always fit and center the graph on initial render or full reload
    setTimeout(() => {
      try {
        cy.fit(undefined, 50); // Add some padding
        cy.center();
      } catch (e) {
        console.warn('Error centering graph:', e);
      }
    }, 100);

    this.cy = cy;

    this.setUpCytoscapeInstance(cy, path);

    // Hide loading indicator
    this.ngZone.run(() => this.cdr.markForCheck());
  } // This closes renderGraph

  setUpCytoscapeInstance(cy: cytoscape.Core, path: string) {
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const objectId = node.data().id;

      // this.cytoscapeService.selectAndCenter(cy, objectId); // Centering will be handled by ngOnInit subscription
    const queryParams: any = {
      object_id: objectId,
      show_info: true // Add show_info parameter
    };
    this.router.navigate([path], { queryParams, queryParamsHandling: 'merge' }); // Use merge to preserve other params if any
    });

    cy.on('tap', (event) => {
      if (event.target === cy) {
      // Clear selection and show_info by navigating with empty query params relevant to selection
      this.router.navigate([path], { queryParams: { object_id: null, show_info: null }, queryParamsHandling: 'merge' });
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
        // instant center for default view - selectAndCenter handles this better
      // try { cy.center(node); } catch { /*no-op*/ }
      // Use selectAndCenter for consistency, or ensure ngOnInit handles initial selection centering if newObjectId is present
      if (this.cy && initId === this.currentObjectId) { // Ensure it's the current one being processed by ngOnInit
         this.cytoscapeService.selectAndCenter(this.cy, initId, 0); // 0 duration for instant
      }
      }
    }
  }

  destroyCurrentCy() {
  if (this.cy) {
    // this.graphState.zoom = this.cy.zoom(); // Removed: No longer restoring zoom/pan
    // this.graphState.pan = this.cy.pan();   // Removed: No longer restoring zoom/pan
    this.cy.destroy();
    this.cy = null;
  }
}

private handleNodeSelectionChange(objectId: string) {
  if (this.cy) {
    this.cytoscapeService.selectAndCenter(this.cy, objectId);
    // Potentially markForCheck if other UI elements depend on selection and are OnPush
    this.cdr.markForCheck(); 
  }
}
}
