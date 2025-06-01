import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import cytoscape from 'cytoscape';
import { adjustLabelSize } from '../../utils/cytoscape-utils';
import { DataService } from '../../services/data.service';
import { ActivatedRoute, Router } from '@angular/router';
import { CytoscapeService } from '../../services/cytoscape.service';
import { LineageHighlightService } from '../../services/lineage-highlight.service';
import { defineNodeHtmlLabel } from './html-nodes';

@Component({
  selector: 'app-column-lineage',
  templateUrl: './column-lineage.component.html',
  styleUrls: ['./column-lineage.component.scss'],
  encapsulation: ViewEncapsulation.None,
  standalone: true
})
export class ColumnLineageComponent implements OnInit {
  private cy: cytoscape.Core | null = null;
  private currentColumnId: string | null = null;
  private graphState = {
    zoom: 1,
    pan: { x: 0, y: 0 }
  };

  constructor(
    private route: ActivatedRoute,
    private dataService: DataService,
    private router: Router,
     private lineageHighlightService: LineageHighlightService,
    private cytoscapeService: CytoscapeService
  ) {}
  
  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      const newColumnId = params['column_id'];
      if (!newColumnId) return;
      if (newColumnId !== this.currentColumnId) {
        this.currentColumnId = newColumnId;
        this.destroyCurrentCy();

        this.dataService.getColumnLineage(newColumnId).subscribe(response => {
          const elements = this.dataService.mapElements(response);
          this.cy = this.cytoscapeService.initializeCytoscape('cy', elements, false);
          
          this.cy.zoom(this.graphState.zoom);
          this.cy.pan(this.graphState.pan);
          
          this.lineageHighlightService.resetEdges(this.cy);
          //this.lineageHighlightService.setEdgesWithDirection(this.cy);

          this.setUpCytoscapeInstance(this.cy, '/column-lineage');
        });
      }
    });
  }
  
  destroyCurrentCy() {
    if (this.cy) {
      this.graphState.zoom = this.cy.zoom();
      this.graphState.pan = this.cy.pan();
      this.cy.destroy();
      this.cy = null;
    }
  }

  setUpCytoscapeInstance(cy: cytoscape.Core, path: string){
    cy.on('tap', (event) => {
      if (event.target === cy) {
        this.router.navigate([path]);
      }
    });

    defineNodeHtmlLabel(cy);
    this.cytoscapeService.htmlNodeStyling(cy);
    this.selectNode(cy);

    setTimeout(() => {
      adjustLabelSize(cy);
    }, 0);

    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const datamodel_name = node.data().datamodel_name;
      const column_id = node.data().id;

      this.router.navigate([path], {
        queryParams: {
          object_id: datamodel_name,
          column_id: column_id,
          show_info: true
        }
      });
    });
  }

  selectNode(cy: cytoscape.Core) {
    const params = this.route.snapshot.queryParams;
    const columnId = params['column_id'] || null;
    this.cytoscapeService.deselectAllNodes(cy);
    if (columnId) {
      const node = cy.nodes().filter(`[id = "${columnId}"]`);
      if (node.length > 0) {
        node.data('isSelected', true);
        try {
          const pos = node.position();
          const currZoom = cy.zoom();
          const targetPan = {
            x: cy.width() / 2 - pos.x * currZoom,
            y: cy.height() / 2 - pos.y * currZoom
          };
          cy.animate({ pan: targetPan }, { duration: 100, easing: 'ease-out' });
        } catch { /* no-op */ }
      }
    }
  }

}