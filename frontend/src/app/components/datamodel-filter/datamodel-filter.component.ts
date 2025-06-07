import { Component, OnInit, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../../services/data.service';
import { Router, ActivatedRoute } from '@angular/router';

type FilterType = 'id' | 'schema' | 'warehouse' | 'object';

interface Filter {
  type: FilterType;
  label: string;
  isOpen: boolean;
  selected: string[];
  available: string[];
  searchTerm: string;
}

@Component({
  selector: 'app-datamodel-filter',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './datamodel-filter.component.html',
  styleUrl: './datamodel-filter.component.scss'
})
export class DatamodelFilterComponent implements OnInit {
  filters: Filter[] = [];
  activeFilters: Filter[] = [];
  showFilterOptions: boolean = false;
  filterDropdownPosition: { left: number; top: number } | null = null;
  availableFilterTypes: { type: FilterType, label: string }[] = [
    //{ type: 'id', label: 'ID' },
    { type: 'schema', label: 'Schema' },
    { type: 'warehouse', label: 'Warehouse' },
    { type: 'object', label: 'Object' }
  ];

  constructor(
    private dataService: DataService, 
    private router: Router, 
    private route: ActivatedRoute,
    private elementRef: ElementRef
  ) {}

  ngOnInit() {
    // Load existing filter values from query params if any
    this.route.queryParams.subscribe(params => {
      // Implementation for loading filters from query params if needed
    });

    // Initialize available values for each filter type
    this.loadFilterOptions();
  }

  loadFilterOptions() {
    this.dataService.getAllObjects().subscribe(response => {
      const elements = response.elements || [];
      const nodes = elements
        .filter((el: any) => el.group === 'nodes' && el.data);

      // Extract unique values for each filter type
      //const ids = new Set<string>();
      const schemas = new Set<string>();
      const warehouses = new Set<string>();
      const objects = new Set<string>();

      nodes.forEach((node: any) => {
        //if (node.data.id) ids.add(node.data.id);
        if (node.data.schema) schemas.add(node.data.schema);
        if (node.data.warehouse) warehouses.add(node.data.warehouse);
        if (node.data.object) objects.add(node.data.object);
      });

      // Populate available filter options
      this.availableFilterTypes.forEach(filterType => {
        let availableValues: string[] = [];
        switch (filterType.type) {
          //case 'id':
            //availableValues = Array.from(ids);
            //break;
          case 'schema':
            availableValues = Array.from(schemas);
            break;
          case 'warehouse':
            availableValues = Array.from(warehouses);
            break;
          case 'object':
            availableValues = Array.from(objects);
            break;
        }

        // Create the filter if not already created
        if (!this.filters.some(f => f.type === filterType.type)) {
          this.filters.push({
            type: filterType.type,
            label: filterType.label,
            isOpen: false,
            selected: [],
            available: availableValues.sort(),
            searchTerm: ''
          });
        } else {
          // Update available values for existing filter
          const existingFilter = this.filters.find(f => f.type === filterType.type);
          if (existingFilter) {
            existingFilter.available = availableValues.sort();
          }
        }
      });
    });
  }

  toggleFilterOptions(event?: MouseEvent) {
    if (event) {
      event.stopPropagation();
      
      // Get the position of the element that was clicked
      const target = event.currentTarget as HTMLElement;
      const rect = target.getBoundingClientRect();
      
      // Calculate position for the dropdown
      this.filterDropdownPosition = {
        left: rect.left,
        top: rect.bottom + window.scrollY
      };
    }
    
    this.showFilterOptions = !this.showFilterOptions;
    // Close any open filter dropdown when showing/hiding filter type selection
    this.filters.forEach(filter => filter.isOpen = false);
  }

  addFilter(filterType: FilterType) {
    const filter = this.filters.find(f => f.type === filterType);
    if (filter && !this.activeFilters.includes(filter)) {
      this.activeFilters.push(filter);
      this.showFilterOptions = false;
    }
  }

  removeFilter(filter: Filter) {
    const index = this.activeFilters.indexOf(filter);
    if (index !== -1) {
      filter.selected = [];
      filter.searchTerm = '';
      this.activeFilters.splice(index, 1);
      this.updateFilters();
    }
  }

  toggleFilter(filter: Filter) {
    // Close all other filters first
    this.filters.forEach(f => {
      if (f !== filter) f.isOpen = false;
    });
    filter.isOpen = !filter.isOpen;
  }

  toggleOption(filter: Filter, option: string) {
    const index = filter.selected.indexOf(option);
    if (index === -1) {
      filter.selected.push(option);
    } else {
      filter.selected.splice(index, 1);
    }
    this.updateFilters();
  }

  toggleSelectAll(filter: Filter) {
    const filteredOptions = this.getFilteredOptions(filter);
    
    // If all filtered options are selected, deselect them all
    if (filteredOptions.every(option => filter.selected.includes(option))) {
      filter.selected = filter.selected.filter(item => !filteredOptions.includes(item));
    } else {
      // Select all filtered options that aren't already selected
      filteredOptions.forEach(option => {
        if (!filter.selected.includes(option)) {
          filter.selected.push(option);
        }
      });
    }
    this.updateFilters();
  }

  isOptionSelected(filter: Filter, option: string): boolean {
    return filter.selected.includes(option);
  }

  isAllSelected(filter: Filter): boolean {
    const filteredOptions = this.getFilteredOptions(filter);
    return filteredOptions.length > 0 && filteredOptions.every(option => filter.selected.includes(option));
  }

  updateFilters() {
    // Create query params from filters
    const queryParams: any = {};
    
    this.activeFilters.forEach(filter => {
      if (filter.selected.length > 0) {
        queryParams[`filter_${filter.type}`] = filter.selected.join(',');
      }
    });

    // Update URL with filter params
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      queryParamsHandling: 'merge'
    });
  }

  getFilteredOptions(filter: Filter): string[] {
    if (!filter.searchTerm) return filter.available;
    
    return filter.available.filter(option => 
      option.toLowerCase().includes(filter.searchTerm.toLowerCase())
    );
  }
  
  // Get filter types that aren't already active
  getAvailableFilterTypes(): { type: FilterType, label: string }[] {
    // Get all filter types that are already active
    const activeTypes = this.activeFilters.map(filter => filter.type);
    
    // Return only filter types that aren't already active
    return this.availableFilterTypes.filter(filterType => 
      !activeTypes.includes(filterType.type)
    );
  }
  
  // Close dropdowns only when clicking outside the component or on non-dropdown elements
  @HostListener('document:click', ['$event'])
  handleDocumentClick(event: MouseEvent) {
    // Get the target element
    const target = event.target as HTMLElement;
    
    // Check if click occurred inside filter dropdown
    const clickedInFilterDropdown = this.elementContainsClass(target, 'filter-dropdown');
    
    // Check if click occurred inside filter type dropdown
    const clickedInFilterTypeDropdown = this.elementContainsClass(target, 'filter-type-dropdown');
    
    // Check if click was on a filter pill
    const clickedOnFilterPill = this.elementContainsClass(target, 'filter-pill');
    
    // Check if click was on the add filter button
    const clickedOnAddFilter = this.elementContainsClass(target, 'add-filter');
    
    // Only close dropdowns if click was outside of any dropdown, pill or add filter button
    if (!clickedInFilterDropdown && !clickedInFilterTypeDropdown && !clickedOnFilterPill && !clickedOnAddFilter) {
      // Close all open dropdowns
      this.filters.forEach(filter => filter.isOpen = false);
      this.showFilterOptions = false;
    }
  }
  
  // Helper method to check if element or any parent has a specific class
  private elementContainsClass(element: HTMLElement | null, className: string): boolean {
    let current = element;
    while (current) {
      if (current.classList && current.classList.contains(className)) {
        return true;
      }
      current = current.parentElement;
    }
    return false;
  }
}
