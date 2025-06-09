import cytoscape from 'cytoscape';
// Import from shared utility - initialization happens in this file
import '../../../app/utils/cytoscape-extensions';

export function defineNodeHtmlNode(cy: cytoscape.Core) {
    const labelConfig = {
      query: 'node',
      cssClass: 'cy-title',
      halign: "center",
      valign: "center",
      valignBox: "center",
      halignBox: "center",
      
      // @ts-ignore
      tpl: (data: any) => {
        
        // Simplified template for large graphs
        const selectedClass = data.isSelected ? 'selected' : '';
        
        let nodeType = data.node_type || '';
        let displayType = '';
        let iconHtml = '';
    
        if (data.type === 'StoredProcedure') {
          nodeType = 'stored_procedure';
          displayType = 'SP';
          iconHtml = '<i class="fas fa-cog"></i>';
        } else if (data.type === 'table') {
          nodeType = 'table';
          displayType = 'TBL';
          iconHtml = '<i class="fas fa-table"></i>';
        } else if (data.type === 'view') {
          displayType = 'VIW';
          iconHtml = '<i class="fas fa-eye"></i>';
        } else {
          displayType = 'UNK';
          iconHtml = '<i class="fas fa-question"></i>';
        }
  
        
        // Extract warehouse and schema information - check multiple potential data sources
        let objectName = data.object;
        let schemaName = data.schema;
        let warehouseName = data.warehouse;
        
        // New node layout with colored sidebar using nodeType for color (ROOT, LEAF, NORMAL, stored_procedure)
        return `
          <div class="node-container ${selectedClass} ${nodeType}" data-id="${data.id || data.name}">
            <div class="node-sidebar ${nodeType}">
              ${iconHtml}
              <div class="node-type-label">${displayType}</div>
            </div>
            <div class="node-content">
              <div class="node-metadata">
                <div class="warehouse-name">${warehouseName || '---'}</div>
                <div class="schema-name">${schemaName || '---'}</div>
              </div>
              <div class="header">${objectName}</div>
            </div>
          </div>
        `;
      }
    };
    
    // @ts-ignore
    cy.nodeHtmlLabel([labelConfig]);    
  }