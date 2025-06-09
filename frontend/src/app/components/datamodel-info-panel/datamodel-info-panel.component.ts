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
  objectType: string = 'unknown';
  headerColorClass: string = 'unknown-header';
  showToast: boolean = false;
  toastMessage: string = '';
  ingestionData: { ID: string, LoadTime: string, IsSuccess: boolean } | null = null;
  columns: { name: string, type: string, column_id: string, is_type_guessed: boolean, is_type_updated: boolean }[] = [];
  filteredColumnsCache: { name: string, type: string, column_id: string, is_type_guessed: boolean, is_type_updated: boolean }[] = [];
  isOpen = false;
  highlightedColumnId: string | null = null;
  searchQuery: string = '';
  panelWidth: number = 300;
  activeTab: string = 'columns';
  dataTests: any[] = [];
  expandedTestRun: string | null = null;
  historyItems: { timestamp: string, type: string, user: string, description: string }[] = [];
  
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
      .pipe(filter(event => event instanceof NavigationEnd));
  }

  fetchDatamodelData(objectId: string) {
    // Clear previous data
    this.dataTests = [];
    this.expandedTestRun = null;
    this.historyItems = [];
    this.columns = [];
    this.filteredColumnsCache = [];
    
    // Track data loading completion
    let objectDataLoaded = false;
    let columnsLoaded = false;
    let dataTestsLoaded = false;
    let historyLoaded = false;
    
    // Function to check if all data is loaded and select the appropriate tab
    const checkAllDataLoaded = () => {
      if (objectDataLoaded && columnsLoaded && dataTestsLoaded && historyLoaded) {
        // Select the first available tab
        const firstAvailableTab = this.getFirstAvailableTab();
        if (firstAvailableTab) {
          this.activeTab = firstAvailableTab;
        }
        this.cdr.markForCheck();
      }
    };
    
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
        

        // Extract object type and add appropriate icon
        let displayType = '';
        let iconHtml = '';
        
        // Check for stored procedures to override the nodeType
        if (data_result.type === 'StoredProcedure') {
          displayType = 'Stored Procedure';
          iconHtml = '<i class="fas fa-cog"></i>';
          this.headerColorClass = 'stored-procedure-header';
        } else if (data_result.type === 'table') {
          displayType = 'Table';
          iconHtml = '<i class="fas fa-table"></i>';
          this.headerColorClass = 'table-header';
        } else if (data_result.type === 'view') {
          // For view, check the node_type to determine color
          displayType = 'View';
          iconHtml = '<i class="fas fa-eye"></i>';
          
          if (data_result.node_type === 'LEAF') {
            this.headerColorClass = 'view-leaf-header';
          } else {
            // Default to NORMAL for views if not specified as LEAF
            this.headerColorClass = 'view-normal-header';
          }
        } else {
          // Unknown types get the question mark
          displayType = data_result.type || 'Unknown';
          iconHtml = '<i class="fas fa-question"></i>';
          this.headerColorClass = 'unknown-header';
        }
        
        this.objectType = iconHtml + ' ' + displayType;
        
        // Mark object data as loaded
        objectDataLoaded = true;
        
        // Fetch ingestion data for this object
        this.fetchIngestionData(this.objectId);
        
        this.cdr.markForCheck();
      } else {
        console.error('Invalid object data format:', data);
        objectDataLoaded = true;
      }
      
      checkAllDataLoaded();
    });
    
    // Fetch columns data
    this.dataService.getColumnsByDataModel(objectId).subscribe(
      (data) => {
        this.columns = data.elements.map((column: any) => ({
          name: column.data.original_name || column.data.name || column.data.id,
          type: column.data.type || 'null',
          column_id: column.data.id,
          is_type_guessed: column.data.is_type_guessed || false,
          is_type_updated: column.data.is_type_updated || false
        }));
        this.updateFilteredColumns();
        columnsLoaded = true;
        this.cdr.markForCheck();
        checkAllDataLoaded();
      },
      (error) => {
        console.error('Error fetching columns:', error);
        columnsLoaded = true;
        checkAllDataLoaded();
      }
    );
    
    // Fetch data tests
    this.dataService.getHistoricalDataTests(objectId).subscribe(
      (data) => {
        this.dataTests = data;
        // Sort data tests by TestTime (newest first) if needed
        if (this.dataTests && this.dataTests.length > 1) {
          this.dataTests.sort((a, b) => new Date(b.TestTime).getTime() - new Date(a.TestTime).getTime());
        }
        dataTestsLoaded = true;
        this.cdr.markForCheck();
        checkAllDataLoaded();
      },
      (error) => {
        console.error('Error fetching data tests:', error);
        this.dataTests = [];
        dataTestsLoaded = true;
        checkAllDataLoaded();
      }
    );
    
    // Fetch history data
    this.dataService.getHistoricalIngestionsById(objectId).subscribe(
      (data) => {
        // Transform the ingestion data into the format expected by the UI
        this.historyItems = data.map((item: any) => ({
          timestamp: item.LoadTime,
          type: item.IsSuccess ? 'success' : 'failure'
        }));
        historyLoaded = true;
        this.cdr.markForCheck();
        checkAllDataLoaded();
      },
      (error) => {
        console.error('Error fetching historical ingestions:', error);
        this.historyItems = [];
        historyLoaded = true;
        checkAllDataLoaded();
      }
    );
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
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { show_info: null },
      queryParamsHandling: 'merge'
    });
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
  
  /**
   * Fetch ingestion data for the current object
   */
  fetchIngestionData(objectId: string) {
    this.dataService.getIngestionById(objectId).subscribe(
      (data) => {
        this.ingestionData = data;
        this.cdr.markForCheck();
      },
      (error) => {
        console.error('Error fetching ingestion data:', error);
        this.ingestionData = null;
        this.cdr.markForCheck();
      }
    );
  }
  
  /**
   * Format the date string for display in YYYY-MM-DD HH:MM format (24-hour clock)
   */
  formatDate(dateString: string): string {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      // Format as YYYY-MM-DD HH:MM (24-hour clock)
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    } catch (e) {
      return dateString;
    }
  }
  
  getSuccessfulTestCount(tests: any[]): number {
    if (!tests || !Array.isArray(tests)) return 0;
    return tests.filter(test => test.IsSuccess).length;
  }
  
  /**
   * Check if the latest data test run has failed
   */
  hasLatestTestFailed(): boolean {
    if (!this.dataTests || this.dataTests.length === 0) return false;
    
    // The data tests are assumed to be sorted by TestTime (newest first)
    // If not, we would need to sort them: this.dataTests.sort((a, b) => new Date(b.TestTime).getTime() - new Date(a.TestTime).getTime());
    
    // Check if the first (latest) test run has IsSuccess = false
    return !this.dataTests[0].IsSuccess;
  }
  
  /**
   * Check if the latest history item has failed
   */
  hasLatestHistoryFailed(): boolean {
    if (!this.historyItems || this.historyItems.length === 0) return false;
    
    // Check if the first (latest) history item has type = 'failure'
    return this.historyItems[0].type === 'failure';
  }

  /**
   * Check if any tabs have data available
   */
  hasAvailableTabs(): boolean {
    return (this.columns && this.columns.length > 0) || 
           (this.dataTests && this.dataTests.length > 0) || 
           (this.historyItems && this.historyItems.length > 0);
  }

  /**
   * Find the first available tab with data
   */
  getFirstAvailableTab(): string | null {
    if (this.columns && this.columns.length > 0) return 'columns';
    if (this.dataTests && this.dataTests.length > 0) return 'data-tests';
    if (this.historyItems && this.historyItems.length > 0) return 'history';
    return null;
  }

  /**
   * Set the active tab if it has data available
   */
  setActiveTab(tabName: string) {
    // Check if the requested tab has data
    let tabHasData = false;
    
    if (tabName === 'columns' && this.columns && this.columns.length > 0) {
      tabHasData = true;
    } else if (tabName === 'data-tests' && this.dataTests && this.dataTests.length > 0) {
      tabHasData = true;
    } else if (tabName === 'history' && this.historyItems && this.historyItems.length > 0) {
      tabHasData = true;
    }
    
    // Only set the active tab if it has data
    if (tabHasData) {
      this.activeTab = tabName;
    } else {
      // Try to select another tab with data
      const availableTab = this.getFirstAvailableTab();
      if (availableTab) {
        this.activeTab = availableTab;
      }
    }
    
    this.cdr.markForCheck();
  }

  /**
   * Fetch data tests for the current object
   */
  fetchDataTests(objectId: string) {
    this.dataService.getHistoricalDataTests(objectId).subscribe(
      (data) => {
        this.dataTests = data;
        // Sort data tests by TestTime (newest first) if needed
        if (this.dataTests && this.dataTests.length > 1) {
          this.dataTests.sort((a, b) => new Date(b.TestTime).getTime() - new Date(a.TestTime).getTime());
        }
        this.cdr.markForCheck();
      },
      (error) => {
        console.error('Error fetching data tests:', error);
        this.dataTests = [];
        this.cdr.markForCheck();
      }
    );
  }
  
  /**
   * Toggle the expanded state of a test run
   */
  toggleTestRun(testTime: string) {
    if (this.expandedTestRun === testTime) {
      this.expandedTestRun = null; // Collapse if already expanded
    } else {
      this.expandedTestRun = testTime; // Expand this test run
    }
    this.cdr.markForCheck();
  }
  
  /**
   * Fetch historical ingestion data for the current object
   */
  fetchHistory(objectId: string) {
    this.dataService.getHistoricalIngestionsById(objectId).subscribe(
      (data) => {
        // Transform the ingestion data into the format expected by the UI
        this.historyItems = data.map((item: any) => ({
          timestamp: item.LoadTime,
          type: item.IsSuccess ? 'success' : 'failure'
        }));
        this.cdr.markForCheck();
      },
      (error) => {
        console.error('Error fetching historical ingestions:', error);
        this.historyItems = [];
        this.cdr.markForCheck();
      }
    );
  }
}