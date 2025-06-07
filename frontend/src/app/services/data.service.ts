// src/app/services/data.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private datamodelUrl = 'http://localhost:8000/api/datamodels';
  private columnsUrl = 'http://localhost:8000/api/columns';
  private baseUrl = 'http://localhost:8000/api'; // Ensure consistent API base
  
  // Cache storage
  private cache: { [key: string]: Observable<any> } = {};

  constructor(private http: HttpClient) {}

  getDatamodels(): Observable<any> {
    const cacheKey = 'datamodels';
    if (!this.cache[cacheKey]) {
      this.cache[cacheKey] = this.http.get<any>(this.datamodelUrl)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  getColumns(): Observable<any> {
    return this.http.get<any>(this.columnsUrl);
  }

  getColumnsByDataModel(datamodel_name: string, page = 0, pageSize = 100): Observable<any> {
    const cacheKey = `columns_${datamodel_name}_${page}_${pageSize}`;
    if (!this.cache[cacheKey]) {
      let params = new HttpParams()
        .set('page', page.toString())
        .set('pageSize', pageSize.toString());
      
      const url = `${this.columnsUrl}/${datamodel_name}`;
      this.cache[cacheKey] = this.http.get<any>(url, { params })
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  getColumnLineage(column_name: string): Observable<any> {
    const url = `${this.baseUrl}/column/lineage/${column_name}`;
    return this.http.get<any>(url);
  }

  getDatamodelById(datamodelId: string): Observable<any> {
    return this.getObjectByName(datamodelId);
  }

  /**
   * Get all objects (data models and stored procedures)
   */
  getAllObjects(): Observable<any> {
    const cacheKey = 'all_objects';
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/objects`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }
  
  /**
   * Get a specific object by name (data model or stored procedure)
   */
  getObjectByName(name: string): Observable<any> {
    const cacheKey = `object_${name}`;
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/objects/${name}`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }
  
  /**
   * Get the lineage of a specific object (data model or stored procedure)
   */
  getObjectLineage(name: string): Observable<any> {
    const cacheKey = `object_lineage_${name}`;
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/object/lineage/${name}`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  /**
   * Get only the edges for the lineage of a specific object
   */
  getObjectLineageEdges(name: string): Observable<any> {
    const cacheKey = `object_lineage_edges_${name}`;
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/object/lineage/edges/${name}`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  /**
   * Get only the upstream edges for the lineage of a specific object
   */
  getObjectLineageUpstreamEdges(name: string): Observable<any> {
    const cacheKey = `object_lineage_upstream_edges_${name}`;
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/object/lineage/edges/upstream/${name}`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  /**
   * Get only the downstream edges for the lineage of a specific object
   */
  getObjectLineageDownstreamEdges(name: string): Observable<any> {
    const cacheKey = `object_lineage_downstream_edges_${name}`;
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/object/lineage/edges/downstream/${name}`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }
  
  /**
   * Fetch lineage for a specific datamodel (uses unified object API)
   */
  getDatamodelLineage(datamodel_name: string): Observable<any> {
    return this.getObjectLineage(datamodel_name);
  }

  /**
   * Fetch all stored procedures (using unified object API)
   */
  getStoredProcedures(): Observable<any> {
    // Use the getAllObjects method and filter for stored procedures
    return this.getAllObjects().pipe(
      map(response => {
        if (response && response.elements) {
          // Filter for only stored procedure nodes
          const storedProcedureNodes = response.elements.filter((element: any) => {
            return element.group === 'nodes' && (
              element.data.node_type === 'StoredProcedure' ||
              element.data.nodeType === 'stored_procedure' ||
              element.data.type === 'stored_procedure'
            );
          });
          
          // Get all edges connected to stored procedure nodes
          const nodeIds = new Set(storedProcedureNodes.map((node: any) => node.data.id));
          const relevantEdges = response.elements.filter((element: any) => {
            return element.group === 'edges' && (
              nodeIds.has(element.data.source) || nodeIds.has(element.data.target)
            );
          });
          
          // Return filtered elements
          response.elements = [...storedProcedureNodes, ...relevantEdges];
        }
        return response;
      })
    );
  }
  
  /**
   * Fetch a specific stored procedure by name (uses unified object API)
   */
  getStoredProcedureByName(name: string): Observable<any> {
    return this.getObjectByName(name);
  }
  
  /**
   * Fetch the lineage of a stored procedure (uses unified object API)
   */
  getStoredProcedureLineage(name: string): Observable<any> {
    return this.getObjectLineage(name);
  }

  /**
   * Fetch external models
   */
  getExternalModels(): Observable<any> {
    const cacheKey = 'external_models';
    if (!this.cache[cacheKey]) {
      const url = `${this.baseUrl}/external_model`;
      this.cache[cacheKey] = this.http.get<any>(url)
        .pipe(shareReplay(1));
    }
    return this.cache[cacheKey];
  }

  mapElements(response: any, highlightedNodeName?: string) {
    // Check if response or elements is undefined
    if (!response || !response.elements) {
      console.error('Invalid response format:', response);
      return [];
    }
    
    // Check if we need to highlight edges based on current route and node highlighting
    const currentRoute = window.location.pathname;
    const isGlobalView = currentRoute.indexOf('/global-lineage') !== -1;
    const shouldHighlightEdges = highlightedNodeName && isGlobalView;
    
    // Throttle rendering for large datasets
    const elements = response.elements.map((element: any) => {
      if (element.group === 'nodes') {
        // Set default selection state
        element.data.isSelected = false;
        
        // Set nodeType for stored procedures - check multiple possible fields
        if (element.data.type === 'stored_procedure' || 
            element.data.node_type === 'StoredProcedure' ||
            element.data.labels?.includes('StoredProcedure')) {

          element.data.nodeType = 'stored_procedure';
          
          // Ensure the node has all required fields for rendering
          if (!element.data.id && element.data.name) {
            element.data.id = element.data.name;
          }
        }
        

      }
      
      // Process edges for stored procedures
      if (element.group === 'edges') {
        // Check for reads-from relationships
        if (element.data.relationship === 'reads_from') {
          element.classes = 'reads-from';
          // Keep original direction for writes_to edges
        }
        // Check for writes-to relationships
        else if (element.data.relationship === 'writes_to') {
          element.classes = 'writes-to';
          // Keep original direction for writes_to edges
          let tempSource = element.data.source;
          element.data.source = element.data.target;
          element.data.target = tempSource;
        }
        
        // If we're highlighting a specific node's lineage, apply opacity
        if (shouldHighlightEdges) {
          // If the edge is connected to the highlighted node, make it visible
          if (element.data.source === highlightedNodeName || element.data.target === highlightedNodeName) {
            element.data.opacity = 1;
            element.data.highlighted = true;
          } else {
            // Otherwise, reduce the opacity
            element.data.opacity = 0.1;
            element.data.highlighted = false;
          }
        }
      }
      
      return element;
    });
    
    const nodes = elements.filter((el: any) => el.group === 'nodes');
    const edges = elements.filter((el: any) => el.group === 'edges');
    // Create a set of node IDs for quick lookup
    const nodeIds = new Set(nodes.map((node: any) => node.data.id));
    
    // Filter out edges where either source or target node doesn't exist in the graph
    const validEdges = elements.filter((el: any) => {
      if (el.group !== 'edges') return true;
      const sourceExists = nodeIds.has(el.data.source);
      const targetExists = nodeIds.has(el.data.target);
      
      if (!sourceExists || !targetExists) {

        return false;
      }
      return true;
    });
    
    // Reassemble the elements with only valid edges
    const finalElements = [...nodes, ...validEdges.filter((el: any) => el.group === 'edges')];
    

    
    // Return in batches of max 500 nodes for better performance
    if (finalElements.length > 500) {
      const batchNodes = nodes.slice(0, 500);
      // Create a set of node IDs in this batch for filtering edges
      const batchNodeIds = new Set(batchNodes.map((node: any) => node.data.id));
      
      // Only include edges where both source and target are in the batch
      const batchEdges = validEdges.filter((el: any) => {
        if (el.group !== 'edges') return false;
        return batchNodeIds.has(el.data.source) && batchNodeIds.has(el.data.target);
      }).slice(0, 1000);
      
      return [...batchNodes, ...batchEdges];
    }
    
    return finalElements;
  }
  
  // Clear a specific cache entry
  clearCache(key: string): void {
    if (this.cache[key]) {
      delete this.cache[key];
    }
  }
  
  // Clear entire cache
  clearAllCache(): void {
    this.cache = {};
  }

}