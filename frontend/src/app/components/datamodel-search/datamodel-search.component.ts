import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../../services/data.service';
import { Router, ActivatedRoute } from '@angular/router';

interface SearchResult {
  id: string;
  name: string;
  warehouse?: string;
  schema?: string;
  object?: string;
  type?: string;
  tags?: string[];
  original_name?: string;
}

@Component({
  selector: 'app-datamodel-search',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './datamodel-search.component.html',
  styleUrls: ['./datamodel-search.component.scss']
})
export class DatamodelSearchComponent {
  searchResults: SearchResult[] = [];
  searchTerm: string = '';
  hasSelection: boolean = false;
  selectedIndex: number = -1;
  private blurTimeoutId: any = null;

  constructor(private dataService: DataService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit() {}

  onSearch(event: any) {
    this.searchTerm = event.target.value.trim().toLowerCase();
    this.hasSelection = false;
    this.selectedIndex = -1; // Reset selection when search changes
    if (this.searchTerm.length > 1) { // Require at least 2 characters to search
      this.dataService.getAllObjects().subscribe(response => {
        const elements = response.elements || [];
        const dataItems = elements
          .filter((el: any) => el.group === 'nodes' && el.data) // Only process node elements with data
          .map((element: any) => ({
            ...element.data
          }));
        this.searchResults = this.filterResults(dataItems);
      });
    } else {
      this.searchResults = [];
    }
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.searchResults = [];
    this.hasSelection = false;
    this.selectedIndex = -1;
  }

  onKeyDown(event: KeyboardEvent): void {
    if (!this.searchResults.length) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.selectedIndex = (this.selectedIndex + 1) % this.searchResults.length;
        this.scrollToSelected();
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.selectedIndex = this.selectedIndex <= 0 ? this.searchResults.length - 1 : this.selectedIndex - 1;
        this.scrollToSelected();
        break;
      case 'Enter':
        if (this.selectedIndex >= 0 && this.selectedIndex < this.searchResults.length) {
          event.preventDefault();
          this.selectResult(this.searchResults[this.selectedIndex]);
        }
        break;
    }
  }

  private scrollToSelected(): void {
    const selectedElement = document.querySelector('.result-item.selected');
    selectedElement?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  filterResults(data: SearchResult[]): SearchResult[] {
    if (!this.searchTerm) return [];
    
    return data.filter(item => {
      // Check if search term matches any of these fields
      const searchFields = [
        item.name?.toLowerCase(),
        item.id?.toLowerCase(),
        item.warehouse?.toLowerCase(),
        item.schema?.toLowerCase(),
        item.object?.toLowerCase(),
        item.original_name?.toLowerCase(),
        ...(item.tags || []).map((t: string) => t?.toLowerCase())
      ].filter((field): field is string => typeof field === 'string');
      
      // Check if search term is included in any of the fields
      return searchFields.some(field => field.includes(this.searchTerm));
    });
  }

  highlight(text: string | undefined, search: string): string {
    if (!text) {
      return '';
    }
    if (!search) {
      return text;
    }
    return text.replace(new RegExp(search, 'gi'), match => {
      return `<span class="highlight">${match}</span>`;
    });
  }

  /**
   * Handle selection of a search result: autofill input and update query params
   */
  selectResult(result: any): void {
    this.searchTerm = result.name || result.id;
    this.hasSelection = true;
    this.searchResults = [];
    this.selectedIndex = -1;
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { object_id: result.id, show_info: 'true' },
      queryParamsHandling: 'merge'
    });
  }

  isSelected(index: number): boolean {
    return this.selectedIndex === index;
  }
  
  /**
   * Hide search results dropdown when input loses focus
   * Uses a small delay to allow clicking on results
   */
  hideResultsDelayed(): void {
    // Clear any existing timeout
    if (this.blurTimeoutId !== null) {
      clearTimeout(this.blurTimeoutId);
    }
    
    // Set a small timeout to allow clicking on results
    this.blurTimeoutId = setTimeout(() => {
      this.searchResults = [];
      this.selectedIndex = -1;
    }, 150); // 150ms delay gives enough time to click a result
  }
}