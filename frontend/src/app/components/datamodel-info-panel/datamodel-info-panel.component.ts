import { Component, OnInit, HostListener, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router'
import { DataService } from '../../services/data.service';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';


@Component({
  selector: 'app-datamodel-info-panel',
  templateUrl: './datamodel-info-panel.component.html',
  styleUrls: ['./datamodel-info-panel.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DatamodelInfoPanelComponent implements OnInit {
  objectId: string = '';
  datamodelLabel: string = '';
  datamodelTags: string = '';
  warehouse: string = '';
  schema: string = '';
  object: string = '';
  showToast: boolean = false;
  toastMessage: string = '';
  columns: { name: string, type: string, column_id: string, is_type_guessed: boolean, is_type_updated: boolean }[] = [];
  filteredColumnsCache: { name: string, type: string, column_id: string, is_type_guessed: boolean, is_type_updated: boolean }[] = [];
  isOpen = false;
  highlightedColumnId: string | null = null;
  searchQuery: string = '';
  closePanelToRoute: string = '';
  panelWidth: number = 300;
  
  // Computed property to determine if we're in the object lineage view
  get lineageToggle(): boolean {
    return this.router.url.split('?')[0] === '/datamodel-lineage';
  }
  
  private resizing = false;
  private startX = 0;
  private startWidth = 0;

  constructor(
    private route: ActivatedRoute, 
    private router: Router,
    private dataService: DataService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {

    this.route.queryParams.subscribe(params => {
      const objectId = params['object_id'];
      const showInfo = params['show_info'];
      this.highlightedColumnId = params['column_id'] || null;
  
      if (objectId && showInfo) {
        this.fetchDatamodelData(objectId);
        this.isOpen = true;
        this.searchQuery = '';
        this.updateFilteredColumns();
      } else {
        this.isOpen = false;
      }
    });

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.closePanelToRoute = this.router.url.split('?')[0]; // Remove query params
    });
  }

  fetchDatamodelData(objectId: string) {
    this.dataService.getObjectByName(objectId).subscribe(data => {
      // The new API response format has elements as an array
      if (data && data.elements && Array.isArray(data.elements) && data.elements.length > 0) {
        // Get the first element's data (should be the requested object)
        let data_result = data.elements[0].data;
        
        this.objectId = data_result.id || data_result.name;
        this.datamodelLabel = data_result.name || data_result.original_name;
        this.datamodelTags = data.tags || 'No tags';
        this.warehouse = data_result.warehouse || '';
        this.schema = data_result.schema || '';
        this.object = data_result.object || '';
        
        this.cdr.markForCheck();
      } else {
        console.error('Invalid object data format:', data);
      }
    });
    
    this.columns = [];
    this.filteredColumnsCache = [];
    
    this.dataService.getColumnsByDataModel(objectId).subscribe(data => {
      this.columns = data.elements.map((column: any) => ({
        name: column.data.original_name || column.data.name || column.data.id,
        type: column.data.type || 'null',
        column_id: column.data.id,
        is_type_guessed: column.data.is_type_guessed || false,
        is_type_updated: column.data.is_type_updated || false
      }));
      this.updateFilteredColumns();
      this.cdr.markForCheck();
    });
  }

  onColumnClick(column: { name: string, type: string, column_id: string, is_type_guessed: boolean, is_type_updated: boolean }) {
    this.router.navigate(['/column-lineage'], {
      queryParams: {
        object_id: this.objectId,
        column_id: column.column_id,
        show_info: true
      }
    });
  }

  updateFilteredColumns() {
    const query = this.searchQuery.toLowerCase();
    if (query === '') {
      this.filteredColumnsCache = this.columns;
    } else {
      this.filteredColumnsCache = this.columns.filter(column =>
        column.name.toLowerCase().includes(query) ||
        column.type.toLowerCase().includes(query)
      );
    }
  }
  
  // Method for search input binding
  onSearchChange(value: string) {
    // Update the filtered columns immediately
    this.updateFilteredColumns();
    this.cdr.markForCheck();
  }

  close() {
    this.isOpen = false;
    this.router.navigate([this.closePanelToRoute]);
  }

  /**
   * Toggle between global and object lineage views
   */
  showLineage() {
    // Check current route to determine toggle destination
    const currentRoute = this.router.url.split('?')[0];
    
    // Build query params
    const queryParams: any = {
      object_id: this.objectId,
      show_info: true
    };
    
    if (currentRoute === '/datamodel-lineage') {
      // We're in object lineage view, go back to global view
      this.router.navigate(['/global-lineage'], { queryParams });
    } else {
      // We're in global or another view, go to object lineage view
      this.router.navigate(['/datamodel-lineage'], { queryParams });
    }
  }

  copyToClipboard(text: string, label: string = '') {
    navigator.clipboard.writeText(text).then(() => {
      // Show toast notification
      this.toastMessage = `Copied ${label ? label + ': ' : ''}${text}`;
      this.showToast = true;
      
      // Automatically hide toast after 3 seconds
      setTimeout(() => {
        this.showToast = false;
        this.cdr.markForCheck();
      }, 3000);
      
      this.cdr.markForCheck();
    });
  }

  /**
   * Toggle between global and object-specific lineage views
   */
  toggleLineage() {
    if (!this.objectId) return;
    
    // Check current route to determine toggle destination
    const currentRoute = this.router.url.split('?')[0];
    
    if (currentRoute === '/datamodel-lineage') {
      // We're in object lineage view, go to global view
      this.router.navigate(['/global-lineage'], { 
        queryParams: { 
          object_id: this.objectId, 
          show_info: true 
        } 
      });
    } else {
      // We're in another view, go to object lineage view
      this.router.navigate(['/datamodel-lineage'], { 
        queryParams: { 
          object_id: this.objectId, 
          show_info: true 
        } 
      });
    }
  }

  onResizeMouseDown(event: MouseEvent) {
    this.resizing = true;
    this.startX = event.clientX;
    this.startWidth = this.panelWidth;
    event.preventDefault();
  }

  @HostListener('document:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (!this.resizing) return;
    const diff = this.startX - event.clientX;
    this.panelWidth = this.startWidth + diff;
    if (this.panelWidth < 150) this.panelWidth = 150;
  }

  @HostListener('document:mouseup', ['$event'])
  onMouseUp() {
    this.resizing = false;
  }
}