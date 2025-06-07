import { Component, OnInit } from '@angular/core';
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
  availableFilterTypes: { type: FilterType, label: string }[] = [
    { type: 'id', label: 'ID' },
    { type: 'schema', label: 'Schema' },
    { type: 'warehouse', label: 'Warehouse' },
    { type: 'object', label: 'Object' }
  ];

  constructor(private dataService: DataService, private router: Router, private route: ActivatedRoute) {}

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
      const ids = new Set<string>();
      const schemas = new Set<string>();
      const warehouses = new Set<string>();
      const objects = new Set<string>();

      nodes.forEach((node: any) => {
        if (node.data.id) ids.add(node.data.id);
        if (node.data.schema) schemas.add(node.data.schema);
        if (node.data.warehouse) warehouses.add(node.data.warehouse);
        if (node.data.object) objects.add(node.data.object);
      });

      // Populate available filter options
      this.availableFilterTypes.forEach(filterType => {
        let availableValues: string[] = [];
        switch (filterType.type) {
          case 'id':
            availableValues = Array.from(ids);
            break;
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

  toggleFilterOptions() {
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
    if (filter.selected.length === filter.available.length) {
      filter.selected = [];
    } else {
      filter.selected = [...filter.available];
    }
    this.updateFilters();
  }

  isOptionSelected(filter: Filter, option: string): boolean {
    return filter.selected.includes(option);
  }

  isAllSelected(filter: Filter): boolean {
    return filter.selected.length === filter.available.length;
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
}
