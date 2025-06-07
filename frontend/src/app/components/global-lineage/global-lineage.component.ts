import { Component, OnInit, ViewEncapsulation, NgZone, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import cytoscape from 'cytoscape';
import { DataService } from '../../services/data.service';
import { Router, ActivatedRoute } from '@angular/router';
import { CytoscapeService } from '../../services/cytoscape.service';

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

      if (this.cy) {
        if (newObjectId && newObjectId !== this.currentObjectId) {
          this.cytoscapeService.selectAndCenter(this.cy, newObjectId);
          this.currentObjectId = newObjectId;
        } else if (!newObjectId && this.currentObjectId) {
          this.cytoscapeService.deselectAllNodes(this.cy);
          this.currentObjectId = null;
        }
        return;
      }

      this.currentObjectId = newObjectId;
      this.dataService.getAllObjects().subscribe(response => {
        if (response && response.elements) {
          response.elements = response.elements.map((element: any) => {
            if (element.group === 'nodes') {
              element.data = {
                ...element.data,
                id: element.data.name,
                isSelected: false
              };
            }
            return element;
          });
        }

        const elements = this.dataService.mapElements(response);
        this.renderGraph(elements, path, this.currentObjectId);
      });
    });
    
  }

  renderGraph(elements: any[], path: string, objectIdToSelect?: string | null) {
    let cy: cytoscape.Core;
    cy = this.cytoscapeService.initializeCytoscape('cy', elements, true, false);
    this.cytoscapeService.standardNodeStyling(cy);

    this.cy = cy;
    this.setUpCytoscapeInstance(cy, path);

    if (objectIdToSelect) {
      this.cytoscapeService.selectAndCenter(cy, objectIdToSelect, 100);
      return;
    }

    cy.fit(undefined, 50);
    cy.center();
  }

  setUpCytoscapeInstance(cy: cytoscape.Core, path: string) {
    
    cy.on('tap', 'node', (event) => {
      const node = event.target;
      const tappedObjectId = node.data().id;

      const queryParams: any = {
        object_id: tappedObjectId,
        show_info: true
      };
      this.router.navigate([path], { queryParams, queryParamsHandling: 'merge' });
    });

    cy.on('tap', (event) => {
      if (event.target === cy) {
        this.router.navigate([path], { queryParams: { object_id: null, show_info: null }, queryParamsHandling: 'merge' });
      }
    });
  }
} 
